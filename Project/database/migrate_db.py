import json
import time
from database.db_operations import get_all_tickets, update_ticket
from ai_agent.voice_to_text import extract_information

def migrate():
    print("Starting database migration to update tickets with key_details...")
    records = get_all_tickets()
    updated_count = 0
    skipped_count = 0
    
    for record in records:
        record_id = record['id']
        transcription = record['transcription']
        key_details_str = record['key_details']
        
        needs_update = False
        
        if not key_details_str:
            needs_update = True
        else:
            try:
                info_json = json.loads(key_details_str)
                if len(info_json) == 0:
                    needs_update = True
            except json.JSONDecodeError:
                needs_update = True
                
        if needs_update:
            print(f"Record #{record_id} needs updating. Reprocessing via Llama 3...")
            new_extracted_info = extract_information(transcription)
            if new_extracted_info and isinstance(new_extracted_info, dict):
                key_details = new_extracted_info.get('key_details')
                key_details_str_new = json.dumps(key_details) if key_details else None
                
                update_ticket(
                    ticket_id=record_id, 
                    title=new_extracted_info.get('title', record.get('title')),
                    description=new_extracted_info.get('description', record.get('description')),
                    category=new_extracted_info.get('category', record.get('category')),
                    priority=new_extracted_info.get('priority', record.get('priority')),
                    key_details=key_details_str_new
                )
                updated_count += 1
                print(f"Successfully updated record #{record_id}.")
            else:
                print(f"Failed to extract info for record #{record_id}.")
            
            # Small sleep to prevent hammering the local LLM too fast if there are many records
            time.sleep(1)
        else:
            skipped_count += 1
            
    print("\n--- Migration Complete ---")
    print(f"Total records checked: {len(records)}")
    print(f"Records updated: {updated_count}")
    print(f"Records skipped (already up-to-date): {skipped_count}")

if __name__ == "__main__":
    migrate()
