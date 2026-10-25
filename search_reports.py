import os

folder = "reports"

os.system("clear")
print("""
================================
 TORDISSX86 REPORT SEARCH ENGINE
================================
""")

keyword = input("Enter search keyword: ").lower()

if not os.path.exists(folder):
    print("Reports folder not found.")
else:
    found = 0

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if os.path.isfile(path):
            with open(path, errors="ignore") as f:
                content = f.read()

            if keyword in content.lower():
                print("\n[+] MATCH:", file)
                found += 1

    print("\nTOTAL MATCHES:", found)

input("\nPress ENTER...")
