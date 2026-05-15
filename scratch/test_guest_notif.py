import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from accounts.models import Complaint, User
from accounts.signals import send_aesthetic_email
from django.utils import timezone

def test_guest_update():
    print("--- Testing Guest User Update ---")
    # 1. Create a guest complaint
    guest_email = "guest_test_user@example.com"
    complaint = Complaint.objects.create(
        name="Guest User",
        email=guest_email,
        complaint_type="Overflowing Bin",
        area="Test Area",
        description="This is a guest complaint test.",
        payment_status=True,
        status="Pending"
    )
    print(f"Created guest complaint: {complaint.complaint_id}")

    # 2. Update status (should trigger email directly to guest_email)
    print("\nUpdating status to 'Verified'...")
    complaint.status = "Verified"
    complaint.save()

    print("\nCheck the console output above for SUCCESS/ERROR logs.")
    
    # 3. Cleanup
    complaint.delete()

if __name__ == "__main__":
    test_guest_update()
