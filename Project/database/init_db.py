import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'voice_data.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'db', 'schema.sql')

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read the schema file
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, 'r') as f:
            schema_script = f.read()
            
        # Execute the schema script
        cursor.executescript(schema_script)
        conn.commit()
        print("Database initialized successfully.")
    else:
        print(f"Error: Schema file '{SCHEMA_PATH}' not found.")
        
    conn.close()

if __name__ == '__main__':
    init_db()
