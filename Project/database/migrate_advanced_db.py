import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'voice_data.db')

def upgrade_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [col[1] for col in cursor.fetchall()]
    
    try:
        if 'status' not in columns:
            cursor.execute("ALTER TABLE tickets ADD COLUMN status TEXT DEFAULT 'Open'")
            print("Added 'status' column.")
            
        if 'sentiment' not in columns:
            cursor.execute("ALTER TABLE tickets ADD COLUMN sentiment TEXT")
            print("Added 'sentiment' column.")
            
        if 'department' not in columns:
            cursor.execute("ALTER TABLE tickets ADD COLUMN department TEXT")
            print("Added 'department' column.")
            
        conn.commit()
        print("Database schema successfully upgraded!")
    except Exception as e:
        print(f"Error upgrading schema: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_schema()
