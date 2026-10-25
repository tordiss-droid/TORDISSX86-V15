import os
import re
import json
import ssl
import socket
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
from urllib.parse import urlparse

import dns.resolver
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from PIL import Image, ExifTags

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE, "reports", "advanced_osint")
os.makedirs(REPORT_DIR, exist_ok=True)

def save_report(name, data):
    filename = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORT_DIR, filename + "_" + name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("\nReport saved:", path)

def resolver():
    r = dns.resolver.Resolver(configure=False)
    r.nameservers = ["1.1.1.1", "8.8.8.8"]
    r.timeout = 5
    r.lifetime = 10
    return r

def dns_records(domain, record_types):
    result = {}
    r = resolver()

    for record in record_types:
        try:
            answers = r.resolve(domain, record)
            result[record] = [str(x) for x in answers]
        except Exception:
            result[record] = []

    return result

def phone_intelligence():
    print("\nPHONE NUMBER INTELLIGENCE")
    number = input("Enter number with country code (example +255...): ").strip()

    try:
        parsed = phonenumbers.parse(number, None)

        data = {
            "input": number,
            "valid": phonenumbers.is_valid_number(parsed),
            "possible": phonenumbers.is_possible_number(parsed),
            "country_code": parsed.country_code,
            "region_code": phonenumbers.region_code_for_number(parsed),
            "international": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "national": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.NATIONAL
            ),
            "e164": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            ),
            "carrier_metadata": carrier.name_for_number(parsed, "en"),
            "region_metadata": geocoder.description_for_number(parsed, "en"),
            "timezones": list(timezone.time_zones_for_number(parsed))
        }

        print(json.dumps(data, indent=4))
        save_report("phone", data)

    except Exception as e:
        print("Phone analysis failed:", e)

def email_intelligence():
    print("\nEMAIL INTELLIGENCE")
    email = input("Enter email address: ").strip()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, email):
        print("Invalid email format.")
        return

    domain = email.rsplit("@", 1)[1].lower()

    records = dns_records(
        domain,
        ["MX", "TXT"]
    )

    txt = records.get("TXT", [])

    spf = [x for x in txt if "v=spf1" in x.lower()]
    dmarc = dns_records("_dmarc." + domain, ["TXT"]).get("TXT", [])

    data = {
        "email": email,
        "format_valid": True,
        "domain": domain,
        "mx_records": records.get("MX", []),
        "spf_records": spf,
        "dmarc_records": dmarc
    }

    print(json.dumps(data, indent=4))
    save_report("email", data)

def camera_forensics():
    print("\nCAMERA & IMAGE FORENSICS")
    path = input("Image file path: ").strip()
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        print("File not found.")
        return

    try:
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()

        image = Image.open(path)
        exif = image.getexif()

        metadata = {}

        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            metadata[tag] = str(value)

        data = {
            "file": os.path.basename(path),
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "size_bytes": os.path.getsize(path),
            "sha256": digest,
            "camera_make": metadata.get("Make", "Not available"),
            "camera_model": metadata.get("Model", "Not available"),
            "date_taken": metadata.get("DateTimeOriginal", "Not available"),
            "gps_metadata_present": "GPSInfo" in metadata,
            "exif": metadata
        }

        print(json.dumps(data, indent=4))
        if data["gps_metadata_present"]:
            print("\nWARNING: This image contains GPS metadata.")
            print("Protect your privacy before sharing it.")

        save_report("image", data)

    except Exception as e:
        print("Image analysis failed:", e)

