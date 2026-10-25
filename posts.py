import os
from datetime import datetime
from urllib.parse import urlparse

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

os.system("clear")

print(RED + """
====================================
       TORDISSX86
       PUBLIC POSTS RESEARCH
====================================
""" + RESET)

url = input("Instagram Post URL: ").strip()

parsed = urlparse(url)

if parsed.scheme not in ("https", "http") or parsed.hostname not in (
    "instagram.com", "www.instagram.com"
):
    print(RED + "Invalid Instagram URL!" + RESET)

else:
    note = input("Investigation notes: ")

    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime(
        "reports/post_%Y%m%d_%H%M%S.txt"
    )

    with open(filename, "w") as f:
        f.write("TORDISSX86 PUBLIC POSTS RESEARCH\n")
        f.write("Date: " + str(datetime.now()) + "\n")
        f.write("Post URL: " + url + "\n")
        f.write("Notes: " + note + "\n")
        f.write("Status: URL recorded; content not independently verified.\n")

    print(GREEN + "\n[+] Research saved!" + RESET)
    print("[+] Report:", filename)

input("\nPress ENTER to exit...")
