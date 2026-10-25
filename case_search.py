import os

FOLDER = "cases"

def search_cases():
    if not os.path.isdir(FOLDER):
        print("\nERROR: Cases folder not found.")
        return

    keyword = input("\nEnter search keyword: ").strip().lower()

    if not keyword:
        print("ERROR: Search keyword cannot be empty.")
        return

    found = 0

    for filename in sorted(os.listdir(FOLDER)):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(FOLDER, filename)

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            if keyword in content.lower():
                found += 1
                print("\n" + "=" * 45)
                print("MATCH FOUND:", filename)
                print("=" * 45)
                print(content)

        except OSError as error:
            print("ERROR:", error)

    if found == 0:
        print("\nNo matching cases found.")

    print(f"\nTotal matches: {found}")

while True:
    os.system("clear")
    print("=" * 45)
    print("       TORDISSX86 CASE SEARCH")
    print("=" * 45)
    print("[1] Search Investigation Cases")
    print("[0] Back to Dashboard")
    print("=" * 45)

    choice = input("Select option: ").strip()

    if choice == "1":
        search_cases()
        input("\nPress ENTER to continue...")
    elif choice == "0":
        break
    else:
        print("Invalid option.")
        input("Press ENTER...")
