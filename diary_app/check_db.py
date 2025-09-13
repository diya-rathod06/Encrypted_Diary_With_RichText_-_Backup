import sqlite3
import os

# Use the same path logic as db.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "secure_diary.db")  # <-- correct file

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Show tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", c.fetchall())

# Show schema of entries table
c.execute("PRAGMA table_info(entries);")
print("Schema:", c.fetchall())

# Peek at entries
try:
    c.execute("SELECT id, created_at, updated_at, content_encrypted FROM entries LIMIT 5;")
    for row in c.fetchall():
        print(row)
except Exception as e:
    print("Error:", e)

conn.close()
import sqlite3
import os

# Use the same path logic as db.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "secure_diary.db")  # <-- correct file

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Show tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", c.fetchall())

# Show schema of entries table
c.execute("PRAGMA table_info(entries);")
print("Schema:", c.fetchall())

# Peek at entries
try:
    c.execute("SELECT id, created_at, updated_at, content_encrypted FROM entries LIMIT 5;")
    for row in c.fetchall():
        print(row)
except Exception as e:
    print("Error:", e)

conn.close()
