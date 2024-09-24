import imaplib
import email
from email.header import decode_header
import time
from datetime import datetime
import pytz  # Import pytz for timezone handling
from dotenv import load_dotenv
import os

load_dotenv()
# Gmail IMAP server settings
IMAP_SERVER = os.getenv('IMAP_SERVER')
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
APP_PASSWORD = os.getenv('APP_PASSWORD')

# List to store found email details
found_emails = []

def extract_email_body(msg):
    """Extract the plain text body of the email."""
    # If the email is multipart, we need to get the payload
    if msg.is_multipart():
        for part in msg.walk():
            # If part is text/plain, return its content
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
    else:
        # If it's a single part, return its content directly
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
    return None  # Return None if no text/plain part found

def check_sent_emails(start_time):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    
    # Select the "Sent" folder
    mail.select('"[Gmail]/Sent Mail"')

    # Search for all emails in the Sent folder
    date_str = start_time.strftime("%d-%b-%Y")
    result, data = mail.search(None, f'SINCE "{date_str}"')

    # Get the list of email IDs
    email_ids = data[0].split()

    # Loop through each email ID
    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        
        # Get the email sent time
        sent_time = email.utils.parsedate_to_datetime(msg['Date'])

        # Ensure sent_time is timezone-aware
        if sent_time.tzinfo is None:
            sent_time = sent_time.replace(tzinfo=pytz.UTC)

        # Check if the email was sent after the script started
        if sent_time > start_time:
            # Decode the email subject
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')

            # Check if the subject matches "Network Upgrade"
            if subject == "Network Upgrade":
                # Prepare email details
                email_details = {
                    'from': msg['From'],
                    'subject': subject,
                    'date': sent_time,
                    'body': extract_email_body(msg)  # Extract the email body
                }
                
                # Check if this email is already in the found_emails list
                if email_details not in found_emails:
                    found_emails.append(email_details)  # Store unique email details
                    print(f"Found email with subject '{subject}' from {msg['From']} on {sent_time}")
                    print(f"Body: {email_details['body']}")  # Print the email body

    # Logout from the server
    mail.logout()

# Get the start time of the script
start_time = datetime.now(pytz.UTC)  # Make start_time timezone-aware

# Run the script in a loop to monitor
while True:
    check_sent_emails(start_time)
    time.sleep(60)  # Check every minute
