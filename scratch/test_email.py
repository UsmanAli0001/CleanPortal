import os
import sys
import django

# Add current directory to sys.path
sys.path.append(os.getcwd())

from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

def test_email():
    try:
        print(f"Attempting to send email from {settings.EMAIL_HOST_USER}...")
        subject = 'Test Email from CleanPortal'
        message = 'This is a test email to verify SMTP configuration.'
        recipient_list = ['cleanpakportal@gmail.com'] # Sending to self for test
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

if __name__ == "__main__":
    test_email()
