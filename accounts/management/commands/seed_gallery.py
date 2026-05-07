from django.core.management.base import BaseCommand
from accounts.models import Complaint
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Seeds the database with before and after gallery data.'

    def handle(self, *args, **options):
        # Create __init__.py if missing
        open('accounts/management/__init__.py', 'a').close()
        open('accounts/management/commands/__init__.py', 'a').close()

        data = [
            {
                'type': 'Street Cleaning',
                'area': 'Model Town',
                'desc': 'Daily street sweeping and dust control operation.',
                'before': 'complaints/images/street_before.png',
                'after': 'complaints/after_images/street_after.png'
            },
            {
                'type': 'Garbage Issue',
                'area': 'G.T. Road',
                'desc': 'Bulk waste removal and area sanitization successful.',
                'before': 'complaints/images/garbage_before.png',
                'after': 'complaints/after_images/garbage_after.png'
            },
            {
                'type': 'Water Issue',
                'area': 'Bhimber Road',
                'desc': 'Leaking main line repaired and surrounding area restored.',
                'before': 'complaints/images/water_before.png',
                'after': 'complaints/after_images/water_after.png'
            }
        ]

        for item in data:
            c, created = Complaint.objects.get_or_create(
                complaint_type=item['type'],
                area=item['area'],
                description=item['desc'],
                status='Completed',
                payment_status=True,
                defaults={'name': 'System Seed', 'email': 'admin@cleanportal.com'}
            )
            
            # Since files are already in media, we just update the path
            c.image = item['before']
            c.after_image = item['after']
            c.save()
            
            self.stdout.write(self.style.SUCCESS(f"Seeded gallery item for {item['type']}"))
