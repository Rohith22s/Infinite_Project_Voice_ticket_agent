from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from datetime import datetime
import sys
import urllib.request
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our existing logic
from ai_agent.voice_to_text import transcribe_audio, extract_information
from database.db_operations import insert_ticket, get_all_tickets, get_ticket_by_id, delete_ticket, update_ticket_status

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Directory to save web audio files
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    status = {
        'Flask Server': 'Online',
        'Database': 'Offline',
        'Whisper Agent': 'Online', # Loaded with Flask
        'Llama 3 Agent': 'Offline'
    }
    
    # Check Database
    try:
        from database.db_operations import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        if cursor.fetchone():
            status['Database'] = 'Online'
        conn.close()
    except Exception:
        pass
        
    # Check Ollama
    try:
        req = urllib.request.Request('http://localhost:11434/')
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                status['Llama 3 Agent'] = 'Online'
    except Exception:
        pass
        
    return jsonify(status)

@app.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):
    return render_template('ticket.html', ticket_id=ticket_id)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/records', methods=['GET'])
def get_records():
    try:
        records = get_all_tickets()
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        record = get_ticket_by_id(ticket_id)
        if record:
            return jsonify(record)
        return jsonify({'error': 'Ticket not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ticket/<int:ticket_id>', methods=['DELETE'])
def delete_ticket_route(ticket_id):
    try:
        success = delete_ticket(ticket_id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Ticket not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ticket/<int:ticket_id>/status', methods=['PUT'])
def update_ticket_status_route(ticket_id):
    try:
        data = request.json
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = update_ticket_status(ticket_id, new_status)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Ticket not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400

    # Save the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(audio_file.filename)[1].lower()
    if not ext:
        ext = '.wav'
    filename = f"web_recording_{timestamp}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio_file.save(filepath)

    # Convert to wav if it's not a .wav file
    if ext != '.wav':
        import subprocess
        wav_filename = f"web_recording_{timestamp}.wav"
        wav_filepath = os.path.join(UPLOAD_FOLDER, wav_filename)
        try:
            print(f"Converting {ext} to .wav using ffmpeg...")
            subprocess.run(['ffmpeg', '-y', '-i', filepath, wav_filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(wav_filepath):
                os.remove(filepath)
                filepath = wav_filepath
                filename = wav_filename
                print("Conversion successful.")
        except Exception as e:
            print(f"Failed to convert {ext} to wav: {e}")
            # Continue with original file if conversion fails

    print(f"Audio saved to {filepath}, starting transcription...")
    
    try:
        # Process with existing code
        transcription = transcribe_audio(filepath)
        
        extracted_info = None
        if transcription is not None:
            if transcription.strip() == "":
                return jsonify({'error': 'No speech detected in the audio'}), 400
                
            extracted_info = extract_information(transcription)
            
            # Save to DB
            db_filepath = f"uploads/{filename}"
            
            if extracted_info and isinstance(extracted_info, dict):
                import json
                key_details = extracted_info.get('key_details')
                key_details_str = json.dumps(key_details) if key_details else None
                
                record_id = insert_ticket(
                    transcription=transcription,
                    title=extracted_info.get('title'),
                    description=extracted_info.get('description'),
                    category=extracted_info.get('category'),
                    priority=extracted_info.get('priority'),
                    key_details=key_details_str,
                    audio_file_path=db_filepath,
                    sentiment=extracted_info.get('sentiment'),
                    department=extracted_info.get('department')
                )
                
                try:
                    import email_service
                    email_service.send_ticket_email(record_id, extracted_info)
                except Exception as e:
                    print(f"Error dispatching email: {e}")
            else:
                record_id = insert_ticket(
                    transcription=transcription,
                    description=str(extracted_info) if extracted_info else None,
                    audio_file_path=db_filepath
                )
            
            return jsonify({
                'success': True,
                'id': record_id,
                'transcription': transcription,
                'extracted_info': extracted_info,
                'audio_file_path': db_filepath
            })
        else:
            return jsonify({'error': 'Transcription failed'}), 500
    except Exception as e:
        print(f"Error processing audio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<path:filename>')
def serve_audio(filename):
    # Safely serve audio files from the uploads folder
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
