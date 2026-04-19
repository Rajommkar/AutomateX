import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "automatex.db")

@contextmanager
def get_connection():
    """
    Context manager that safely yields a SQLite connection.
    Automatically commits changes on success and rolls back on failure,
    then closes the connection.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """
    Initializes the database schema cleanly.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # 2. Logs Table (Upgraded with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL
            )
        ''')

        # 3. Tasks Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                schedule TEXT NOT NULL
            )
        ''')
