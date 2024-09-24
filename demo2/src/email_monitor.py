import imaplib
import email
from email.header import decode_header
import time
from datetime import datetime
import pytz  # Import pytz for timezone handling
from dotenv import load_dotenv
import os
from crewai_tools import tool  # type: ignore # Replace with your actual tool library

# Load environment variables from .env file
load_dotenv()

# Gmail IMAP server settings
IMAP_SERVER = os.getenv('IMAP_SERVER')
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
APP_PASSWORD = os.getenv('APP_PASSWORD')

def extract_email_body(msg):
    """Extract the plain text body of the email."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
    else:
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
    return None  # Return None if no text/plain part found

@tool  # Decorator to expose this function as a tool
def fetch_email_with_subject(subject_to_find="Network Upgrade"):
    """
    Function to check for the first email with a specific subject in the Gmail 'Sent Mail' folder.
    Returns the email details as a string and stops monitoring once found.
    """
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)

    try:
        # Select the "Sent" folder
        mail.select('"[Gmail]/Sent Mail"')

        # Get the current time
        start_time = datetime.now(pytz.UTC)

        # Search for all emails since the script start time
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

                # Check if the subject matches the desired one
                if subject == subject_to_find:
                    # Extract the email body
                    body = extract_email_body(msg)

                    # Prepare the email details string
                    email_details = (
                        f"Subject: {subject}\n"
                        f"From: {msg['From']}\n"
                        f"Date: {sent_time}\n"
                        f"Body:\n{body}"
                    )

                    # Return the email details and stop monitoring
                    return email_details

        # If no email is found after looping through
        return "No email with the specified subject found."

    finally:
        # Logout from the server
        mail.logout()

# Example usage of the tool:
# If this tool is called, it will check the 'Sent Mail' folder for an email with the subject "Network Upgrade"