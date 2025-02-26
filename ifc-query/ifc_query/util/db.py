import sqlite3
import os
import importlib
import glob
from pathlib import Path
from logging import log, INFO, DEBUG, WARN, ERROR
import uuid
from datetime import datetime, timedelta
from typing import Optional
DB_FOLDER = "ifc_query/data"
DB_PATH = DB_FOLDER / Path("info.db")

def get_current_schema_version():
    """Get the current schema version from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT version FROM schema_version ORDER BY version DESC LIMIT 1')
        version = cursor.fetchone()
        return version[0] if version else 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return 0
    finally:
        conn.close()

def apply_migrations(current_version):
    """Apply all necessary migrations in order"""
    migrations_path = Path(__file__).parent / 'migrations'
    migration_files = glob.glob(str(migrations_path / 'migration_*_*.py'))
    log(INFO, f"Migrations found: {migration_files}")
    
    # Parse migration files to get from and to versions
    migrations = []
    for file in migration_files:
        filename = os.path.basename(file)
        from_ver, to_ver = map(int, filename.replace('migration_', '').replace('.py', '').split('_'))
        migrations.append((from_ver, to_ver, file))
    
    # Sort migrations by from_version
    migrations.sort(key=lambda x: x[0])
    log(INFO, f"Migrataions: {migrations}")

    n_migrations_applied = 0

    # Apply each needed migration in order
    for from_ver, to_ver, file_path in migrations:
        if from_ver >= current_version and to_ver > current_version:
            # Import and run the migration
            module_path = f"ifc_query.migrations.migration_{from_ver}_{to_ver}"
            log(INFO, f"Attempting migration {module_path}, from {os.getcwd()}")
            migration_module = importlib.import_module(module_path)
            migration_module.migrate()
            n_migrations_applied += 1

    return n_migrations_applied

def ensure_db_exists():
    """Create the database and tables if they don't exist, and apply any pending migrations"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            login TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

    # Check and apply migrations
    current_version = get_current_schema_version()
    log(INFO, f"Database schema version: {current_version}")
    n = apply_migrations(current_version)
    log(INFO, f"{n} database migrations applied.")

def add_user(login: str, name: str):
    """Add or update a user in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users (login, name)
        VALUES (?, ?)
    ''', (login, name))
    
    conn.commit()
    conn.close()

def get_user(login: str):
    """Retrieve a user from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE login = ?', (login,))
    user = cursor.fetchone()
    
    conn.close()
    return user

def store_session(user_id: str, access_token: str) -> str:
    """Store a session with an encrypted token and return a session ID"""
    session_id = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(days=30)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # TODO: Encrypt token before storage
    query = """
        INSERT INTO sessions (session_id, user_id, access_token, expires_at)
        VALUES (?, ?, ?, ?)
    """
    cursor.execute(query, (session_id, user_id, access_token, expiry))
    conn.commit()
    conn.close()
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """Retrieve and validate a session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT user_id, access_token, expires_at 
        FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """
    result = cursor.execute(query, (session_id, datetime.now())).fetchone()
    conn.close()
    
    if result:
        return {
            'user_id': result[0],
            'access_token': result[1],
            'expires_at': result[2]
        }
    return None

def delete_session(session_id: str) -> None:
    """Remove a session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "DELETE FROM sessions WHERE session_id = ?"
    cursor.execute(query, (session_id,))
    conn.commit()
    conn.close()