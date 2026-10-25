import os

folder = "reports"
os.makedirs(folder, exist_ok=True)

while True:
    os.system("clear")
    print("""
================================
       TORDISSX86
       INVESTIGATION REPORTS
================================
""")

    files = sorted(os.listdir(folder))

    print("TOTAL REPORTS:", len(files))

    for i, file in enumerate(files, 1):
        print(f"[{i}] {file}")

    print("""
[1] VIEW REPORT
[0] BACK
""")

    choice = input("REPORTS >> ")

    if choice == "0":
        break

    elif choice == "1":
        try:
            n = int(input("Report number: "))
            if 1 <= n <= len(files):
                with open(os.path.join(folder, files[n-1]),
                          encoding="utf-8") as f:
                    print("\n", f.read())
            else:
                print("Invalid number")
        except ValueError:
            print("Enter a valid number")

        input("\nPress ENTER...")
