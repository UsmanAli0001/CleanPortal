import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
sys.path.append(os.getcwd())
django.setup()

from accounts.signals import send_aesthetic_email

email = "daku84525@gmail.com"
print(f"Sending manual test email to {email}...")
send_aesthetic_email(
    subject="Final Status Check",
    recipient_email=email,
    user_name="Rehman",
    message_title="Configuration Complete",
    message_content="Your account has been set as a permanent recipient for system alerts. Staff status has been removed as requested."
)
print("Done.")
