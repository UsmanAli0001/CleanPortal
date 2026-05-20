import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    username = 'CleanPortal'
    email = 'cleanportal@gmail.com'
    password = 'cleanportal123'
    
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True
    })
    
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"Superuser '{username}' password successfully set to '{password}'.")

if __name__ == '__main__':
    main()
