import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CleanPortal.settings')
django.setup()

from django.template import engines
from django.template.library import import_library

try:
    lib = import_library('accounts.templatetags.custom_filters')
    print("Successfully imported library directly!")
except Exception as e:
    print(f"Failed to import directly: {e}")

try:
    engine = engines['django']
    # This is what Django does internally to find libraries
    from django.template.backends.django import get_package_libraries
    libs = {}
    for app_config in django.apps.apps.get_app_configs():
        libs.update(get_package_libraries(app_config.name + '.templatetags'))
    
    print("Registered libraries found in apps:")
    for name in sorted(libs.keys()):
        print(f" - {name}")
    
    if 'custom_filters' in libs:
        print("\nSUCCESS: 'custom_filters' is registered!")
    else:
        print("\nFAILURE: 'custom_filters' is NOT registered!")

except Exception as e:
    print(f"Error during check: {e}")
