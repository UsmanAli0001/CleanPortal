import os
import re

def main():
    templates_dir = "c:/Users/hp/OneDrive/Desktop/django/CleanPortal/accounts/templates"
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # find all forms
                forms = re.findall(r'<form[\s\S]*?</form>', content, re.IGNORECASE)
                for i, form in enumerate(forms):
                    if 'method="post"' in form.lower() or "method='post'" in form.lower() or "method=post" in form.lower():
                        if "{% csrf_token %}" not in form:
                            print(f"File: {path}")
                            print(f"Missing CSRF token in POST form #{i+1}")

if __name__ == "__main__":
    main()
