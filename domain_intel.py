import os
import json
import socket
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse

REPORT_DIR = "domain_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def get_domain():
    value = input("Enter domain (example.com): ").strip().lower()

    if "://" in value:
        value = urlparse(value).hostname or ""

    if not value or " " in value or "." not in value:
        print("Invalid domain.")
        return None

    if any(not (c.isalnum() or c in ".-") for c in value):
        print("Invalid domain characters.")
        return None

    return value

def lookup_domain():
    domain = get_domain()

    if not domain:
        return

    url = "https://rdap.org/domain/" + domain

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TORDISSX86-Educational-Tool"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        registrar = "Unavailable"
        nameservers = []
        events = []

        for entity in data.get("entities", []):
            for item in entity.get("roles", []):
                if item == "registrar":
                    registrar = entity.get("handle", "Unavailable")

        for server in data.get("nameservers", []):
            nameservers.append(server.get("ldhName", ""))

        for event in data.get("events", []):
            events.append({
                "action": event.get("eventAction"),
                "date": event.get("eventDate")
            })

        report = {
            "tool": "TORDISSX86 Domain Intelligence",
            "date": datetime.now().isoformat(),
            "domain": domain,
            "registrar": registrar,
            "nameservers": nameservers,
            "events": events
        }

        print("\nDOMAIN INTELLIGENCE")
        print("=" * 40)
        print("Domain:", domain)
        print("Registrar:", registrar)
        print("Nameservers:")

        for server in nameservers:
            print("-", server)

        print("\nRegistration Events:")
        for event in events:
            print(event["action"], ":", event["date"])

        filename = datetime.now().strftime(
            "DOMAIN_%Y%m%d_%H%M%S.json"
        )

        path = os.path.join(REPORT_DIR, filename)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print("\nReport saved:", path)

    except urllib.error.HTTPError as error:
        print("RDAP service returned HTTP status:", error.code)
    except urllib.error.URLError as error:
        print("Network connection failed:", error.reason)
    except Exception as error:
        print("Lookup failed:", error)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 v6.2")
        print("DOMAIN INTELLIGENCE")
        print("=" * 45)
        print("[1] Public RDAP Lookup")
        print("[0] Back")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            lookup_domain()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
