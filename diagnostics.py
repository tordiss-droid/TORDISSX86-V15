import os
import sys
import importlib.util

print("\n===== TORDISSX86 SYSTEM DIAGNOSTICS =====")
print("Python:", sys.version.split()[0])

modules = [
    "profile.py",
    "username.py",
    "posts.py",
    "image_meta.py",
    "reports.py",
    "search_reports.py",
    "export.py",
    "timeline.py"
]

print("\nMODULE STATUS:")
for module in modules:
    status = "ONLINE" if os.path.isfile(module) else "MISSING"
    print(f"{module}: {status}")

print("\nREPORTS FOLDER:",
      "AVAILABLE" if os.path.isdir("reports") else "MISSING")

print("PILLOW:",
      "INSTALLED" if importlib.util.find_spec("PIL") else "NOT INSTALLED")

print("\n===== CHECK COMPLETE =====")
input("\nPress ENTER to return...")
