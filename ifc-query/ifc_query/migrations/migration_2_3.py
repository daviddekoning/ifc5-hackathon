import sqlite3
from ifc_query import db
from logging import log, INFO

def migrate():
    """
    Migration to add sessions table for secure token storage.
    Migrates from version 2 to version 3.
    """
    connection = sqlite3.connect(db.DB_PATH)
    cursor = connection.cursor()

    # Create the sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            access_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(login)
        )
    ''')

    # Create index for faster session lookups and expiry checks
    cursor.execute('''
        CREATE INDEX idx_sessions_expiry 
        ON sessions(session_id, expires_at)
    ''')

    # Update schema version to 3
    cursor.execute('INSERT INTO schema_version (version) VALUES (?)', (3,))

    connection.commit()
    connection.close()
    log(INFO, "Applied migration 2 -> 3")

if __name__ == '__main__':
    migrate() 