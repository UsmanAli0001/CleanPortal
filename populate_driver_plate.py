import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from accounts.models import DriverDetail

def assign_unique_plate_numbers(start=1, end=50, prefix='PLT'):
    """Assign unique plate numbers to DriverDetail records with IDs in the given range.
    Plate numbers will be in the format '{prefix}-{num:03d}'.
    Only records without a plate_number are updated.
    """
    drivers = DriverDetail.objects.filter(id__gte=start, id__lte=end).order_by('id')
    for idx, driver in enumerate(drivers, start=start):
        if not driver.plate_number:
            driver.plate_number = f"{prefix}-{idx:03d}"
            driver.save(update_fields=['plate_number'])
            print(f"Assigned plate {driver.plate_number} to driver {driver.id}")
        else:
            print(f"Driver {driver.id} already has plate {driver.plate_number}")

if __name__ == '__main__':
    # Adjust range as needed; here we assume driver IDs 1-50 correspond to SR NO 1-50
    assign_unique_plate_numbers(1, 50)
