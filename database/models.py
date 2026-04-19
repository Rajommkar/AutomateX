from database.db import get_db_connection

class User:
    @staticmethod
    def create(email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        try:
            return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        finally:
            conn.close()

class Log:
    @staticmethod
    def create(action, status):
        # timestamp is handled by the default value CURRENT_TIMESTAMP
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO logs (action, status) VALUES (?, ?)", (action, status))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            return conn.execute("SELECT * FROM logs ORDER BY timestamp DESC").fetchall()
        finally:
            conn.close()

class Task:
    @staticmethod
    def create(task_type, schedule):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tasks (task_type, schedule) VALUES (?, ?)", (task_type, schedule))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            return conn.execute("SELECT * FROM tasks").fetchall()
        finally:
            conn.close()
