CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcription TEXT NOT NULL,
    title TEXT,
    description TEXT,
    category TEXT,
    priority TEXT,
    key_details TEXT,
    audio_file_path TEXT,
    status TEXT DEFAULT 'Open',
    sentiment TEXT,
    department TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0
);
