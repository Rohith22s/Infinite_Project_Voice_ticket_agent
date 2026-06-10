import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'voice_data.db')

def insert_ticket(transcription, title=None, description=None, category=None, priority=None, key_details=None, audio_file_path=None, status='Open', sentiment=None, department=None):
    """
    Insert a new ticket record into the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tickets (transcription, title, description, category, priority, key_details, audio_file_path, status, sentiment, department)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (transcription, title, description, category, priority, key_details, audio_file_path, status, sentiment, department))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id

def update_ticket(ticket_id, title=None, description=None, category=None, priority=None, key_details=None):
    """
    Update the details for an existing ticket record.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tickets 
        SET title = ?, description = ?, category = ?, priority = ?, key_details = ?
        WHERE id = ?
    ''', (title, description, category, priority, key_details, ticket_id))
    
    conn.commit()
    conn.close()

def update_ticket_status(ticket_id, new_status):
    """
    Update the status of a ticket.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE tickets SET status = ? WHERE id = ?', (new_status, ticket_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_all_tickets():
    """
    Retrieve all ticket records.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tickets WHERE is_deleted = 0 ORDER BY created_at DESC')
    records = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return records

def get_ticket_by_id(ticket_id):
    """
    Retrieve a single ticket record by its ID.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tickets WHERE id = ? AND is_deleted = 0', (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_ticket(ticket_id):
    """
    Delete a ticket record by its ID (soft delete).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE tickets SET is_deleted = 1 WHERE id = ?', (ticket_id,))
    
    # Check if a row was actually updated
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted

if __name__ == '__main__':
    # Example usage:
    new_id = insert_ticket("Hello, this is a test note.", title="Test", description="Test description", category="Other", priority="Low")
    print(f"Inserted record with ID: {new_id}")
    
    print("All records:")
    for record in get_all_tickets():
        print(record)
