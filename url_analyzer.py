import os
import re
import json
import socket
import hashlib
from datetime import datetime
from urllib.parse import urlparse, parse_qs

REPORT_DIR = "url_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def analyze_url():
    raw_url = input("Enter public website URL: ").strip()

    if not raw_url:
        print("URL cannot be empty.")
        return

    if "://" not in raw_url:
        raw_url = "https://" + raw_url

    parsed = urlparse(raw_url)

    if parsed.scheme not in ("http", "https"):
        print("Unsupported URL scheme.")
        return

    domain = parsed.hostname

    if not domain or not re.fullmatch(
        r"[A-Za-z0-9.-]+", domain
    ):
        print("Invalid domain.")
        return

    try:
        port = parsed.port
    except ValueError:
        print("Invalid port.")
        return

    try:
        ip_addresses = sorted({
            item[4][0]
            for item in socket.getaddrinfo(domain, port or 443)
        })
    except socket.gaierror:
        ip_addresses = []

    url_hash = hashlib.sha256(
        raw_url.encode("utf-8")
    ).hexdigest()

    parameters = parse_qs(parsed.query)

    report = {
        "tool": "TORDISSX86 URL Analyzer",
        "date": datetime.now().isoformat(),
        "url": raw_url,
        "scheme": parsed.scheme,
        "domain": domain,
        "port": port,
        "path": parsed.path,
        "query_parameters": parameters,
        "fragment": parsed.fragment,
        "dns_addresses": ip_addresses,
        "sha256": url_hash
    }

    print("\nURL ANALYSIS REPORT")
    print("=" * 45)
    print("Scheme:", parsed.scheme)
    print("Domain:", domain)
    print("Port:", port or ("443" if parsed.scheme == "https" else "80"))
    print("Path:", parsed.path or "/")
    print("HTTPS:", "YES" if parsed.scheme == "https" else "NO")
    print("DNS Addresses:", ", ".join(ip_addresses) or "Unavailable")
    print("Query Parameters:", parameters or "None")
    print("SHA-256:", url_hash)

    filename = datetime.now().strftime(
        "URL_%Y%m%d_%H%M%S.json"
    )

    filepath = os.path.join(REPORT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nReport saved:", filepath)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 v6.1")
        print("URL & WEBSITE ANALYZER")
        print("=" * 45)
        print("[1] Analyze URL")
        print("[0] Back")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            analyze_url()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
