import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'voice_data.db')

def migrate_db():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Step 1: Create the new `tickets` table
    print("Creating new 'tickets' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription TEXT NOT NULL,
            title TEXT,
            description TEXT,
            category TEXT,
            priority TEXT,
            key_details TEXT,
            audio_file_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # Step 2: Fetch all existing voice notes
    print("Fetching existing voice_notes...")
    try:
        cursor.execute("SELECT * FROM voice_notes")
        records = cursor.fetchall()
    except sqlite3.OperationalError:
        print("Table 'voice_notes' does not exist or has already been migrated.")
        conn.close()
        return

    print(f"Found {len(records)} records. Migrating...")
    migrated_count = 0
    
    for row in records:
        record_id = row['id']
        transcription = row['transcription']
        extracted_info_str = row['extracted_info']
        audio_file_path = row['audio_file_path']
        created_at = row['created_at']
        is_deleted = row['is_deleted']
        
        # Default empty values
        title = None
        description = None
        category = None
        priority = None
        key_details_str = None
        
        if extracted_info_str:
            try:
                info = json.loads(extracted_info_str)
                title = info.get('title')
                description = info.get('description')
                category = info.get('category')
                priority = info.get('priority')
                
                key_details = info.get('key_details')
                if key_details and isinstance(key_details, dict):
                    key_details_str = json.dumps(key_details)
            except json.JSONDecodeError:
                # If it's not valid JSON, we can put the raw text into description as a fallback
                description = extracted_info_str

        cursor.execute('''
            INSERT INTO tickets (id, transcription, title, description, category, priority, key_details, audio_file_path, created_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_id, transcription, title, description, category, priority, key_details_str, audio_file_path, created_at, is_deleted))
        
        migrated_count += 1

    print(f"Successfully migrated {migrated_count} records.")

    # Step 3: Rename/Drop the old table
    print("Dropping the old 'voice_notes' table...")
    cursor.execute("DROP TABLE voice_notes")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate_db()
