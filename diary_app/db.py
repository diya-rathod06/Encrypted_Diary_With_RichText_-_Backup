import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "secure_diary.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            title TEXT NOT NULL,
            content BLOB NOT NULL,
            plaintext TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_entry(user, title, encrypted_content, plaintext_content, created_at, updated_at):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO entries (user, title, content, plaintext, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user, title, encrypted_content, plaintext_content, created_at, updated_at))
    conn.commit()
    conn.close()

def update_entry(entry_id, user, title, encrypted_content, plaintext_content, updated_at):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE entries
        SET title=?, content=?, plaintext=?, updated_at=?
        WHERE id=? AND user=?
    """, (title, encrypted_content, plaintext_content, updated_at, entry_id, user))
    conn.commit()
    conn.close()

def delete_entry(entry_id, user):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id=? AND user=?", (entry_id, user))
    conn.commit()
    conn.close()

def get_entries(user):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM entries WHERE user=? ORDER BY id DESC", (user,))
    rows = c.fetchall()
    conn.close()
    return [(row["id"], row["title"], row["created_at"], row["updated_at"], row["content"], row["plaintext"]) for row in rows]

def search_entries(user, query):
    query = query.lower()
    matched_ids = []
    for entry in get_entries(user):
        title, plaintext = entry[1].lower(), entry[5].lower() if entry[5] else ""
        if query in title or query in plaintext:
            matched_ids.append(entry[0])
    return matched_ids
