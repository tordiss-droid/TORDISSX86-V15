import os
import sys
import platform
import shutil
import subprocess

def get_property(name):
    try:
        result = subprocess.run(
            ["getprop", name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() or "Unavailable"
    except (OSError, subprocess.TimeoutExpired):
        return "Unavailable"

def show_information():
    total, used, free = shutil.disk_usage(os.path.expanduser("~"))

    info = {
        "Device Model": get_property("ro.product.model"),
        "Manufacturer": get_property("ro.product.manufacturer"),
        "Android Version": get_property("ro.build.version.release"),
        "SDK Version": get_property("ro.build.version.sdk"),
        "Kernel": platform.release(),
        "Architecture": platform.machine(),
        "Python Version": platform.python_version(),
        "Operating System": platform.system(),
        "Storage Total (GB)": round(total / (1024 ** 3), 2),
        "Storage Used (GB)": round(used / (1024 ** 3), 2),
        "Storage Free (GB)": round(free / (1024 ** 3), 2)
    }

    print("\n" + "=" * 45)
    print("TORDISSX86 SYSTEM INFORMATION")
    print("=" * 45)

    for key, value in info.items():
        print(f"{key}: {value}")

    print("=" * 45)

def main():
    while True:
        os.system("clear")
        print("TORDISSX86 SYSTEM INFORMATION CENTER")
        print("[1] View Device Information")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            show_information()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
