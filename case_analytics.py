import os
from datetime import datetime, date

FOLDER = "cases"

def analyze_cases():
    os.makedirs(FOLDER, exist_ok=True)

    files = [
        f for f in os.listdir(FOLDER)
        if f.endswith(".txt")
    ]

    today = date.today()
    current_month = today.strftime("%Y-%m")

    today_count = 0
    month_count = 0
    valid_dates = []

    for filename in files:
        path = os.path.join(FOLDER, filename)

        try:
            modified = datetime.fromtimestamp(
                os.path.getmtime(path)
            )

            if modified.date() == today:
                today_count += 1

            if modified.strftime("%Y-%m") == current_month:
                month_count += 1

            valid_dates.append(modified)

        except OSError:
            continue

    latest = max(valid_dates) if valid_dates else None

    print("\n" + "=" * 45)
    print("       TORDISSX86 CASE ANALYTICS")
    print("=" * 45)
    print(f"Total Cases       : {len(files)}")
    print(f"Created Today     : {today_count}")
    print(f"Modified This Month: {month_count}")

    if latest:
        print("Latest Case Date  :", latest.strftime("%Y-%m-%d %H:%M"))
    else:
        print("Latest Case       : No cases found")

    print("=" * 45)

while True:
    os.system("clear")
    print("TORDISSX86 CASE ANALYTICS")
    print("[1] Generate Analytics")
    print("[0] Back to Dashboard")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        analyze_cases()
        input("\nPress ENTER to continue...")
    elif choice == "0":
        break
    else:
        print("Invalid option.")
        input("Press ENTER...")
