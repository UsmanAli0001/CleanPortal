import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Complaint, Vehicle, Staff
from accounts.views import update_complaint

def run_tests():
    print("--- Starting Complaint Status Transition Validation Tests ---")
    
    # 1. Setup Test Data
    # Fetch/create admin user
    user, _ = User.objects.get_or_create(username='CleanPortal', defaults={'is_staff': True})
    user.is_staff = True
    user.save()
    
    # Fetch/create staff member
    staff, _ = Staff.objects.get_or_create(
        name='Transition Tester',
        defaults={'role': 'Driver', 'area': 'Model Town', 'phone': '0300-1122334'}
    )
    
    # Create test complaint
    complaint, _ = Complaint.objects.get_or_create(
        complaint_id='TRANSITION-TEST-001',
        defaults={
            'name': 'Test User',
            'complaint_type': 'Garbage issue',
            'area': 'Model Town',
            'description': 'Test complaint transitions',
            'payment_status': True,
            'assigned_to': staff
        }
    )
    complaint.assigned_to = staff
    complaint.save()
    
    # Create test vehicle and set its status to Completed
    vehicle, _ = Vehicle.objects.get_or_create(
        vehicle_id='TRANS-VEH',
        defaults={
            'vehicle_type': 'Garbage issue',
            'driver_name': 'Tester',
            'assigned_zone': 'Model Town',
            'status': 'Completed',
            'is_active': True,
            'current_complaint': complaint
        }
    )
    vehicle.status = 'Completed'
    vehicle.current_complaint = complaint
    vehicle.save()
    
    factory = RequestFactory()
    url = f"/update-complaint/{complaint.id}/"
    
    def try_transition(from_status, to_status, should_succeed):
        # Set complaint status in database
        complaint.status = from_status
        complaint.save()
        
        print(f"\n--- Testing Transition: '{from_status}' -> '{to_status}' (Expected to {'SUCCEED' if should_succeed else 'FAIL'}) ---")
        
        request = factory.post(url, {
            'status': to_status,
            'staff': staff.id
        })
        request.user = user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Call the view
        response = update_complaint(request, complaint.id)
        
        # Refresh from db
        complaint.refresh_from_db()
        msg_texts = [m.message for m in messages]
        
        print(f"Redirect response code: {response.status_code}")
        print(f"Complaint Status in DB: '{complaint.status}'")
        print(f"Messages returned: {msg_texts}")
        
        if should_succeed:
            assert complaint.status == to_status, f"FAIL: Expected status to become '{to_status}'!"
            print(f"SUCCESS: Successfully transitioned from '{from_status}' to '{to_status}'!")
        else:
            assert complaint.status == from_status, f"FAIL: Status illegally transitioned to '{to_status}'!"
            assert any(f"cannot be changed from" in msg for msg in msg_texts), "FAIL: Missing validation error message!"
            print(f"SUCCESS: Correctly blocked illegal transition from '{from_status}' to '{to_status}'!")

    try:
        # Test Case 1: Completed -> In Progress (Should Fail)
        try_transition('Completed', 'In Progress', should_succeed=False)
        
        # Test Case 2: Completed -> Verified (Should Fail)
        try_transition('Completed', 'Verified', should_succeed=False)
        
        # Test Case 3: Completed -> Pending (Should Fail)
        try_transition('Completed', 'Pending', should_succeed=False)
        
        # Test Case 4: In Progress -> Verified (Should Fail)
        try_transition('In Progress', 'Verified', should_succeed=False)
        
        # Test Case 5: In Progress -> Pending (Should Fail)
        try_transition('In Progress', 'Pending', should_succeed=False)
        
        # Test Case 6: Verified -> Pending (Should Fail)
        try_transition('Verified', 'Pending', should_succeed=False)
        
        # Test Case 7: Pending -> In Progress (Should Succeed)
        try_transition('Pending', 'In Progress', should_succeed=True)
        
        # Test Case 8: In Progress -> Completed (Should Succeed)
        try_transition('In Progress', 'Completed', should_succeed=True)
        
        print("\n=== ALL COMPLAINT TRANSITION TESTS PASSED SUCCESSFULLY! ===")
        
    finally:
        # Cleanup test data
        vehicle.delete()
        complaint.delete()

if __name__ == '__main__':
    run_tests()
