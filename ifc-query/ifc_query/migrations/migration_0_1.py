import sqlite3
from ifc_query import db
from logging import log, INFO

def migrate():
    """
    Initial migration that creates the schema_version table to track database versions.
    Migrates from version 0 (no version table) to version 1.
    """
    connection = sqlite3.connect(db.DB_PATH)
    cursor = connection.cursor()

    # Create the schema_version table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert initial version (1)
    cursor.execute('INSERT INTO schema_version (version) VALUES (?)', (1,))

    connection.commit()
    connection.close()
    log(INFO, "Applied migration 0 -> 1")

if __name__ == '__main__':
    migrate()
