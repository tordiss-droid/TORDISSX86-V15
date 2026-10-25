import os
import re
from collections import Counter
from datetime import datetime

LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

def analyze_log():
    path = input("\nEnter log file path: ").strip()
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        print("ERROR: Log file not found.")
        return

    counts = Counter()
    errors = []

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            for line_number, line in enumerate(file, 1):
                text = line.strip()
                upper = text.upper()

                if "ERROR" in upper or "FAILED" in upper:
                    counts["ERROR"] += 1
                    errors.append((line_number, text))
                elif "WARNING" in upper or "WARN" in upper:
                    counts["WARNING"] += 1
                elif "INFO" in upper:
                    counts["INFO"] += 1

    except OSError as error:
        print("ERROR:", error)
        return

    print("\n" + "=" * 45)
    print("TORDISSX86 LOG ANALYZER")
    print("=" * 45)
    print("File:", os.path.basename(path))
    print("Error entries:", counts["ERROR"])
    print("Warning entries:", counts["WARNING"])
    print("Info entries:", counts["INFO"])
    print("Total lines:", sum(counts.values()))

    print("\nERROR DETAILS:")

    if errors:
        for number, message in errors[:20]:
            print(f"Line {number}: {message}")
    else:
        print("No errors detected.")

    if len(errors) > 20:
        print(f"...and {len(errors) - 20} more errors.")

    print("=" * 45)

    save = input("\nSave analysis report? (y/n): ").lower()

    if save == "y":
        filename = datetime.now().strftime(
            "LOG_REPORT_%Y%m%d_%H%M%S.txt"
        )
        output = os.path.join(LOG_FOLDER, filename)

        with open(output, "w", encoding="utf-8") as file:
            file.write("TORDISSX86 LOG ANALYSIS REPORT\n")
            file.write(f"Source: {os.path.basename(path)}\n")
            file.write(f"Errors: {counts['ERROR']}\n")
            file.write(f"Warnings: {counts['WARNING']}\n")
            file.write(f"Info: {counts['INFO']}\n\n")

            for number, message in errors:
                file.write(f"Line {number}: {message}\n")

        print("Report saved:", output)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 LOG ANALYZER v4.4")
        print("=" * 45)
        print("[1] Analyze Log File")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            analyze_log()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
