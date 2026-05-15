import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth.models import User

emails = [
    "daku84525@gmail.com",
    "neendiyanchurail@gmail.com",
    "nida0786495@gmail.com",
    "pookiee7717@gmail.com",
    "quiettears124713@gmail.com",
    "u0736874@gmail.com",
    "ua837300@gmail.com",
    "ua934825@gmail.com",
    "ua993073@gmail.com"
]

print("Removing Staff/Superuser status from the 9 users...")
for email in emails:
    user = User.objects.filter(email=email).first()
    if user:
        user.is_staff = False
        user.is_superuser = False
        user.save()
        print(f"REVERTED: {email} | Staff: {user.is_staff} | Superuser: {user.is_superuser}")
    else:
        print(f"NOT FOUND: {email}")
