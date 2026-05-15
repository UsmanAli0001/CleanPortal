import os
import sys
import django
import threading
import time

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from accounts.models import Complaint
from django.contrib.auth.models import User

def test_update_notification():
    print("Finding a complaint to update status...")
    complaint = Complaint.objects.first()
    if not complaint:
        print("No complaints found to test.")
        return

    print(f"Updating status for complaint {complaint.complaint_id} from {complaint.status} to 'Verified'...")
    
    # We want to see if emails are sent. 
    # The 'send_aesthetic_email' function uses a thread, so we might need to wait a bit to see the output.
    
    complaint.status = 'Verified'
    complaint.save()
    
    print("Update saved. Waiting a few seconds for background threads to log...")
    time.sleep(5)

if __name__ == "__main__":
    test_update_notification()
