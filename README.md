# Ignite Ticket: AI Voice → Ticket Agent

Ignite Ticket is a next-generation AI-powered customer support dashboard. It automates the entire support pipeline by listening to user audio (in English or regional languages like Tamil), transcribing and translating it, and using local LLMs to intelligently extract structured ticket metadata (Name, Email, Priority, Category, and Department). Finally, it routes the generated ticket to the appropriate department via automated email.

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/9cb60ba8-fcee-4525-a118-e68f167959f0" />


# Features

-  Voice-to-Text & Translation**: Utilizes OpenAI's Whisper model to transcribe audio and translate regional languages (like Tamil) into English automatically.
-  Intelligent JSON Extraction**: Uses Llama 3 (via Ollama) to analyze the transcript, correct phonetic misspellings, determine sentiment, and extract key details (`Name`, `Email`, `Mobile No`, `Problem`).
-  Automated Priority & Routing**: The AI automatically assigns ticket priorities (Low, Medium, High, Critical) and categorizes issues by department (IT Support, Hardware, Billing, etc.).
-  Smart Email Dispatch**: Automatically emails the structured ticket directly to the assigned department using an SMTP integration with fallback mock mode.
-  Glassmorphism UI**: A beautiful, modern, and fully responsive frontend dashboard built with vanilla HTML/CSS/JS, featuring dynamic priority badges and real-time ticket rendering.
-  SQLite Database**: Lightweight and reliable local storage for all tickets and audio file references.

# Technology Stack

- Backend: Python, Flask
- AI/ML: Whisper (Local Speech-to-Text), Llama 3 (Local LLM via Ollama)
- Database: SQLite3
- Frontend: HTML5, CSS3 (Glassmorphism Theme), Vanilla JavaScript
- Audio Processing: Sounddevice, Scipy, FFmpeg

# Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.8+](https://www.python.org/downloads/)
- [FFmpeg](https://ffmpeg.org/download.html) (Required for audio format conversion)
- [Ollama](https://ollama.com/) (Required for running Llama 3 locally)

You must pull the Llama 3 model into Ollama before running the app:
```bash
ollama run llama3
```

# Installation & Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ignite-ticket.git
   cd ignite-ticket
   ```

2. Set up a Virtual Environment (Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install Dependencies
   ```bash
   pip install flask openai-whisper sounddevice scipy ollama python-dotenv
   ```

4. Environment Variables
   Create a `.env` file in the root directory for email routing:
   ```env
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```
   *(Note: If left empty, the app will safely fall back to "Mock Email Mode" and print emails to the terminal).*

# Running the Application

1. Start the Backend/Frontend Server
   ```bash
   python backend/app.py
   ```
2. Access the Dashboard
   Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

# Testing

To manually test the AI pipeline from the UI:
1. Click "Record" on the dashboard.
2. Speak a sample issue (e.g., *"My name is John, my email is john@test.com, and my internet router is completely dead!"*).
3. Click "Submit".
4. The system will convert your voice, extract the JSON, route the email, and display the new ticket on the dashboard with a `High` priority badge.

# Project Structure

```text
├── backend/
│   ├── app.py              # Main Flask server and API routes
│   └── email_service.py    # SMTP dispatch logic
├── frontend/
│   ├── static/             # CSS styling and JS logic
│   └── templates/          # HTML templates (index, ticket view)
├── database/
│   ├── db_operations.py    # SQLite queries and inserts
│   └── db/                 # Contains voice_data.db
├── ai_agent/
│   └── voice_to_text.py    # Whisper transcription & Llama 3 extraction logic
└── .env                    # Secret environment variables
```


# License
This project is open-source and available under the [MIT License](LICENSE).
