import imaplib
import email
from email.header import decode_header
import time
import json  # Import json for saving in JSON format
import os
from dotenv import load_dotenv

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

def load_saved_email_ids(filename="email_ids.json"):
    """Load saved email IDs from a JSON file."""
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return set(json.load(file))  # Return as a set for fast lookup
    return set()

def save_email_id(email_id, filename="email_ids.json"):
    """Save a new email ID to the JSON file."""
    saved_ids = load_saved_email_ids(filename)
    saved_ids.add(email_id)  # Add the new email ID
    with open(filename, 'w') as file:
        json.dump(list(saved_ids), file)  # Save back to the file
    print(f"Email ID {email_id} saved.")

def load_emails_from_json(filename="emails.json"):
    """Load existing emails from a JSON file."""
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)  # Load existing email details
    return []  # Return an empty list if no file exists

def save_email_to_json(email_details, filename="emails.json"):
    """Save the email details to a JSON file."""
    existing_emails = load_emails_from_json(filename)  # Load existing emails
    existing_emails.append(email_details)  # Append the new email details
    with open(filename, 'w') as file:
        json.dump(existing_emails, file, indent=4)  # Save back to the file
    print(f"Email saved to {filename}")

def fetch_last_email_with_subjects(subjects_to_find):
    """
    Function to continuously check the last sent email for specific subjects in the Gmail 'Sent Mail' folder.
    Saves the email details in JSON format if the subject matches and the email ID is unique.
    """
    while True:
        try:
            # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ACCOUNT, APP_PASSWORD)

            # Select the "Sent" folder
            mail.select('"[Gmail]/Sent Mail"')

            # Search for all email IDs in the Sent folder
            result, data = mail.search(None, "ALL")

            # Get the list of email IDs
            email_ids = data[0].split()
            if email_ids:
                # Get the last (most recent) email ID
                latest_email_id = email_ids[-1]

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
                    email_id = msg['Message-ID']  # Unique email ID

                    # Check if the email ID is unique
                    saved_ids = load_saved_email_ids()
                    if email_id not in saved_ids:
                        # Prepare the email details as a dictionary for JSON
                        email_details = {
                            "Subject": subject,
                            "From": msg['From'],
                            "Date": sent_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                            "Body": body
                        }

                        # Save the email ID and details
                        save_email_id(email_id)
                        save_email_to_json(email_details)
                    else:
                        print(f"Email ID {email_id} already exists. Discarding the email.")
                else:
                    print(f"No matching subject found in the last sent email: {subject}")

            # Wait for a minute before checking again
            time.sleep(10)

        except imaplib.IMAP4.error as e:
            print(f"IMAP error occurred: {e}")
            time.sleep(60)  # Wait before trying to reconnect

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait before trying again

        finally:
            # Logout from the server
            mail.logout()

# Example usage:
# Continuously check for emails with "Network Upgrade", "Change IDs", or "Device Status"
subjects_to_monitor = ["Network Upgrade", "Change IDs", "Device Status"]
fetch_last_email_with_subjects(subjects_to_monitor)