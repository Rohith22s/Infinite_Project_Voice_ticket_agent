import smtplib
from email.message import EmailMessage
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Department Routing Mappings
DEPARTMENT_EMAILS = {
    "IT Support": "rohithsathish701@gmail.com",
    "Hardware": "rohithsathish701@gmail.com",
    "Network": "rohithsathish701@gmail.com",
    "Software": "rohithsathish701@gmail.com",
    "Billing": "rohithsathish701@gmail.com",
    "Finance": "rohithsathish701@gmail.com",
    "Sales": "rohithsathish701@gmail.com",
    "General": "rohithsathish701@gmail.com"
}

# Standard fallback
DEFAULT_EMAIL = "rohithsathish701@gmail.com"

def get_target_email(department):
    if not department:
        return DEFAULT_EMAIL
    
    # Try exact match
    if department in DEPARTMENT_EMAILS:
        return DEPARTMENT_EMAILS[department]
    
    # Try partial match
    dept_lower = department.lower()
    for key, email in DEPARTMENT_EMAILS.items():
        if key.lower() in dept_lower:
            return email
            
    return DEFAULT_EMAIL

def send_ticket_email(ticket_id, record):
    """
    Sends an email alert to the appropriate department.
    If SMTP credentials are not set, prints the email to the console (Mock Mode).
    """
    department = record.get('department', 'General')
    target_email = get_target_email(department)
    
    title = record.get('title', 'New Support Ticket')
    priority = record.get('priority', 'Low')
    description = record.get('description', 'No description provided.')
    category = record.get('category', 'Other')
    
    key_details = record.get('key_details', '{}')
    if isinstance(key_details, str):
        try:
            key_details = json.loads(key_details)
        except:
            key_details = {}
            
    customer_name = key_details.get('Name', 'Not provided')
    customer_email = key_details.get('Email', 'Not provided')
    customer_phone = key_details.get('Mobile No', 'Not provided')
    
    subject = f"[{priority.upper()}] Ticket #{ticket_id}: {title}"
    
    body = f"""
NEW TICKET ALERT
----------------------------------------
Ticket ID:   #{ticket_id}
Department:  {department}
Category:    {category}
Priority:    {priority}

CUSTOMER DETAILS
----------------------------------------
Name:  {customer_name}
Email: {customer_email}
Phone: {customer_phone}

DESCRIPTION
----------------------------------------
{description}

----------------------------------------
Sent automatically by Ignite Ticket AI.
"""

    smtp_email = os.getenv("SMTP_EMAIL", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    
    if not smtp_email or not smtp_password:
        print("\n" + "="*50)
        print("📧 MOCK EMAIL MODE 📧")
        print(f"Would have sent email to: {target_email}")
        print(f"Subject: {subject}")
        print("-" * 50)
        print(body.strip())
        print("="*50 + "\n")
        return True
        
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_email
        msg['To'] = target_email
        msg.set_content(body)
        
        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(smtp_email, smtp_password)
            smtp.send_message(msg)
            
        print(f"Successfully emailed ticket #{ticket_id} to {target_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {target_email}: {e}")
        return False
