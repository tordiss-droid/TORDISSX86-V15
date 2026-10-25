import os
import json
import hashlib
from datetime import datetime

FOLDER = "integrity_reports"
DATABASE = os.path.join(FOLDER, "baseline.json")

os.makedirs(FOLDER, exist_ok=True)

def calculate_hash(path):
    sha = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha.update(chunk)

    return sha.hexdigest()

def load_database():
    if not os.path.isfile(DATABASE):
        return {}

    try:
        with open(DATABASE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}

def save_database(data):
    temp = DATABASE + ".tmp"

    with open(temp, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    os.replace(temp, DATABASE)

def inspect_file():
    path = os.path.abspath(
        os.path.expanduser(input("\nEnter file path: ").strip())
    )

    if not os.path.isfile(path):
        print("ERROR: File not found.")
        return

    current_hash = calculate_hash(path)
    database = load_database()

    print("\nFile:", os.path.basename(path))
    print("SHA-256:", current_hash)

    if path in database:
        previous = database[path]["sha256"]

        if previous == current_hash:
            print("Integrity Status: UNCHANGED")
        else:
            print("Integrity Status: CHANGED")
            print("Previous hash:", previous)
    else:
        print("Integrity Status: FIRST CHECK")

    database[path] = {
        "sha256": current_hash,
        "checked_at": datetime.now().isoformat(timespec="seconds")
    }

    save_database(database)
    print("\nBaseline updated successfully.")

def compare_files():
    first = os.path.expanduser(input("\nFirst file path: ").strip())
    second = os.path.expanduser(input("Second file path: ").strip())

    if not os.path.isfile(first) or not os.path.isfile(second):
        print("ERROR: One or both files were not found.")
        return

    hash1 = calculate_hash(first)
    hash2 = calculate_hash(second)

    print("\nFirst SHA-256:", hash1)
    print("Second SHA-256:", hash2)

    if hash1 == hash2:
        print("\nRESULT: FILES ARE IDENTICAL")
    else:
        print("\nRESULT: FILES ARE DIFFERENT")

def view_history():
    database = load_database()

    if not database:
        print("\nNo integrity records found.")
        return

    for path, record in database.items():
        print("\nFile:", path)
        print("SHA-256:", record["sha256"])
        print("Checked:", record["checked_at"])

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 FILE INTEGRITY MONITOR v4.3")
        print("=" * 45)
        print("[1] Inspect File Integrity")
        print("[2] Compare Two Files")
        print("[3] View Integrity History")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            inspect_file()
            input("\nPress ENTER to continue...")
        elif choice == "2":
            compare_files()
            input("\nPress ENTER to continue...")
        elif choice == "3":
            view_history()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
