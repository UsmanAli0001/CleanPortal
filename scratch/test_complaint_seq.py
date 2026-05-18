import os
import sys
import django

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from accounts.models import Complaint

def test_sequence():
    print("--- Testing Sequential Complaint ID Generation ---")
    
    # 1. Get current maximum numeric ID
    all_ids = Complaint.objects.filter(complaint_id__startswith="GRT-2026-").values_list('complaint_id', flat=True)
    max_num = 0
    for cid in all_ids:
        try:
            num = int(cid.split('-')[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            pass
    
    print(f"Current maximum complaint number: {max_num} (ID: GRT-2026-{str(max_num).zfill(4)})")
    
    # 2. Create a new test complaint
    test_complaint = Complaint.objects.create(
        name="Test User",
        email="test@example.com",
        complaint_type="Garbage issue",
        area="Model Town",
        description="A test complaint to verify ID sequence generation.",
        status="Pending",
        payment_status=False
    )
    
    generated_id = test_complaint.complaint_id
    print(f"Generated Complaint ID: {generated_id}")
    
    expected_num = max_num + 1
    expected_id = f"GRT-2026-{str(expected_num).zfill(4)}"
    print(f"Expected Complaint ID: {expected_id}")
    
    assert generated_id == expected_id, f"Error: Got {generated_id}, expected {expected_id}"
    print("SUCCESS: ID generated matches expectation exactly!")
    
    # Clean up the created test complaint
    test_complaint.delete()
    print("Cleanup successful.")

if __name__ == '__main__':
    test_sequence()
