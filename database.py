import sqlite3
import logging

DB_NAME = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            current_mode TEXT DEFAULT 'none',
            last_score REAL DEFAULT 0.0,
            total_tasks INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_text TEXT,
            ai_feedback TEXT,
            score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def update_user_info(user_id, username, full_name, mode=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                   (user_id, username, full_name))
    if mode:
        cursor.execute('UPDATE users SET current_mode = ? WHERE user_id = ?', (mode, user_id))
    conn.commit()
    conn.close()

def get_user_mode(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT current_mode FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 'none'

def save_result(user_id, text, score, feedback):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_score = ?, total_tasks = total_tasks + 1 WHERE user_id = ?', (score, user_id))
    cursor.execute('INSERT INTO history (user_id, task_text, ai_feedback, score) VALUES (?, ?, ?, ?)',
                   (user_id, text, feedback, score))
    conn.commit()
    conn.close()