import os
import socket
import ssl
import json
import urllib.request
from datetime import datetime

REPORT_FOLDER = "security_reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

def get_domain():
    domain = input("\nEnter domain (example.com): ").strip().lower()

    if not domain or "/" in domain or " " in domain:
        print("ERROR: Enter a valid domain name.")
        return None

    return domain

def dns_lookup():
    domain = get_domain()

    if not domain:
        return

    try:
        results = socket.getaddrinfo(
            domain, None, socket.AF_UNSPEC
        )

        addresses = sorted({
            result[4][0] for result in results
        })

        print("\nDNS LOOKUP RESULTS")
        print("=" * 40)

        for address in addresses:
            print("IP Address:", address)

    except socket.gaierror:
        print("DNS lookup failed.")

def https_inspection():
    domain = get_domain()

    if not domain:
        return

    context = ssl.create_default_context()

    try:
        with socket.create_connection(
            (domain, 443), timeout=8
        ) as connection:

            with context.wrap_socket(
                connection, server_hostname=domain
            ) as secure_socket:

                certificate = secure_socket.getpeercert()

                print("\nHTTPS INSPECTION")
                print("=" * 40)
                print("Domain:", domain)
                print("TLS Version:", secure_socket.version())
                print("Cipher:", secure_socket.cipher()[0])
                print("Certificate:", "VALIDATED")

                print("Subject:", certificate.get("subject"))
                print("Issuer:", certificate.get("issuer"))
                print("Valid Until:", certificate.get("notAfter"))

    except (OSError, ssl.SSLError) as error:
        print("\nHTTPS inspection failed.")
        print("Details:", error)

def inspect_headers():
    domain = get_domain()

    if not domain:
        return

    import subprocess

    url = "https://" + domain
    print("\nConnecting to:", url)

    try:
        result = subprocess.run(
            [
                "curl", "-sS", "-D", "-", "-o", "/dev/null",
                "-L", "--max-time", "15",
                "--user-agent", "Mozilla/5.0 TORDISSX86",
                url
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode != 0:
            print("Connection failed:", result.stderr)
            return

        print("\nHTTP RESPONSE HEADERS")
        print("=" * 40)
        print(result.stdout)

    except subprocess.TimeoutExpired:
        print("Request timed out.")
    except FileNotFoundError:
        print("curl is not installed.")
    except Exception as error:
        print("Header inspection failed:", error)

def save_report():
    domain = get_domain()

    if not domain:
        return

    report = {
        "tool": "TORDISSX86 Network Security Lab",
        "domain": domain,
        "date": datetime.now().isoformat(),
        "note": "Educational domain inspection"
    }

    filename = datetime.now().strftime(
        "SECURITY_%Y%m%d_%H%M%S.json"
    )

    path = os.path.join(REPORT_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nReport saved:", path)

def main():
    while True:
        os.system("clear")

        print("=" * 45)
        print("TORDISSX86 NETWORK SECURITY LAB v4.9")
        print("=" * 45)
        print("[1] DNS Lookup")
        print("[2] HTTPS Inspection")
        print("[3] HTTP Headers")
        print("[4] Save Domain Report")
        print("[0] Back to Dashboard")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            dns_lookup()
        elif choice == "2":
            https_inspection()
        elif choice == "3":
            inspect_headers()
        elif choice == "4":
            save_report()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