def domain_intelligence():
    print("\nDOMAIN INTELLIGENCE")
    domain = input("Enter domain (example.com): ").strip().lower()
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.split("/")[0]

    if not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        print("Invalid domain.")
        return

    records = dns_records(
        domain,
        ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    )

    data = {
        "domain": domain,
        "dns_records": records
    }

    try:
        request = urllib.request.Request(
            "https://rdap.org/domain/" + urllib.parse.quote(domain),
            headers={"User-Agent": "TORDISSX86/7.0"}
        )

        with urllib.request.urlopen(request, timeout=12) as response:
            rdap = json.loads(response.read().decode("utf-8"))
            data["rdap"] = {
                "ldh_name": rdap.get("ldhName"),
                "status": rdap.get("status"),
                "events": rdap.get("events", [])
            }

    except Exception as e:
        data["rdap_error"] = str(e)

    print(json.dumps(data, indent=4))
    save_report("domain", data)

def username_intelligence():
    print("\nPUBLIC USERNAME SEARCH")
    username = input("Enter username: ").strip().lstrip("@")

    if not re.match(r"^[A-Za-z0-9._-]{1,50}$", username):
        print("Invalid username format.")
        return

    sites = {
        "Google": "https://www.google.com/search?q=",
        "GitHub": "https://github.com/",
        "Reddit": "https://www.reddit.com/user/",
        "Instagram": "https://www.instagram.com/",
        "TikTok": "https://www.tiktok.com/@"
    }

    results = {}

    for site, base in sites.items():
        if site == "Google":
            url = base + urllib.parse.quote('"' + username + '"')
        else:
            url = base + urllib.parse.quote(username)

        results[site] = url
        print(site + ":", url)

    save_report("username", {
        "username": username,
        "public_search_links": results
    })

def url_analyzer():
    print("\nURL ANALYZER")
    value = input("Enter URL: ").strip()

    if "://" not in value:
        value = "https://" + value

    parsed = urlparse(value)
    host = parsed.hostname

    if not host:
        print("Invalid URL.")
        return

    data = {
        "url": value,
        "scheme": parsed.scheme,
        "hostname": host,
        "port": parsed.port,
        "path": parsed.path,
        "query_present": bool(parsed.query)
    }

    try:
        addresses = socket.getaddrinfo(host, None)
        data["resolved_addresses"] = sorted(
            set(x[4][0] for x in addresses)
        )
    except Exception as e:
        data["resolution_error"] = str(e)

    print(json.dumps(data, indent=4))
    save_report("url", data)

def file_forensics():
    print("\nFILE FORENSICS")
    path = os.path.expanduser(input("File path: ").strip())

    if not os.path.isfile(path):
        print("File not found.")
        return

    digest = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)

    data = {
        "file": os.path.basename(path),
        "size_bytes": os.path.getsize(path),
        "sha256": digest.hexdigest(),
        "modified": datetime.fromtimestamp(
            os.path.getmtime(path)
        ).isoformat()
    }

    print(json.dumps(data, indent=4))
    save_report("file", data)



def dns_intelligence():
    print("\nDNS INTELLIGENCE")
    domain = input("Enter domain: ").strip().lower()

    if not domain or "/" in domain or " " in domain:
        print("Invalid domain.")
        return

    records = dns_records(
        domain, ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    )

    data = {"domain": domain, "records": records}
    print(json.dumps(data, indent=4))
    save_report("dns", data)


