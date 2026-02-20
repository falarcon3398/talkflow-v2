import sqlite3
import os
from pathlib import Path

# Try to find the DB
db_path = Path("/Volumes/FREDDY FILES/ANTIGRAVITY/1001-VIDEO AVATAR/api_server/talkflow.db")

if not db_path.exists():
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, name, type, image_url FROM avatars")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} avatars:")
    for row in rows:
        print(row)
except Exception as e:
    print(f"Error querying DB: {e}")
finally:
    conn.close()
