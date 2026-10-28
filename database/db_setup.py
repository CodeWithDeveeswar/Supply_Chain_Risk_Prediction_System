"""Create or migrate the local SQLite schema without seeding a default account."""
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "database.db")


def setup_database():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT,
        email TEXT,
        password_hash TEXT,
        created_at TEXT
    )""")
    user_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)")}
    if "email" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "password_hash" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "created_at" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")

    cursor.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, supplier TEXT,
        region INTEGER, transport INTEGER, delay REAL, weather INTEGER,
        demand INTEGER, inventory INTEGER, traffic INTEGER, port_delay INTEGER,
        order_value REAL, fuel_cost REAL, risk TEXT, user_id INTEGER
    )""")
    prediction_columns = {row[1] for row in cursor.execute("PRAGMA table_info(predictions)")}
    if "user_id" not in prediction_columns:
        cursor.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER")

    # Remove the old seeded demo account, but keep its old prediction rows for
    # the first account created through the new registration page to adopt.
    cursor.execute("DELETE FROM users WHERE username = 'admin' AND password = 'admin123' AND (password_hash IS NULL OR password_hash = '')")
    for user_id, old_password, password_hash in cursor.execute(
        "SELECT id, password, password_hash FROM users"
    ).fetchall():
        if old_password and not password_hash:
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                           (generate_password_hash(old_password), user_id))

    cursor.execute("UPDATE users SET created_at = COALESCE(created_at, ?)",
                   (datetime.now().isoformat(timespec="seconds"),))
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_nocase ON users(username COLLATE NOCASE)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email COLLATE NOCASE) WHERE email IS NOT NULL AND email != ''")

    conn.commit()
    conn.close()
    print("Database setup completed successfully.")


if __name__ == "__main__":
    setup_database()
