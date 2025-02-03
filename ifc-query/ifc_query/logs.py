from pathlib import Path
import sqlite3
from typing import Dict
from datetime import datetime
import os
import streamlit as st
from ifc_query.db import DB_FOLDER
import json

# Ensure data directory exists
os.makedirs(DB_FOLDER, exist_ok=True)

LOG_DB_PATH = DB_FOLDER / Path('logs.db')

def init_db():
    """Initialize the logs database if it doesn't exist."""
    conn = sqlite3.connect(LOG_DB_PATH)
    cursor = conn.cursor()
    
    # Create logs table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            timestamp TEXT,
            event TEXT,
            user TEXT,
            properties TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log(event: str, user: str, properties: Dict):
    """
    Log an event to the database.
    
    Args:
        event: The name of the event
        user: The username of the person performing the action
        properties: A dictionary of additional properties to log
    """
    init_db()
    
    timestamp = datetime.now().isoformat()
    
    conn = sqlite3.connect(LOG_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO logs (timestamp, event, user, properties) VALUES (?, ?, ?, ?)',
        (timestamp, event, user, json.dumps(properties))
    )
    
    conn.commit()
    conn.close()

def st_log(event: str, properties: Dict):
    """
    Log an event using the current Streamlit user.
    
    Args:
        event: The name of the event
        properties: A dictionary of additional properties to log
    """
    # Get username from Streamlit session state
    user = st.session_state.get('username', 'unknown')
    log(event, user, properties)
