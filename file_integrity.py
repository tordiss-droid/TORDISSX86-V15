import os
import json
import hashlib
from datetime import datetime

REPORT_DIR = "integrity_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

BASELINE_FILE = os.path.join(REPORT_DIR, "file_baselines.json")

def calculate_hash(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

def load_baselines():
    if not os.path.exists(BASELINE_FILE):
        return {}

    try:
        with open(BASELINE_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return {}

def save_baselines(data):
    with open(BASELINE_FILE, "w") as file:
        json.dump(data, file, indent=4)

def inspect_file():
    path = input("Enter file path: ").strip()

    if not os.path.isfile(path):
        print("File not found.")
        return

    try:
        digest = calculate_hash(path)
        print("\nFILE INTEGRITY RESULT")
        print("=" * 40)
        print("File:", path)
        print("SHA-256:", digest)

        baselines = load_baselines()

        if path in baselines:
            if baselines[path]["sha256"] == digest:
                print("Status: UNCHANGED")
            else:
                print("Status: MODIFIED")
        else:
            print("Status: NO BASELINE")

        report = {
            "file": path,
            "sha256": digest,
            "date": datetime.now().isoformat()
        }

        filename = datetime.now().strftime("FILE_%Y%m%d_%H%M%S.json")

        with open(os.path.join(REPORT_DIR, filename), "w") as file:
            json.dump(report, file, indent=4)

    except PermissionError:
        print("Permission denied.")
    except Exception as error:
        print("Error:", error)

def create_baseline():
    path = input("Enter file path: ").strip()

    if not os.path.isfile(path):
        print("File not found.")
        return

    try:
        digest = calculate_hash(path)
        baselines = load_baselines()

        baselines[path] = {
            "sha256": digest,
            "created": datetime.now().isoformat()
        }

        save_baselines(baselines)
        print("\nBaseline saved successfully.")
        print("SHA-256:", digest)

    except Exception as error:
        print("Error:", error)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 v5.2")
        print("FILE INTEGRITY SCANNER")
        print("=" * 45)
        print("[1] Inspect File")
        print("[2] Create Baseline")
        print("[3] View Baselines")
        print("[0] Back")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            inspect_file()
        elif choice == "2":
            create_baseline()
        elif choice == "3":
            print(json.dumps(load_baselines(), indent=4))
        elif choice == "0":
            break
        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
