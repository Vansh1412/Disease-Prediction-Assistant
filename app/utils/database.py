import hashlib
import json
import sqlite3
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

DB_PATH = Path("database.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@lru_cache(maxsize=1)
def init_db() -> None:
    conn = get_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    # Migrate existing DB: add is_admin column if missing
    try:
        c.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Prediction History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            disease TEXT NOT NULL,
            confidence REAL NOT NULL,
            model_used TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # User Preferences Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            user_id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'Dark',
            notifications INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Seed admin account
    _ADMIN_EMAIL    = "chopravansh1412@gmail.com"
    _ADMIN_NAME     = "Admin"
    _ADMIN_PASSWORD = "vansh@1412"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('SELECT id FROM users WHERE email = ?', (_ADMIN_EMAIL,))
    if not c.fetchone():
        c.execute(
            'INSERT INTO users (name, email, password_hash, created_at, last_login, is_admin) VALUES (?,?,?,?,?,1)',
            (_ADMIN_NAME, _ADMIN_EMAIL, hash_password(_ADMIN_PASSWORD), now, now)
        )
        admin_id = c.lastrowid
        c.execute('INSERT OR IGNORE INTO preferences (user_id) VALUES (?)', (admin_id,))
    else:
        # Ensure the existing admin account has is_admin=1 and correct password
        c.execute(
            'UPDATE users SET is_admin=1, password_hash=? WHERE email=?',
            (hash_password(_ADMIN_PASSWORD), _ADMIN_EMAIL)
        )
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name: str, email: str, password: str) -> tuple[bool, int | str]:
    conn = get_connection()
    c = conn.cursor()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO users (name, email, password_hash, created_at, last_login)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, hash_password(password), now, now))
        user_id = c.lastrowid
        c.execute('''
            INSERT INTO preferences (user_id) VALUES (?)
        ''', (user_id,))
        conn.commit()
        return True, user_id
    except sqlite3.IntegrityError:
        return False, "Email already exists"
    finally:
        conn.close()


def login_user(email: str, password: str) -> tuple[bool, dict[str, Any] | str]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, name, password_hash, is_admin FROM users WHERE email = ?
    ''', (email,))
    user = c.fetchone()
    
    if user and user[2] == hash_password(password):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('UPDATE users SET last_login = ? WHERE id = ?', (now, user[0]))
        conn.commit()
        conn.close()
        return True, {"id": user[0], "name": user[1], "email": email, "is_admin": bool(user[3])}
    
    conn.close()
    return False, "Invalid email or password"


def save_prediction(
    user_id: int,
    symptoms: list[str],
    disease: str,
    confidence: float,
    model_used: str,
) -> None:
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symptoms_str = json.dumps(symptoms) if isinstance(symptoms, list) else str(symptoms)
    c.execute('''
        INSERT INTO predictions (user_id, date, symptoms, disease, confidence, model_used)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, now, symptoms_str, disease, confidence, model_used))
    conn.commit()
    conn.close()


def get_user_predictions(user_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT date, symptoms, disease, confidence, model_used 
        FROM predictions WHERE user_id = ? ORDER BY date DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"date": r[0], "symptoms": r[1], "disease": r[2], "confidence": r[3], "model": r[4]} for r in rows]


def get_user_preferences(user_id: int) -> dict[str, Any]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT theme, notifications FROM preferences WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"theme": row[0], "notifications": bool(row[1])}
    return {"theme": "Dark", "notifications": True}


def update_preferences(user_id: int, theme: str, notifications: bool) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE preferences SET theme = ?, notifications = ? WHERE user_id = ?
    ''', (theme, int(notifications), user_id))
    conn.commit()
    conn.close()


# ── Admin-specific helpers ─────────────────────────────────────────────────

def get_all_users() -> list[dict[str, Any]]:
    """Return all users (admin use only)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, name, email, created_at, last_login, is_admin FROM users ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "email": r[2],
         "created_at": r[3], "last_login": r[4], "is_admin": bool(r[5])}
        for r in rows
    ]


def get_all_predictions() -> list[dict[str, Any]]:
    """Return all predictions across all users (admin use only)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.date, p.disease, p.confidence, p.model_used, p.symptoms, u.name
        FROM predictions p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.date DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return [
        {"date": r[0], "disease": r[1], "confidence": r[2],
         "model": r[3], "symptoms": r[4], "user_name": r[5] or "Guest"}
        for r in rows
    ]


def get_admin_stats() -> dict[str, Any]:
    """Aggregate statistics for the admin dashboard."""
    conn = get_connection()
    c = conn.cursor()
    stats: dict[str, Any] = {}

    c.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
    stats["total_patients"] = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM predictions')
    stats["total_predictions"] = c.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM predictions WHERE date LIKE ?", (f"{today}%",))
    stats["today_predictions"] = c.fetchone()[0]

    c.execute('SELECT AVG(confidence) FROM predictions')
    avg = c.fetchone()[0]
    stats["avg_confidence"] = round(avg, 1) if avg else 0.0

    c.execute('SELECT disease, COUNT(*) as cnt FROM predictions GROUP BY disease ORDER BY cnt DESC LIMIT 8')
    stats["disease_dist"] = {r[0]: r[1] for r in c.fetchall()}

    c.execute('SELECT model_used, COUNT(*) as cnt FROM predictions GROUP BY model_used')
    stats["model_usage"] = {r[0]: r[1] for r in c.fetchall()}

    conn.close()
    return stats
