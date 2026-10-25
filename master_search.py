import os
import sys
import subprocess

TOOLS = {
    "1": ("Username OSINT", "username.py"),
    "2": ("Public Profile Analysis", "profile.py"),
    "3": ("Public Posts Research", "posts.py"),
    "4": ("Search Reports", "search_reports.py"),
    "5": ("Investigation Timeline", "timeline.py"),
    "6": ("Export Reports", "export.py")
}

while True:
    os.system("clear")
    print("=" * 42)
    print("       TORDISSX86 OSINT MASTER SEARCH")
    print("=" * 42)

    for key, (name, filename) in TOOLS.items():
        status = "ONLINE" if os.path.isfile(filename) else "MISSING"
        print(f"[{key}] {name} [{status}]")

    print("[0] BACK TO DASHBOARD")
    print("=" * 42)

    choice = input("Select tool: ").strip()

    if choice == "0":
        break

    if choice in TOOLS:
        name, filename = TOOLS[choice]

        if os.path.isfile(filename):
            subprocess.run([sys.executable, filename])
        else:
            print(f"\nERROR: {filename} haipo!")
            input("Bonyeza ENTER...")
    else:
        print("Chaguo si sahihi!")
        input("Bonyeza ENTER...")
