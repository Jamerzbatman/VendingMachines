import os
import sys
import subprocess

# Ask for the app name
app_name = input("Enter the Django app name: ").strip()

if not app_name:
    print("App name cannot be empty!")
    sys.exit(1)

# Create the app using Django's management command
os.system(f"python manage.py startapp {app_name}")

# Path to settings.py
settings_path = "main/settings.py"

# Read the settings.py file
with open(settings_path, "r") as file:
    lines = file.readlines()

# Find INSTALLED_APPS
installed_apps_index = None
for i, line in enumerate(lines):
    if "INSTALLED_APPS" in line:
        installed_apps_index = i
        break

if installed_apps_index is None:
    print("Could not find INSTALLED_APPS in settings.py!")
    sys.exit(1)

# Check if the app is already listed
if f"'{app_name}'," in "".join(lines):
    print(f"App '{app_name}' is already in INSTALLED_APPS.")
else:
    # Insert the app name before the closing bracket of INSTALLED_APPS
    for i in range(installed_apps_index, len(lines)):
        if lines[i].strip().startswith("]"):
            lines.insert(i, f"    '{app_name}',\n")
            break

    # Write back to settings.py
    with open(settings_path, "w") as file:
        file.writelines(lines)

    print(f"App '{app_name}' added to INSTALLED_APPS.")

print(f"App '{app_name}' created successfully.")

# Get the script file path
script_path = os.path.abspath(__file__)

# Use subprocess to delete the script after completion
delete_command = f"python -c \"import os, time; time.sleep(2); os.remove(r'{script_path}'); print('Script deleted successfully.')\""
