import os
import ast
import sys
from datetime import datetime

EXPECTED_FILES = [
    "dashboard.py",
    "profile.py",
    "username.py",
    "posts.py",
    "image_meta.py",
    "reports.py",
    "search_reports.py",
    "export.py",
    "timeline.py",
    "diagnostics.py",
    "master_search.py",
    "case_manager.py",
    "case_search.py",
    "case_analytics.py",
    "evidence_vault.py",
    "forensics.py",
    "network_diagnostics.py",
    "system_info.py",
    "integrity_monitor.py",
    "log_analyzer.py"
]

EXPECTED_FOLDERS = [
    "reports",
    "cases",
    "evidence",
    "forensics_reports",
    "network_reports",
    "integrity_reports",
    "logs"
]

def audit_files():
    results = {
        "online": [],
        "missing": [],
        "syntax_errors": [],
        "empty": []
    }

    for filename in EXPECTED_FILES:
        if not os.path.isfile(filename):
            results["missing"].append(filename)
            continue

        if os.path.getsize(filename) == 0:
            results["empty"].append(filename)
            continue

        try:
            with open(filename, "r", encoding="utf-8") as file:
                source = file.read()

            ast.parse(source, filename=filename)
            results["online"].append(filename)

        except SyntaxError as error:
            results["syntax_errors"].append(
                f"{filename}: Line {error.lineno}: {error.msg}"
            )
        except OSError as error:
            results["syntax_errors"].append(
                f"{filename}: {error}"
            )

    return results

def audit_folders():
    available = []
    missing = []

    for folder in EXPECTED_FOLDERS:
        if os.path.isdir(folder):
            available.append(folder)
        else:
            missing.append(folder)

    return available, missing

def run_audit():
    print("\nRunning project security audit...")

    files = audit_files()
    available, missing = audit_folders()

    print("\n" + "=" * 48)
    print("       TORDISSX86 SECURITY AUDIT")
    print("=" * 48)

    print("\nPYTHON MODULES")
    print("Valid files:", len(files["online"]))
    print("Missing files:", len(files["missing"]))
    print("Empty files:", len(files["empty"]))
    print("Syntax errors:", len(files["syntax_errors"]))

    print("\nPROJECT FOLDERS")
    print("Available:", len(available))
    print("Missing:", len(missing))

    if files["missing"]:
        print("\nMISSING MODULES:")
        for item in files["missing"]:
            print("-", item)

    if files["empty"]:
        print("\nEMPTY MODULES:")
        for item in files["empty"]:
            print("-", item)

    if files["syntax_errors"]:
        print("\nSYNTAX ERRORS:")
        for item in files["syntax_errors"]:
            print("-", item)

    if missing:
        print("\nMISSING FOLDERS:")
        for item in missing:
            print("-", item)

    total_problems = (
        len(files["missing"])
        + len(files["empty"])
        + len(files["syntax_errors"])
        + len(missing)
    )

    print("\n" + "=" * 48)

    if total_problems == 0:
        print("PROJECT STATUS: HEALTHY")
    else:
        print("PROJECT STATUS: ISSUES DETECTED")

    print("Total issues:", total_problems)
    print("=" * 48)

    save = input("\nSave audit report? (y/n): ").strip().lower()

    if save == "y":
        os.makedirs("audit_reports", exist_ok=True)

        filename = datetime.now().strftime(
            "AUDIT_%Y%m%d_%H%M%S.txt"
        )

        path = os.path.join("audit_reports", filename)

        with open(path, "w", encoding="utf-8") as file:
            file.write("TORDISSX86 SECURITY AUDIT\n")
            file.write(f"Date: {datetime.now()}\n")
            file.write(f"Valid modules: {len(files['online'])}\n")
            file.write(f"Missing modules: {len(files['missing'])}\n")
            file.write(f"Empty modules: {len(files['empty'])}\n")
            file.write(f"Syntax errors: {len(files['syntax_errors'])}\n")
            file.write(f"Available folders: {len(available)}\n")
            file.write(f"Missing folders: {len(missing)}\n")
            file.write(f"Total issues: {total_problems}\n")

            for category, items in files.items():
                file.write(f"\n{category.upper()}:\n")
                for item in items:
                    file.write(str(item) + "\n")

            file.write("\nMISSING FOLDERS:\n")
            for item in missing:
                file.write(item + "\n")

        print("Report saved:", path)

def main():
    while True:
        os.system("clear")
        print("=" * 48)
        print("TORDISSX86 SECURITY AUDIT CENTER v4.5")
        print("=" * 48)
        print("[1] Run Project Audit")
        print("[0] Back to Dashboard")
        print("=" * 48)

        choice = input("Select option: ").strip()

        if choice == "1":
            run_audit()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
