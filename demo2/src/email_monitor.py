import imaplib
import email
from email.header import decode_header
import time
from datetime import datetime
import pytz  # Import pytz for timezone handling
from dotenv import load_dotenv
import os

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

def save_email_to_file(email_details, filename="emails.txt"):
    """Save the email details to a file."""
    with open(filename, 'a') as file:
        file.write(email_details + "\n\n")
    print(f"Email saved to {filename}")

def fetch_last_email_with_subjects(subjects_to_find):
    """
    Function to continuously check the last sent email for specific subjects in the Gmail 'Sent Mail' folder.
    Saves the email details to a file if the subject matches.
    """
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)

    last_checked_email_id = None  # Store the last checked email ID to avoid repeated processing

    try:
        # Select the "Sent" folder
        mail.select('"[Gmail]/Sent Mail"')

        # Keep checking for new emails
        while True:
            # Search for all email IDs in the Sent folder
            result, data = mail.search(None, "ALL")

            # Get the list of email IDs
            email_ids = data[0].split()
            if email_ids:
                # Get the last (most recent) email ID
                latest_email_id = email_ids[-1]
                print(latest_email_id)
                # Check if it's a new email (not the same as the last checked)
                if latest_email_id != last_checked_email_id:
                    last_checked_email_id = latest_email_id

                    # Fetch the latest email
                    result, msg_data = mail.fetch(latest_email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Decode the email subject
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')

                    # Check if the subject matches any in the desired list
                    if any(keyword in subject for keyword in subjects_to_find):
                        # Extract the email body
                        body = extract_email_body(msg)

                        # Get the email sent time
                        sent_time = email.utils.parsedate_to_datetime(msg['Date'])

                        # Prepare the email details string
                        email_details = (
                            f"Subject: {subject}\n"
                            f"From: {msg['From']}\n"
                            f"Date: {sent_time}\n"
                            f"Body:\n{body}"
                        )

                        # Save the email details to a file
                        save_email_to_file(email_details)
                    else:
                        print(f"No matching subject found in the last sent email: {subject}")

            # Wait for a minute before checking again
            time.sleep(10)

    finally:
        # Logout from the server
        mail.logout()

# Example usage:
# Continuously check for emails with "Network Upgrade", "Change IDs", or "Device Status"
subjects_to_monitor = ["Network Upgrade", "Change IDs", "Device Status"]
fetch_last_email_with_subjects(subjects_to_monitor)
