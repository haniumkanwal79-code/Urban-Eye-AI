
import sqlite3

DB_NAME = "issues.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_table():

    conn = get_connection()
    c = conn.cursor()

    # ================= ISSUES TABLE =================
    c.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            image_path TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ================= USERS TABLE =================
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()
