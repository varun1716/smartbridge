import sqlite3
import json
import os
from datetime import datetime

DATABASE_NAME = os.path.join(os.path.dirname(__file__), "networking_assistant.db")

def get_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_description TEXT NOT NULL,
            interests TEXT NOT NULL,
            extracted_themes TEXT NOT NULL,
            conversation_starters TEXT NOT NULL,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_interaction(event_description: str, interests: list, extracted_themes: list, conversation_starters: list) -> int:
    """Saves a networking interaction to the database and returns the generated ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (event_description, interests, extracted_themes, conversation_starters)
        VALUES (?, ?, ?, ?)
    """, (
        event_description,
        json.dumps(interests),
        json.dumps(extracted_themes),
        json.dumps(conversation_starters)
    ))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def update_feedback(interaction_id: int, feedback: str) -> bool:
    """Updates the feedback (e.g., 'thumbs_up', 'thumbs_down', or None) for a given interaction ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE history
        SET feedback = ?
        WHERE id = ?
    """, (feedback, interaction_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def get_history() -> list:
    """Retrieves all past interactions, sorted by timestamp descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    history_items = []
    for row in rows:
        try:
            interests = json.loads(row["interests"])
        except Exception:
            interests = [row["interests"]]
            
        try:
            extracted_themes = json.loads(row["extracted_themes"])
        except Exception:
            extracted_themes = []
            
        try:
            conversation_starters = json.loads(row["conversation_starters"])
        except Exception:
            conversation_starters = []
            
        history_items.append({
            "id": row["id"],
            "event_description": row["event_description"],
            "interests": interests,
            "extracted_themes": extracted_themes,
            "conversation_starters": conversation_starters,
            "feedback": row["feedback"],
            "timestamp": row["timestamp"]
        })
    return history_items

# Initialize database schema immediately when imported/loaded
init_db()
