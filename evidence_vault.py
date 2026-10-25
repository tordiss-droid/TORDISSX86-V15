import os
import json
from datetime import datetime

FOLDER = "evidence"
DATABASE = os.path.join(FOLDER, "evidence_records.json")

os.makedirs(FOLDER, exist_ok=True)

def load_records():
    if not os.path.isfile(DATABASE):
        return []

    try:
        with open(DATABASE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        print("ERROR: Evidence database could not be read.")
        return []

def save_records(records):
    temp_file = DATABASE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    os.replace(temp_file, DATABASE)

def register_evidence():
    print("\n=== REGISTER NEW EVIDENCE ===")

    title = input("Evidence title: ").strip()
    filename = input("Evidence filename: ").strip()
    description = input("Evidence description: ").strip()

    if not title or not filename:
        print("ERROR: Title and filename are required.")
        return

    record = {
        "evidence_id": datetime.now().strftime("EV_%Y%m%d_%H%M%S_%f"),
        "title": title,
        "filename": filename,
        "description": description,
        "registered_at": datetime.now().isoformat(timespec="seconds")
    }

    records = load_records()
    records.append(record)
    save_records(records)

    print("\nEvidence record saved successfully.")
    print("Evidence ID:", record["evidence_id"])

def view_evidence():
    records = load_records()

    if not records:
        print("\nNo evidence records found.")
        return

    for record in records:
        print("\n" + "=" * 40)
        print("Evidence ID:", record.get("evidence_id"))
        print("Title:", record.get("title"))
        print("Filename:", record.get("filename"))
        print("Description:", record.get("description"))
        print("Registered:", record.get("registered_at"))

def main():
    while True:
        os.system("clear")
        print("=" * 42)
        print("       TORDISSX86 EVIDENCE VAULT")
        print("=" * 42)
        print("[1] Register Evidence")
        print("[2] View Evidence Records")
        print("[0] Back to Dashboard")
        print("=" * 42)

        choice = input("Select option: ").strip()

        if choice == "1":
            register_evidence()
            input("\nPress ENTER to continue...")
        elif choice == "2":
            view_evidence()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
