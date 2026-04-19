import hashlib
from database.db import get_connection

def create_user(email, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        return cursor.lastrowid

def get_user(email):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def save_log(action, status, user_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user_id, action, status) VALUES (?, ?, ?)", (user_id, action, status))
        return cursor.lastrowid

def get_logs():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM logs ORDER BY timestamp DESC").fetchall()

def create_task(task_type, schedule):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task_type, schedule) VALUES (?, ?)", (task_type, schedule))
        return cursor.lastrowid

def get_tasks():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM tasks").fetchall()
