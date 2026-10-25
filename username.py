import os
from datetime import datetime
from urllib.parse import quote

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

os.system("clear")

print(RED + """
================================
       TORDISSX86
       USERNAME OSINT
================================
""" + RESET)

username = input("Enter username: ").strip().lstrip("@")

if not username:
    print("Invalid username")
else:
    sites = {
        "Instagram": "https://www.instagram.com/",
        "GitHub": "https://github.com/",
        "Reddit": "https://www.reddit.com/user/",
        "TikTok": "https://www.tiktok.com/@"
    }

    print("\nUSERNAME:", username)
    print("\nPUBLIC PROFILE LINKS\n")

    results = []

    for site, base in sites.items():
        url = base + quote(username)
        print(f"[+] {site}: {url}")
        results.append(f"{site}: {url}")

    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime(
        "reports/username_%Y%m%d_%H%M%S.txt"
    )

    with open(filename, "w") as f:
        f.write("TORDISSX86 USERNAME OSINT\n")
        f.write("Username: " + username + "\n")
        f.write("\n".join(results))
        f.write("\n\nStatus: Links generated, not verified.")

    print(GREEN + "\n[+] Report saved: " + filename + RESET)

input("\nPress ENTER to exit...")
