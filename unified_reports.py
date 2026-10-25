import os
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

REPORT_DIRS = [
    "reports",
    "dns_reports",
    "domain_reports",
    "network_reports",
    "forensics_reports",
    "security_reports",
    "learning_reports",
    "exports"
]

def collect_reports():
    results = []

    for folder in REPORT_DIRS:
        directory = ROOT / folder

        if not directory.exists():
            continue

        for file in directory.rglob("*"):
            if file.is_file() and file.name != "index.json":
                try:
                    stat = file.stat()
                    results.append({
                        "name": file.name,
                        "folder": folder,
                        "path": str(file.relative_to(ROOT)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(
                            stat.st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })
                except OSError:
                    continue

    return sorted(results, key=lambda x: x["modified"], reverse=True)

def view_reports():
    reports = collect_reports()

    print("\n========== REPORT CENTER ==========")
    print("TOTAL REPORTS:", len(reports))

    if not reports:
        print("No reports found.")
        return

    for i, item in enumerate(reports, 1):
        print(f"\n[{i}] {item['name']}")
        print("Folder:", item["folder"])
        print("Size:", item["size"], "bytes")
        print("Modified:", item["modified"])

def search_reports():
    reports = collect_reports()
    query = input("Search report name: ").lower()

    matches = [
        item for item in reports
        if query in item["name"].lower()
        or query in item["folder"].lower()
    ]

    print("\nSEARCH RESULTS:", len(matches))

    for item in matches:
        print(item["path"])

def export_index():
    reports = collect_reports()
    output = ROOT / "reports" / "unified_report_index.json"

    with output.open("w", encoding="utf-8") as f:
        json.dump(reports, f, indent=4)

    print("\nIndex saved:", output.relative_to(ROOT))

def main():
    while True:
        print("""
================================
 TORDISSX86 UNIFIED REPORTS
================================
[1] View all reports
[2] Search reports
[3] Export report index
[0] Back / Exit
""")

        choice = input("REPORT CENTER >> ").strip()

        if choice == "1":
            view_reports()
        elif choice == "2":
            search_reports()
        elif choice == "3":
            export_index()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
