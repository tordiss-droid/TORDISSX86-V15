import os
import sys
import platform
import shutil
import subprocess
from datetime import datetime

def get_android_info():
    try:
        result = subprocess.run(
            ["getprop", "ro.build.version.release"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() or "Unavailable"
    except Exception:
        return "Unavailable"

def get_ram_info():
    try:
        with open("/proc/meminfo", "r") as file:
            lines = file.readlines()

        info = {}

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                if parts[0] in ("MemTotal:", "MemAvailable:"):
                    info[parts[0]] = int(parts[1]) // 1024

        total = info.get("MemTotal:", 0)
        available = info.get("MemAvailable:", 0)

        print("Total RAM:", total, "MB")
        print("Available RAM:", available, "MB")

    except Exception:
        print("RAM information unavailable.")

def get_storage_info():
    total, used, free = shutil.disk_usage(os.path.expanduser("~"))

    print("Total Storage:", round(total / (1024 ** 3), 2), "GB")
    print("Used Storage:", round(used / (1024 ** 3), 2), "GB")
    print("Free Storage:", round(free / (1024 ** 3), 2), "GB")

def check_project():
    print("\nPROJECT MODULE STATUS")
    print("=" * 40)

    modules = [
        "dashboard.py",
        "profile.py",
        "username.py",
        "posts.py",
        "image_meta.py",
        "reports.py",
        "master_search.py",
        "case_manager.py",
        "forensics.py",
        "network_diagnostics.py",
        "system_info.py",
        "integrity_monitor.py",
        "log_analyzer.py",
        "security_audit.py",
        "password_lab.py",
        "password_generator.py",
        "encryption_lab.py",
        "network_security.py",
        "learning_center.py",
        "system_health.py"
    ]

    for module in modules:
        status = "AVAILABLE" if os.path.isfile(module) else "MISSING"
        print(f"{module:<28} {status}")

def main():
    while True:
        os.system("clear")

        print("=" * 45)
        print("TORDISSX86 v5.1")
        print("SYSTEM HEALTH MONITOR")
        print("=" * 45)
        print("[1] Device Information")
        print("[2] RAM Information")
        print("[3] Storage Information")
        print("[4] Project Module Status")
        print("[5] Full System Report")
        print("[0] Back")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            print("\nDEVICE INFORMATION")
            print("Android:", get_android_info())
            print("Python:", sys.version.split()[0])
            print("Architecture:", platform.machine())
            print("Platform:", platform.platform())
            print("Processor:", platform.processor() or "Unavailable")

        elif choice == "2":
            get_ram_info()

        elif choice == "3":
            get_storage_info()

        elif choice == "4":
            check_project()

        elif choice == "5":
            print("\nFULL SYSTEM REPORT")
            print("Date:", datetime.now().isoformat())
            print("Android:", get_android_info())
            print("Python:", sys.version.split()[0])
            print("Architecture:", platform.machine())
            get_ram_info()
            print()
            get_storage_info()
            check_project()

        elif choice == "0":
            break

        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
