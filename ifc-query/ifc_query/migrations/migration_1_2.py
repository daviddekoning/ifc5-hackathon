import sqlite3
from ifc_query import db
from logging import log, INFO

def migrate():
    """
    Migration to add 'plan' column to users table.
    Migrates from version 1 to version 2.
    """
    connection = sqlite3.connect(db.DB_PATH)
    cursor = connection.cursor()

    # Add plan column to users table with default value 'free'
    cursor.execute('ALTER TABLE users ADD COLUMN plan TEXT NOT NULL DEFAULT "free"')

    # Update schema version to 2
    cursor.execute('INSERT INTO schema_version (version) VALUES (?)', (2,))

    connection.commit()
    connection.close()
    log(INFO, "Applied migration 1 -> 2")

if __name__ == '__main__':
    migrate()