def tls_analyzer():
    print("\nSSL/TLS CERTIFICATE ANALYZER")
    host = input("Enter hostname: ").strip().lower()

    if not host or "/" in host or " " in host:
        print("Invalid hostname.")
        return

    try:
        context = ssl.create_default_context()

        with socket.create_connection((host, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as secure:
                cert = secure.getpeercert()

                data = {
                    "hostname": host,
                    "tls_version": secure.version(),
                    "cipher": secure.cipher(),
                    "subject": cert.get("subject"),
                    "issuer": cert.get("issuer"),
                    "valid_from": cert.get("notBefore"),
                    "valid_until": cert.get("notAfter"),
                    "subject_alt_names": cert.get("subjectAltName")
                }

        print(json.dumps(data, indent=4))
        save_report("tls", data)

    except Exception as e:
        print("TLS analysis failed:", str(e))


def http_security_headers():
    print("\nHTTP SECURITY HEADERS")
    host = input("Enter website URL or hostname: ").strip()

    if not host:
        print("Invalid input.")
        return

    if "://" not in host:
        host = "https://" + host

    parsed = urlparse(host)

    if not parsed.hostname:
        print("Invalid URL.")
        return

    try:
        request = urllib.request.Request(
            host,
            headers={"User-Agent": "TORDISSX86/8.0"},
            method="GET"
        )

        with urllib.request.urlopen(request, timeout=12) as response:
            headers = dict(response.headers.items())
            response.read(1)

        security_names = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy"
        ]

        data = {
            "url": host,
            "status": response.status,
            "security_headers": {
                name: headers.get(name, "Not present")
                for name in security_names
            }
        }

        print(json.dumps(data, indent=4))
        save_report("http_headers", data)

    except Exception as e:
        print("Header analysis failed:", str(e))


def public_search():
    print("\nPUBLIC WEB SEARCH")
    query = input("Enter public search keywords: ").strip()

    if not query:
        print("Search query cannot be empty.")
        return

    encoded = urllib.parse.quote_plus(query)

    links = {
        "Google": "https://www.google.com/search?q=" + encoded,
        "Bing": "https://www.bing.com/search?q=" + encoded,
        "DuckDuckGo": "https://duckduckgo.com/?q=" + encoded
    }

    data = {"query": query, "search_links": links}

    for name, url in links.items():
        print(name + ": " + url)

    save_report("public_search", data)




def report_search():
    print("\nREPORT SEARCH")
    keyword = input("Enter search keyword: ").strip().lower()

    if not keyword:
        print("Keyword required.")
        return

    found = 0

    for root, dirs, files in os.walk(REPORT_DIR):
        for filename in files:
            if not filename.endswith(".json"):
                continue

            path = os.path.join(root, filename)

            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()

                if keyword in content.lower():
                    print("MATCH:", path)
                    found += 1
            except Exception:
                continue

    print("Reports found:", found)


def export_all_reports():
    print("\nEXPORT ALL REPORTS")
    collected = []

    for root, dirs, files in os.walk(REPORT_DIR):
        for filename in files:
            if not filename.endswith(".json"):
                continue

            path = os.path.join(root, filename)

            try:
                with open(path, encoding="utf-8") as f:
                    collected.append({
                        "filename": filename,
                        "data": json.load(f)
                    })
            except Exception:
                continue

    output = os.path.join(
        REPORT_DIR,
        "all_reports_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    )

    with open(output, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=4, ensure_ascii=False)

    print("Exported reports:", len(collected))
    print("Saved:", output)


def project_diagnostics():
    print("\nPROJECT DIAGNOSTICS")

    import sys
    import platform
    import importlib.util

    modules = [
        "dns",
        "phonenumbers",
        "PIL"
    ]

    data = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "dependencies": {},
        "report_directory_exists": os.path.isdir(REPORT_DIR)
    }

    for module in modules:
        data["dependencies"][module] = (
            importlib.util.find_spec(module) is not None
        )

    print(json.dumps(data, indent=4))
    save_report("diagnostics", data)


def view_reports():
    print("\nSAVED REPORTS")
    files = sorted(os.listdir(REPORT_DIR))

    if not files:
        print("No reports available.")
        return

    for item in files:
        print("-", item)



CASE_DIR = os.path.join(BASE, "cases")
os.makedirs(CASE_DIR, exist_ok=True)
CASE_FILE = os.path.join(CASE_DIR, "cases.json")


def load_cases():
    if not os.path.exists(CASE_FILE):
        return []
    try:
        with open(CASE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_cases(cases):
    with open(CASE_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)


def create_case():
    print("\nCREATE INVESTIGATION CASE")
    title = input("Case title: ").strip()
    description = input("Description: ").strip()

    if not title:
        print("Title required.")
        return

    cases = load_cases()
    case_id = "TORD-" + datetime.now().strftime("%Y%m%d%H%M%S")

    case = {
        "case_id": case_id,
        "title": title,
        "description": description,
        "created": datetime.now().isoformat(),
        "notes": [],
        "status": "OPEN"
    }

    cases.append(case)
    save_cases(cases)
    print("Case created:", case_id)


def view_cases():
    print("\nINVESTIGATION CASES")
    cases = load_cases()

    if not cases:
        print("No cases found.")
        return

    for case in cases:
        print(
            case["case_id"],
            "|",
            case["title"],
            "|",
            case["status"]
        )


def add_case_note():
    cases = load_cases()

    case_id = input("Enter Case ID: ").strip()
    note = input("Enter note: ").strip()

    if not note:
        print("Note required.")
        return

    for case in cases:
        if case["case_id"] == case_id:
            case["notes"].append({
                "note": note,
                "date": datetime.now().isoformat()
            })
            save_cases(cases)
            print("Note saved.")
            return

    print("Case not found.")


def search_cases():
    keyword = input("Search keyword: ").strip().lower()

    if not keyword:
        print("Keyword required.")
        return

    matches = 0

    for case in load_cases():
        content = json.dumps(case).lower()

        if keyword in content:
            print(case["case_id"], "|", case["title"])
            matches += 1

    print("Matches:", matches)


def case_statistics():
    cases = load_cases()

    total = len(cases)
    opened = sum(1 for c in cases if c["status"] == "OPEN")
    closed = sum(1 for c in cases if c["status"] == "CLOSED")

    print("\nCASE STATISTICS")
    print("Total:", total)
    print("Open:", opened)
    print("Closed:", closed)


def backup_project_data():
    import zipfile

    output_dir = os.path.join(BASE, "backups")
    os.makedirs(output_dir, exist_ok=True)

    filename = "TORDISSX86_backup_" + datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    ) + ".zip"

    output = os.path.join(output_dir, filename)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder in ["reports", "cases", "evidence"]:
            folder_path = os.path.join(BASE, folder)

            if not os.path.isdir(folder_path):
                continue

            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    path = os.path.join(root, file)
                    archive.write(
                        path,
                        os.path.relpath(path, BASE)
                    )

    print("Backup created:", output)


def main():
    while True:
        print("\n" + "=" * 48)
        print("       TORDISSX86 ADVANCED OSINT v10.0")
        print("=" * 48)
        print("1. Phone Number Intelligence")
        print("2. Email Intelligence")
        print("3. Camera & Image Forensics")
        print("4. Domain Intelligence")
        print("5. Public Username Search")
        print("6. URL Analyzer")
        print("7. File Forensics")
        print("8. View Reports")
        print("9. DNS Intelligence")
        print("10. SSL/TLS Certificate Analyzer")
        print("11. HTTP Security Headers")
        print("12. Public Web Search")
        print("13. Report Search")
        print("14. Export All Reports")
        print("15. Project Diagnostics")
        print("16. Create Investigation Case")
        print("17. View Investigation Cases")
        print("18. Add Case Notes")
        print("19. Search Cases")
        print("20. Case Statistics")
        print("21. Backup Project Data")
        print("0. Exit")

        choice = input("\nSelect option: ").strip()

        actions = {
            "1": phone_intelligence,
            "2": email_intelligence,
            "3": camera_forensics,
            "4": domain_intelligence,
            "5": username_intelligence,
            "6": url_analyzer,
            "7": file_forensics,
            "8": view_reports,
            "9": dns_intelligence,
            "10": tls_analyzer,
            "11": http_security_headers,
            "12": public_search,
            "13": report_search,
            "14": export_all_reports,
            "15": project_diagnostics,
            "16": create_case,
            "17": view_cases,
            "18": add_case_note,
            "19": search_cases,
            "20": case_statistics,
            "21": backup_project_data
        }

        if choice == "0":
            print("TORDISSX86 Advanced OSINT closed.")
            break

        action = actions.get(choice)

        if action:
            try:
                action()
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
            except Exception as e:
                print("Module error:", e)
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
