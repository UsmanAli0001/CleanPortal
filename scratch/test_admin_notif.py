import os
import sys
import django

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from accounts.models import Feedback
from django.contrib.auth.models import User

def test_admin_notifications():
    print("Creating a test feedback to trigger admin notifications...")
    user = User.objects.filter(username='daku84525@gmail.com').first()
    
    # This should trigger notify_admin via the signal
    feedback = Feedback.objects.create(
        user=user,
        rating=5,
        comment="This is a test feedback to verify admin email delivery to all special recipients."
    )
    print(f"Feedback created: {feedback}")

if __name__ == "__main__":
    test_admin_notifications()
