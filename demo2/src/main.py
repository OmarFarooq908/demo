from email_monitor import EmailMonitor
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
APP_PASSWORD = os.getenv('APP_PASSWORD')
def main():
    # Replace with your email and password
    email_address = EMAIL_ACCOUNT
    email_password = APP_PASSWORD
    
    # Define criteria for monitoring outgoing emails
    monitoring_criteria = ['Network Upgrade', 'Change ID', 'Device Status']

    # Initialize the EmailMonitor
    email_monitor = EmailMonitor(email_address, email_password, monitoring_criteria)
    
    # Start monitoring emails
    email_monitor.monitor_emails()

if __name__ == "__main__":
    main()