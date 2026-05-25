import os
import sys
import django
from django.db import transaction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from accounts.models import Complaint

def run():
    apply_changes = '--apply' in sys.argv
    complaints = list(Complaint.objects.all().order_by('id'))
    print(f"Total complaints found: {len(complaints)}")
    
    updates = []
    for index, c in enumerate(complaints, start=1):
        new_id = f"GRT-2026-{str(index).zfill(4)}"
        if c.complaint_id != new_id:
            print(f"Complaint ID {c.id}: {c.complaint_id} -> {new_id}")
            updates.append((c, new_id))
            
    if not updates:
        print("All complaints are already perfectly sequenced!")
        return
        
    print(f"\nProposing to update {len(updates)} complaints.")
    if apply_changes:
        try:
            with transaction.atomic():
                # 1. Update to a temp value first to avoid UniqueViolation
                for c, new_id in updates:
                    temp_id = f"TEMP-{c.id}-{new_id}"
                    c.complaint_id = temp_id
                    c.save(update_fields=['complaint_id'])
                
                # 2. Update to the final sequential value
                for c, new_id in updates:
                    c.complaint_id = new_id
                    c.save(update_fields=['complaint_id'])
            print("Successfully updated database!")
        except Exception as e:
            print(f"Error executing transaction: {e}")
    else:
        print("Dry run complete. Run with '--apply' to save changes.")

if __name__ == '__main__':
    run()
