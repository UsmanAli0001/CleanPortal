import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Complaint, Vehicle
from accounts.views import update_complaint

def run_tests():
    print("--- Starting Programmatic Validation Tests ---")
    
    # 1. Retrieve the test complaint and vehicle
    complaint = Complaint.objects.get(complaint_id='GRT-2026-0034')
    vehicle = Vehicle.objects.get(vehicle_id='GT-TEST')
    
    # Reset statuses
    complaint.status = 'In Progress'
    complaint.save()
    vehicle.status = 'Active'
    vehicle.current_complaint = complaint
    vehicle.save()
    
    print(f"Initial State: Complaint '{complaint.complaint_id}' is '{complaint.status}', Vehicle '{vehicle.vehicle_id}' is '{vehicle.status}'")
    
    # Create request factory
    factory = RequestFactory()
    
    # 2. Test 1: Try to complete the complaint while vehicle is ACTIVE (should block)
    url = f"/update-complaint/{complaint.id}/"
    request = factory.post(url, {
        'status': 'Completed',
        'staff': complaint.assigned_to.id if complaint.assigned_to else ''
    })
    
    # Mock user and messages framework
    request.user = User.objects.get(username='CleanPortal')
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    # Call the view
    response = update_complaint(request, complaint.id)
    
    # Refresh from db
    complaint.refresh_from_db()
    vehicle.refresh_from_db()
    
    print("\n--- Test 1: Completing complaint while vehicle is Active ---")
    print(f"Redirected response status code: {response.status_code}")
    print(f"Complaint Status in DB: '{complaint.status}' (Expected: 'In Progress')")
    
    # Check messages
    msg_texts = [m.message for m in messages]
    print(f"Messages returned to user: {msg_texts}")
    
    assert complaint.status == 'In Progress', "FAIL: Complaint status changed to Completed despite Active vehicle!"
    assert any("must first be set to 'Completed'" in msg for msg in msg_texts), "FAIL: Expected validation error message not found!"
    print("SUCCESS: Test 1 Passed! Validation blocked the transition and showed the correct error message.")
    
    # 3. Test 2: Set vehicle to Completed, then try to complete the complaint (should succeed)
    vehicle.status = 'Completed'
    vehicle.save()
    
    print(f"\nState Update: Set Vehicle '{vehicle.vehicle_id}' status to '{vehicle.status}'")
    
    # New request
    request2 = factory.post(url, {
        'status': 'Completed',
        'staff': complaint.assigned_to.id if complaint.assigned_to else ''
    })
    request2.user = User.objects.get(username='CleanPortal')
    setattr(request2, 'session', 'session')
    messages2 = FallbackStorage(request2)
    setattr(request2, '_messages', messages2)
    
    # Call view again
    response2 = update_complaint(request2, complaint.id)
    
    # Refresh
    complaint.refresh_from_db()
    print("\n--- Test 2: Completing complaint when vehicle is Completed ---")
    print(f"Redirected response status code: {response2.status_code}")
    print(f"Complaint Status in DB: '{complaint.status}' (Expected: 'Completed')")
    
    msg_texts2 = [m.message for m in messages2]
    print(f"Messages returned to user: {msg_texts2}")
    
    assert complaint.status == 'Completed', "FAIL: Complaint status did not change to Completed after vehicle completion!"
    print("SUCCESS: Test 2 Passed! Complaint status successfully updated to Completed.")
    print("\n--- All Programmatic Validation Tests Passed Successfully! ---")

if __name__ == '__main__':
    run_tests()
