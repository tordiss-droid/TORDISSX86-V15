import os
import hashlib
import json
from datetime import datetime

def calculate_hash(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

def inspect_file():
    path = input("\nEnter image file path: ").strip()
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        print("ERROR: File not found.")
        return

    extension = os.path.splitext(path)[1].lower()
    size = os.path.getsize(path)
    file_hash = calculate_hash(path)

    print("\n" + "=" * 45)
    print("TORDISSX86 DIGITAL FORENSICS")
    print("=" * 45)

    print("Filename:", os.path.basename(path))
    print("Extension:", extension)
    print("File Size:", size, "bytes")
    print("SHA-256:", file_hash)
    print("Modified:", datetime.fromtimestamp(
        os.path.getmtime(path)
    ))

    try:
        from PIL import Image

        with Image.open(path) as image:
            print("Image Format:", image.format)
            print("Dimensions:", image.size)
            print("Color Mode:", image.mode)
            print("EXIF Fields:", len(image.getexif()))

    except ImportError:
        print("Pillow: Not installed")
    except Exception:
        print("Image Metadata: Unable to read")

    print("=" * 45)

    save = input("\nSave forensic report? (y/n): ").lower()

    if save == "y":
        os.makedirs("forensics_reports", exist_ok=True)

        report = {
            "filename": os.path.basename(path),
            "extension": extension,
            "size_bytes": size,
            "sha256": file_hash,
            "modified": datetime.fromtimestamp(
                os.path.getmtime(path)
            ).isoformat()
        }

        name = datetime.now().strftime("FORENSICS_%Y%m%d_%H%M%S.json")
        output = os.path.join("forensics_reports", name)

        with open(output, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print("Report saved:", output)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 DIGITAL FORENSICS v4.0")
        print("=" * 45)
        print("[1] Inspect Image File")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            inspect_file()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
