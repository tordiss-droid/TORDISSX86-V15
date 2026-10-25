import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"

MODULES = {
    "1": ("Advanced OSINT Intelligence", "advanced_osint.py"),
    "2": ("Profile Analysis", "profile.py"),
    "3": ("Username OSINT", "username.py"),
    "4": ("Public Posts Research", "posts.py"),
    "5": ("Image Metadata", "image_meta.py"),
    "6": ("Investigation Reports", "reports.py"),
    "7": ("Master Search", "master_search.py"),
    "8": ("Domain Intelligence", "domain_intel.py"),
    "9": ("DNS Intelligence", "dns_intel.py"),
    "10": ("URL Analyzer", "url_analyzer.py"),
    "11": ("Digital Forensics", "forensics.py"),
    "12": ("File Integrity", "file_integrity.py"),
    "13": ("Integrity Monitor", "integrity_monitor.py"),
    "14": ("Evidence Vault", "evidence_vault.py"),
    "15": ("Case Manager", "case_manager.py"),
    "16": ("Case Analytics", "case_analytics.py"),
    "17": ("Network Diagnostics", "network_diagnostics.py"),
    "18": ("Network Security", "network_security.py"),
    "19": ("Security Audit", "security_audit.py"),
    "20": ("Log Analyzer", "log_analyzer.py"),
    "21": ("Password Lab", "password_lab.py"),
    "22": ("Password Generator", "password_generator.py"),
    "23": ("Encryption Lab", "encryption_lab.py"),
    "24": ("System Information", "system_info.py"),
    "25": ("System Health", "system_health.py"),
    "26": ("Learning Center", "learning_center.py"),
    "27": ("V11 Case Dashboard", "v11_dashboard.py"),
    "28": ("Diagnostics", "diagnostics.py"),
    "32": ("Unified Reports Center", "unified_reports.py"),
}

def launch(file):
    path = ROOT / file

    if not path.is_file():
        print(RED + f"\nModule missing: {file}" + RESET)
        input("\nENTER...")
        return

    print(CYAN + f"\nLaunching {file}..." + RESET)

    try:
        subprocess.run([sys.executable, str(path)], cwd=ROOT)
    except KeyboardInterrupt:
        print("\nModule stopped.")
    except Exception as error:
        print(RED + str(error) + RESET)

    input("\nPress ENTER to return...")

def dashboard():
    while True:
        os.system("clear")

        print(CYAN + """
╔══════════════════════════════════════╗
║            TORDISSX86                ║
║       UNIFIED INTELLIGENCE LAB       ║
║               V12.0                  ║
╚══════════════════════════════════════╝
""" + RESET)

        print(GREEN + "========== INTELLIGENCE MODULES ==========" + RESET)

        for number, (name, file) in MODULES.items():
            status = "READY" if (ROOT / file).is_file() else "MISSING"
            print(f"[{number:>2}] {name:<29} [{status}]")

        print("\n" + CYAN + "========== WEB & PROJECT ==========" + RESET)
        print("[29] Open Web Panel")
        print("[30] Project Backup")
        print("[31] Project Inventory")
        print("[33] V12 Integration Center")
        print("[0]  EXIT")

        choice = input("\nTORDISSX86 >> ").strip()

        if choice in MODULES:
            launch(MODULES[choice][1])

        elif choice == "29":
            print("\nStart the existing web panel using its configured port.")
            print("Run: python web_panel.py")
            input("\nENTER...")

        elif choice == "30":
            name = "TORDISSX86_BACKUP_" + __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S") + ".tar.gz"
            subprocess.run([
                "tar", "-czf", str(ROOT / "backups" / name),
                "--exclude=__pycache__", "--exclude=*.pyc", "."
            ], cwd=ROOT)
            print("\nBackup saved in backups/" + name)
            input("\nENTER...")

        elif choice == "31":
            files = sorted(ROOT.glob("*.py"))
            print("\nPYTHON MODULES:", len(files))
            for file in files:
                print(" -", file.name)
            input("\nENTER...")


        elif choice == "33":
            print("\\nV12 INTEGRATION CENTER")
            print("Start Web Panel: python web_panel.py")
            print("Open: http://127.0.0.1:5055/v12/integrations/")
            input("\\nENTER...")

        elif choice == "0":
            print(GREEN + "\nTORDISSX86 CLOSED." + RESET)
            break

        else:
            input("Invalid option. ENTER...")

if __name__ == "__main__":
    dashboard()
