# src/email_notification.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from .config import SENDER_EMAIL, PASSWORD, RECEIVER_EMAIL

def send_email(subject, body, attachment_dir):
    # Use credentials from config.py
    sender_email = SENDER_EMAIL
    password = PASSWORD
    to_email = RECEIVER_EMAIL

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach the video file from the directory
    for filename in os.listdir(attachment_dir):
        file_path = os.path.join(attachment_dir, filename)
        if os.path.isfile(file_path):
            part = MIMEBase('application', 'octet-stream')
            with open(file_path, 'rb') as attachment:
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)

    # Connect to the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)

    # Send the email
    text = msg.as_string()
    server.sendmail(sender_email, to_email, text)
    server.quit()

    print(f"Email sent to {to_email} with attachments.")