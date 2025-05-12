import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import argparse
import os
import getpass
import sys
from dotenv import load_dotenv

load_dotenv()


def send_email(sender_email, receiver_email, subject, body, 
               smtp_server="smtp.gmail.com", port=587, 
               password=None, attachment_path=None):
    """
    Send an email from sender_email to receiver_email with optional attachment.
    
    Args:
        sender_email (str): The email address to send from
        receiver_email (str): The email address to send to
        subject (str): The subject of the email
        body (str): The body text of the email
        smtp_server (str): SMTP server address (default: smtp.gmail.com)
        port (int): SMTP server port (default: 587 for TLS)
        password (str): Password for the sender email account
        attachment_path (str, optional): Path to a file to attach
    
    Returns:
        bool: True if sending was successful, False otherwise
    """
    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    # Add attachment if specified
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_path))
                
            # Add header as key/value pair to attachment part
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            message.attach(part)
            print(f"Attached: {os.path.basename(attachment_path)}")
        except Exception as e:
            print(f"Failed to attach file: {e}")
            return False
    
    # Log in to server and send email
    try:
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            
            if password:
                server.login(sender_email, password)
            
            server.sendmail(sender_email, receiver_email, message.as_string())
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def main():
    """Parse command line arguments and send email."""
    parser = argparse.ArgumentParser(description='Send an email with optional attachment')
    
    # Required arguments
    parser.add_argument('--from', dest='sender', required=True,
                        help='Sender email address')
    parser.add_argument('--to', dest='receiver', required=True,
                        help='Recipient email address')
    parser.add_argument('--subject', required=True,
                        help='Subject of the email')
    
    # Optional arguments
    parser.add_argument('--body', default='',
                        help='Body text of the email')
    parser.add_argument('--body-file', dest='body_file',
                        help='Path to file containing body text')
    parser.add_argument('--attachment', 
                        help='Path to file to attach')
    parser.add_argument('--server', default='smtp.gmail.com',
                        help='SMTP server address (default: smtp.gmail.com)')
    parser.add_argument('--port', type=int, default=587,
                        help='SMTP server port (default: 587)')
    parser.add_argument('--no-prompt', dest='no_prompt', action='store_true',
                        help='Do not prompt for password (use environment variable EMAIL_PASSWORD)')
    
    args = parser.parse_args()
    
    # Get body from file if specified
    body = args.body
    if args.body_file:
        try:
            with open(args.body_file, 'r') as f:
                body = f.read()
        except Exception as e:
            print(f"Error reading body file: {e}")
            return 1
    
    # Get password
    password = os.getenv('EMAIL_PASSWORD')
    if not password and not args.no_prompt:
        password = getpass.getpass(f"Enter password for {args.sender}: ")
    
    if not password:
        print("No password provided. For Gmail, you may need to use an App Password.")
        print("Instructions: https://support.google.com/accounts/answer/185833")
        return 1
    
    # Send the email
    print(f"Sending email from {args.sender} to {args.receiver}...")
    success = send_email(
        sender_email=args.sender,
        receiver_email=args.receiver,
        subject=args.subject,
        body=body,
        smtp_server=args.server,
        port=args.port,
        password=password,
        attachment_path=args.attachment
    )
    
    if success:
        print("Email sent successfully!")
        return 0
    else:
        print("Failed to send email.")
        return 1


if __name__ == "__main__":
    sys.exit(main())