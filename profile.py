import os
from datetime import datetime

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

os.system("clear")

print(RED + """
================================
      TORDISSX86
      PROFILE ANALYSIS
================================
""" + RESET)

username = input(GREEN + "Enter public username: " + RESET)

if not username.strip():
    print("Username cannot be empty")
else:
    print("\n[+] Analysis started...")
    print("[+] Username:", username)
    print("[+] Checking public profile URL...")

    url = "https://www.instagram.com/" + username.strip().lstrip("@")

    print("[+] Public URL:", url)

    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime(
        "reports/profile_%Y%m%d_%H%M%S.txt"
    )

    with open(filename, "w") as f:
        f.write("TORDISSX86 PROFILE ANALYSIS\n")
        f.write("Username: " + username + "\n")
        f.write("Public URL: " + url + "\n")
        f.write("Date: " + str(datetime.now()) + "\n")
        f.write("Status: URL generated; profile not verified.\n")

    print(GREEN + "\n[+] Report saved: " + filename + RESET)

input("\nPress ENTER to exit...")
