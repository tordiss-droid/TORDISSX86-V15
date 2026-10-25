import os
from datetime import datetime

folder = "reports"

os.system("clear")

print("""
====================================
 TORDISSX86 v3.3
 INVESTIGATION TIMELINE
====================================
""")

if not os.path.exists(folder):
    print("No reports folder.")
else:
    files = []

    for name in os.listdir(folder):
        path = os.path.join(folder, name)

        if os.path.isfile(path):
            timestamp = os.path.getmtime(path)
            date = datetime.fromtimestamp(timestamp)
            files.append((timestamp, name, date))

    files.sort(reverse=True)

    print("TOTAL EVENTS:", len(files))

    for timestamp, name, date in files:
        print(f"\n[{date.strftime('%Y-%m-%d %H:%M:%S')}]")
        print("REPORT:", name)

input("\nPress ENTER to exit...")
