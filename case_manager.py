import os
import re
from datetime import datetime

FOLDER = "cases"
os.makedirs(FOLDER, exist_ok=True)

def create_case():
    title = input("\nCase title: ").strip()
    if not title:
        print("Title haiwezi kuwa tupu.")
        return

    notes = input("Investigation notes: ").strip()
    case_id = datetime.now().strftime("CASE_%Y%m%d_%H%M%S")
    filename = os.path.join(FOLDER, case_id + ".txt")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("TORDISSX86 INVESTIGATION CASE\n")
        file.write(f"Case ID: {case_id}\n")
        file.write(f"Title: {title}\n")
        file.write(f"Created: {datetime.now()}\n")
        file.write("\nNOTES:\n")
        file.write(notes + "\n")

    print(f"\nCase saved: {case_id}")

def list_cases():
    files = sorted(os.listdir(FOLDER))
    files = [f for f in files if f.endswith(".txt")]

    if not files:
        print("\nHakuna case iliyohifadhiwa.")
        return

    for i, name in enumerate(files, 1):
        print(f"[{i}] {name}")

    choice = input("\nChagua namba ya kusoma (0 kurudi): ")

    if choice == "0":
        return

    if choice.isdigit() and 1 <= int(choice) <= len(files):
        path = os.path.join(FOLDER, files[int(choice) - 1])
        with open(path, "r", encoding="utf-8") as file:
            print("\n" + file.read())
    else:
        print("Chaguo si sahihi.")

while True:
    os.system("clear")
    print("=" * 40)
    print(" TORDISSX86 CASE MANAGER v3.6")
    print("=" * 40)
    print("[1] CREATE NEW CASE")
    print("[2] VIEW SAVED CASES")
    print("[0] BACK")
    print("=" * 40)

    choice = input("Select: ").strip()

    if choice == "1":
        create_case()
        input("\nENTER kurudi...")
    elif choice == "2":
        list_cases()
        input("\nENTER kurudi...")
    elif choice == "0":
        break
    else:
        print("Chaguo si sahihi.")
        input("ENTER...")
