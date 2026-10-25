import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

os.system("clear")

print(RED + """
================================
      TORDISSX86
      IMAGE METADATA
================================
""" + RESET)

path = input("Enter image file path: ").strip()

try:
    with Image.open(path) as img:
        print("\n[+] FORMAT:", img.format)
        print("[+] DIMENSIONS:", img.size)
        print("[+] MODE:", img.mode)
        print("[+] SIZE:", os.path.getsize(path), "bytes")

        exif = img.getexif()

        print("\n[+] EXIF INFORMATION")

        metadata = []

        for tag, value in exif.items():
            name = TAGS.get(tag, str(tag))
            print(name, ":", value)
            metadata.append(f"{name}: {value}")

        if not metadata:
            print("No EXIF metadata found.")

        os.makedirs("reports", exist_ok=True)

        filename = datetime.now().strftime(
            "reports/image_%Y%m%d_%H%M%S.txt"
        )

        with open(filename, "w") as f:
            f.write("TORDISSX86 IMAGE METADATA\n")
            f.write(f"File: {path}\n")
            f.write(f"Format: {img.format}\n")
            f.write(f"Dimensions: {img.size}\n")
            f.write("\n".join(metadata))

        print(GREEN + "\n[+] REPORT SAVED: " + filename + RESET)

except Exception as e:
    print(RED + "\n[!] ERROR: " + str(e) + RESET)

input("\nPress ENTER to exit...")
