import json
import hashlib
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DATA = BASE / "v11_data"
DATA.mkdir(exist_ok=True)

EVIDENCE = DATA / "evidence.json"
TIMELINE = DATA / "timeline.json"
LOGS = DATA / "activity_logs.json"


def load(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save(path, data):
    path.write_text(json.dumps(data, indent=4))


def log(action):
    data = load(LOGS)
    data.append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "action": action
    })
    save(LOGS, data)


def cases():
    data = load(BASE / "cases" / "cases.json")
    if isinstance(data, dict):
        for key in ("cases", "data", "records"):
            if isinstance(data.get(key), list):
                return data[key]
        return []
    return data if isinstance(data, list) else []


def case_name(item):
    if isinstance(item, dict):
        return str(item.get("id") or item.get("case_id") or item.get("name") or "Unnamed")
    return str(item)


def choose_case():
    data = cases()
    if not data:
        print("No cases found. Create a case in Advanced OSINT first.")
        return None

    for i, item in enumerate(data, 1):
        print(f"{i}. {case_name(item)}")

    try:
        return data[int(input("Select case: ")) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def dashboard():
    print("\nTORDISSX86 MASTER DASHBOARD")
    print("Cases:", len(cases()))
    print("Evidence:", len(load(EVIDENCE)))
    print("Timeline events:", len(load(TIMELINE)))
    print("Activity logs:", len(load(LOGS)))


def add_timeline():
    case = choose_case()
    if case is None:
        return

    event = input("Event description: ").strip()
    if event:
        data = load(TIMELINE)
        data.append({
            "case": case_name(case),
            "time": datetime.now().isoformat(timespec="seconds"),
            "event": event
        })
        save(TIMELINE, data)
        log("Timeline event added")
        print("Event saved.")


def view_timeline():
    case = choose_case()
    if case is None:
        return

    for item in load(TIMELINE):
        if item["case"] == case_name(case):
            print(item["time"], "-", item["event"])


def register_evidence():
    case = choose_case()
    if case is None:
        return

    path = Path(input("File path: ").strip()).expanduser()

    if not path.is_file():
        print("File not found.")
        return

    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        data = load(EVIDENCE)
        data.append({
            "case": case_name(case),
            "file": str(path.resolve()),
            "sha256": digest
        })
        save(EVIDENCE, data)
        log("Evidence registered")
        print("SHA256:", digest)
    except OSError as error:
        print("File error:", error)


def verify_evidence():
    data = load(EVIDENCE)

    for i, item in enumerate(data, 1):
        print(f"{i}. {item['file']}")

    try:
        item = data[int(input("Select evidence: ")) - 1]
        path = Path(item["file"])

        if not path.is_file():
            print("Original file unavailable.")
            return

        current = hashlib.sha256(path.read_bytes()).hexdigest()
        print("MATCH" if current == item["sha256"] else "MISMATCH")
        log("Evidence verified")
    except (ValueError, IndexError, OSError):
        print("Unable to verify evidence.")


def export_case():
    case = choose_case()
    if case is None:
        return

    name = case_name(case)
    report = {
        "case": case,
        "timeline": [x for x in load(TIMELINE) if x["case"] == name],
        "evidence": [x for x in load(EVIDENCE) if x["case"] == name],
        "exported_at": datetime.now().isoformat()
    }

    folder = DATA / "exports"
    folder.mkdir(exist_ok=True)
    output = folder / "case_export.json"
    save(output, report)
    log("Case exported")
    print("Export saved:", output)


def activity_logs():
    for item in load(LOGS):
        print(item["time"], "-", item["action"])


def main():
    while True:
        print("""
========================================
       TORDISSX86 ADVANCED OSINT v11.0
========================================
1. Master Dashboard
2. Add Timeline Event
3. View Investigation Timeline
4. Register Evidence
5. Verify Evidence SHA256
6. Export Investigation Case
7. View Activity Logs
0. Exit
""")
        choice = input("Select option: ").strip()

        actions = {
            "1": dashboard,
            "2": add_timeline,
            "3": view_timeline,
            "4": register_evidence,
            "5": verify_evidence,
            "6": export_case,
            "7": activity_logs
        }

        if choice == "0":
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("Invalid option.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
