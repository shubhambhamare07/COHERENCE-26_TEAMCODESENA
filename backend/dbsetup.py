"""
ArthRakshak — Database Setup
Creates SQLite arthrakshak.db with schema for users, schemes, anomalies, risk_history.
Run: python db_setup.py
"""

import os
import sqlite3
import json

# Path to data folder (sibling of backend)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
DB_PATH = os.path.join(DATA_DIR, "arthrakshak.db")


def ensure_data_dir():
    """Ensure data and reports directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    reports_dir = os.path.join(DATA_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    gitkeep = os.path.join(reports_dir, ".gitkeep")
    if not os.path.exists(gitkeep):
        open(gitkeep, "a").close()


def create_db(conn):
    """Create database schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gov_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT,
            name TEXT,
            dept TEXT,
            state TEXT,
            district TEXT,
            town TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS schemes (
            id TEXT PRIMARY KEY,
            name TEXT,
            level TEXT,
            sector TEXT,
            utilization REAL,
            risk_score INTEGER,
            budget_cr REAL,
            state TEXT,
            district TEXT,
            town TEXT,
            data_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS anomalies (
            id TEXT PRIMARY KEY,
            scheme_id TEXT,
            scheme_name TEXT,
            anomaly_type TEXT,
            severity TEXT,
            detail TEXT,
            amount_cr REAL,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            resolved_by TEXT
        );

        CREATE TABLE IF NOT EXISTS risk_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheme_id TEXT,
            dept TEXT,
            score INTEGER,
            score_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_anomalies_scheme ON anomalies(scheme_id);
        CREATE INDEX IF NOT EXISTS idx_risk_history_scheme ON risk_history(scheme_id);
    """)


def seed_users(conn):
    """Seed demo users from users.json."""
    users_path = os.path.join(DATA_DIR, "users.json")
    if not os.path.exists(users_path):
        return
    with open(users_path, "r", encoding="utf-8") as f:
        users = json.load(f)
    for u in users:
        conn.execute(
            """INSERT OR REPLACE INTO users (gov_id, username, password_hash, name, dept, state, district, town)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                u.get("govId", ""),
                u.get("username", ""),
                u.get("password", ""),  # In production, use hashed password
                u.get("name", ""),
                u.get("dept", ""),
                u.get("state", ""),
                u.get("district", ""),
                u.get("town", ""),
            ),
        )


def main():
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    try:
        create_db(conn)
        seed_users(conn)
        conn.commit()
        print(f"[OK] arthrakshak.db created at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
