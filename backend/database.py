"""
SQLite database setup for Screen-U
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "screenu.db"

def get_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_connection()
    cursor = conn.cursor()

    # Roles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            department TEXT,
            description TEXT,
            scoring_config TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            role_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            analysis TEXT NOT NULL,
            score TEXT NOT NULL,
            status TEXT NOT NULL,
            recruiter_summary TEXT,
            interview_questions TEXT,
            rejection_feedback TEXT,
            interview_profile TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    """)

    # Interview ratings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT NOT NULL,
            competency TEXT NOT NULL,
            question_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        )
    """)

    conn.commit()
    conn.close()

def dict_from_row(row):
    """Convert sqlite3.Row to dict"""
    if row is None:
        return None
    return dict(row)

def list_from_rows(rows):
    """Convert list of sqlite3.Row to list of dicts"""
    return [dict(row) for row in rows]
