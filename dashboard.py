import os

RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"

modules = {
    "PROFILE ANALYSIS": "profile.py",
    "USERNAME OSINT": "username.py",
    "PUBLIC POSTS": "posts.py",
    "IMAGE METADATA": "image_meta.py",
    "REPORTS": "reports.py"
}

while True:
    os.system("clear")
    print(RED + """
╔══════════════════════════════════╗
║       TORDISSX86 v3.0            ║
║       CYBER INTELLIGENCE         ║
║       OSINT LAB                  ║
╚══════════════════════════════════╝
""" + RESET)

    print(CYAN + "SYSTEM MODULE STATUS" + RESET)

    for name, file in modules.items():
        status = GREEN + "ONLINE" if os.path.isfile(file) else RED + "MISSING"
        print(f"[+] {name}: {status}{RESET}")

    print("\n" + GREEN + "[1] PROFILE ANALYSIS")
    print("[2] USERNAME OSINT")
    print("[3] PUBLIC POSTS")
    print("[4] IMAGE METADATA")
    print("[5] INVESTIGATION REPORTS")
    print("[9] SYSTEM DIAGNOSTICS")
    print("[10] OSINT MASTER SEARCH")
    print("[11] INVESTIGATION CASE MANAGER")
    print("[12] CASE SEARCH ENGINE")
    print("[13] CASE ANALYTICS")
    print("[14] EVIDENCE VAULT")
    print("[15] DIGITAL FORENSICS TOOLKIT")
    print("[16] NETWORK DIAGNOSTICS")
    print("[17] SYSTEM INFORMATION CENTER")
    print("[18] FILE INTEGRITY MONITOR")
    print("[19] LOG ANALYZER")
    print("[20] SECURITY AUDIT CENTER")
    print("[21] PASSWORD SECURITY LAB")
    print("[22] SECURE PASSWORD GENERATOR")
    print("[23] ENCRYPTION & DECRYPTION LAB")
    print("[24] NETWORK SECURITY LAB")
    print("[25] CYBERSECURITY LEARNING CENTER")
    print("[26] SYSTEM HEALTH MONITOR")
    print("[27] FILE INTEGRITY SCANNER")
    print("[28] GENERAL OSINT SEARCH CENTER")
    print("[29] URL & WEBSITE ANALYZER")
    print("[30] DOMAIN INTELLIGENCE")
    print("[31] DNS INTELLIGENCE ANALYZER")
    print("[0] EXIT" + RESET)

    choice = input("\nTORDISSX86 >> ")

    selected = {
        "33": "v11_dashboard.py",
        "32": "advanced_osint.py",
        "31": "dns_intel.py",
        "30": "domain_intel.py",
        "29": "url_analyzer.py",
        "28": "osint_search.py",
        "27": "file_integrity.py",
        "26": "system_health.py",
        "25": "learning_center.py",
        "24": "network_security.py",
        "23": "encryption_lab.py",
        "22": "password_generator.py",
        "21": "password_lab.py",
        "20": "security_audit.py",
        "19": "log_analyzer.py",
        "18": "integrity_monitor.py",
        "17": "system_info.py",
        "16": "network_diagnostics.py",
        "15": "forensics.py",
        "14": "evidence_vault.py",
        "13": "case_analytics.py",
        "12": "case_search.py",
        "11": "case_manager.py",
        "10": "master_search.py",
        "9": "diagnostics.py",
        "1": "profile.py",
        "2": "username.py",
        "3": "posts.py",
        "4": "image_meta.py",
        "5": "reports.py"
    }

    if choice in selected:
        if os.path.isfile(selected[choice]):
            os.system(f"python {selected[choice]}")
        else:
            print("Module missing!")
            input("ENTER...")
    elif choice == "0":
        break
