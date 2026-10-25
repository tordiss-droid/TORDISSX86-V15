import os
import json
import dns.resolver
from datetime import datetime

REPORT_DIR = "dns_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]

def analyze_dns():
    domain = input("Enter authorized domain: ").strip().lower()

    if not domain or " " in domain:
        print("Invalid domain.")
        return

    results = {}

    print("\nDNS INTELLIGENCE REPORT")
    print("=" * 45)
    print("Domain:", domain)

    for record_type in RECORD_TYPES:
        print(f"\n[{record_type} RECORDS]")

        try:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
            resolver.timeout = 5
            resolver.lifetime = 15
            answers = resolver.resolve(domain, record_type, lifetime=15)

            records = []

            for answer in answers:
                value = answer.to_text()
                records.append(value)
                print(value)

            results[record_type] = records

        except dns.resolver.NoAnswer:
            results[record_type] = []
            print("No records found.")

        except dns.resolver.NXDOMAIN:
            print("Domain does not exist.")
            return

        except Exception as error:
            results[record_type] = []
            print("Lookup unavailable:", str(error))

    report = {
        "tool": "TORDISSX86 DNS Intelligence",
        "date": datetime.now().isoformat(),
        "domain": domain,
        "records": results
    }

    filename = datetime.now().strftime(
        "DNS_%Y%m%d_%H%M%S.json"
    )

    path = os.path.join(REPORT_DIR, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nReport saved:", path)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 v6.3")
        print("DNS INTELLIGENCE ANALYZER")
        print("=" * 45)
        print("[1] Analyze DNS Records")
        print("[0] Back")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            analyze_dns()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
