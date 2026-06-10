import sounddevice as sd
from scipy.io.wavfile import write
import os
import time
import argparse
from datetime import datetime
from database.db_operations import insert_ticket
import json
# pyrefly: ignore [missing-import]
import whisper
# pyrefly: ignore [missing-import]
import ollama

print("Loading Whisper model (this may take a few seconds)...")
# Changed to 'base' for faster processing (previously 'small')
whisper_model = whisper.load_model("base")



# Configuration for audio recording
SAMPLE_RATE = 44100
DURATION = 60  # seconds
def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"recording_{timestamp}.wav"

def record_audio(duration=DURATION, fs=SAMPLE_RATE, filename=None):
    if filename is None:
        filename = generate_filename()
    print(f"Recording for {duration} seconds... Please speak now.")
    # Record audio data
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    
    # Save as WAV file
    write(filename, fs, recording)
    return filename

def transcribe_audio(filename):
    try:
        print("Processing audio with local Whisper...")
        # task="translate" converts audio in any language to English text
        result = whisper_model.transcribe(filename, task="translate")
        text = result["text"].strip()
        print(f"\nTranscription successful:\n--> '{text}'\n")
        return text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def extract_information(text):
    try:
        print("Extracting information with local Ollama... (optimized for speed)")
        response = ollama.chat(
            model='llama3',
            format='json',
            options={'temperature': 0.0, 'num_predict': 300}, # Limit output tokens and temperature for faster processing
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert AI support agent. The user may speak in English, Tamil, or a mix of both (Tanglish). The audio has been automatically transcribed and translated into English, which often introduces phonetic misspellings or literal translations of Tamil idioms. Extract and correct the customer's details from this transcription. Fix phonetic errors (e.g. 'Cozzalia K O W S A L Y A' to 'Kowsalya') and interpret context properly. All output must be written in professional English. Return ONLY a valid JSON object with exactly these keys: 'title' (short summary), 'description' (polished explanation of the issue), 'category' (one of: 'Network', 'Hardware', 'Software', 'Other'), 'department' (e.g., 'IT Support', 'Billing', 'Sales', 'General'), 'priority' (STRICTLY determined by department: if IT Support/Hardware/Network -> 'High', if Billing/Finance -> 'Medium', if Sales/General/Other -> 'Low'), 'sentiment' (one of: 'Positive', 'Neutral', 'Frustrated', 'Urgent'), and 'key_details' (a nested JSON object containing exactly 4 keys: 'Name' (Correctly spelled), 'Email' (Format as a valid lowercase email address), 'Mobile No' (Continuous digits only), and 'Problem'. If a detail is missing, use 'Not provided'). Do not include any other text."
                },
                {"role": "user", "content": text}
            ]
        )
        extracted = response['message']['content']
        print(f"\nExtraction successful:\n-->\n{extracted}\n")
        
        # Strip markdown code blocks if present
        if "```json" in extracted:
            extracted = extracted.split("```json")[1].split("```")[0].strip()
        elif "```" in extracted:
            extracted = extracted.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(extracted)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse response as JSON. Error: {e}. Returning raw text.")
            with open("ollama_debug.log", "a") as f:
                f.write(f"JSONDecodeError: {e}\nRaw output: {extracted}\n\n")
            return {"description": extracted}
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        with open("ollama_error.log", "a") as f:
            f.write(f"Exception: {e}\nTraceback: {traceback.format_exc()}\n\n")
        return None

def main():
    parser = argparse.ArgumentParser(description="Voice to Text AI")
    parser.add_argument("-f", "--file", type=str, help="Path to an existing audio file (.wav) to transcribe")
    args = parser.parse_args()

    print("=== Voice to Text AI ===")
    
    try:
        # Step 1: Get audio
        if args.file:
            if not os.path.exists(args.file):
                print(f"Error: File '{args.file}' not found.")
                return
            audio_path = args.file
            print(f"Using provided audio file: {audio_path}")
        else:
            audio_path = record_audio()
            print(f"Audio saved to: {audio_path}")
        
        # Step 2: Transcribe audio
        transcription = transcribe_audio(audio_path)
        
        # Step 3: Extract information
        extracted_info = None
        if transcription:
            extracted_info = extract_information(transcription)
        
        # Step 4: Save to Database
        if transcription:
            print("Saving to database...")
            # We are now saving the actual audio file path to the database
            if extracted_info and isinstance(extracted_info, dict):
                key_details = extracted_info.get('key_details')
                key_details_str = json.dumps(key_details) if key_details else None
                
                record_id = insert_ticket(
                    transcription=transcription,
                    title=extracted_info.get('title'),
                    description=extracted_info.get('description'),
                    category=extracted_info.get('category'),
                    priority=extracted_info.get('priority'),
                    key_details=key_details_str,
                    audio_file_path=audio_path,
                    sentiment=extracted_info.get('sentiment'),
                    department=extracted_info.get('department')
                )
            else:
                record_id = insert_ticket(
                    transcription=transcription,
                    description=str(extracted_info) if extracted_info else None,
                    audio_file_path=audio_path
                )
            print(f"Record successfully saved with ID: {record_id}")
            print(f"Audio file kept at: {audio_path}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
