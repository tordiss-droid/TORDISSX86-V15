import re
import json
import socket
import ssl
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from email.utils import parseaddr

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports" / "web_intelligence"
REPORTS.mkdir(parents=True, exist_ok=True)

def save_report(kind, data):
    name = kind + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    path = REPORTS / name
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")
    return str(path.relative_to(ROOT))

def domain_intel(domain):
    domain = domain.strip().lower()
    if not re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
        raise ValueError("Invalid domain name")

    result = {"domain": domain, "checked": datetime.now().isoformat()}

    try:
        result["ip_addresses"] = sorted({
            item[4][0] for item in socket.getaddrinfo(domain, 443)
        })
    except Exception as e:
        result["dns_error"] = str(e)

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=6) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as secure:
                cert = secure.getpeercert()
                result["tls"] = {
                    "version": secure.version(),
                    "subject": str(cert.get("subject")),
                    "issuer": str(cert.get("issuer")),
                    "expires": cert.get("notAfter")
                }
    except Exception as e:
        result["tls_error"] = str(e)

    return result

def email_intel(address):
    address = address.strip()
    parsed = parseaddr(address)[1]
    if parsed != address or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", address):
        raise ValueError("Invalid email format")

    domain = address.rsplit("@", 1)[1].lower()
    result = {
        "email": address,
        "format_valid": True,
        "domain": domain,
        "checked": datetime.now().isoformat(),
        "note": "Format validation only; mailbox ownership and existence are not verified."
    }

    try:
        import dns.resolver
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
        resolver.lifetime = 5
        result["mx_records"] = [
            str(x.exchange).rstrip(".")
            for x in resolver.resolve(domain, "MX")
        ]
    except Exception as e:
        result["mx_note"] = "MX lookup unavailable: " + str(e)

    return result

def phone_intel(number):
    number = number.strip()
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        return {
            "input": number,
            "valid": phonenumbers.is_valid_number(parsed),
            "possible": phonenumbers.is_possible_number(parsed),
            "country_code": parsed.country_code,
            "region": phonenumbers.region_code_for_number(parsed),
            "number_type": str(phonenumbers.number_type(parsed)),
            "note": "Number metadata only; no subscriber identity lookup."
        }
    except ImportError:
        raise ValueError("Install dependency: pip install phonenumbers")
    except Exception as e:
        raise ValueError("Phone number error: " + str(e))

def username_intel(username):
    username = username.strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9._-]{2,40}", username):
        raise ValueError("Invalid username")

    sites = {
        "GitHub": "https://github.com/" + username,
        "Reddit": "https://www.reddit.com/user/" + username,
        "Instagram": "https://www.instagram.com/" + username + "/"
    }

    result = {"username": username, "public_profiles": {}}

    for site, url in sites.items():
        result["public_profiles"][site] = url

    result["note"] = "Profile URLs are leads only; existence has not been verified."
    return result

def analyze(kind, value):
    functions = {
        "domain": domain_intel,
        "email": email_intel,
        "phone": phone_intel,
        "username": username_intel
    }
    if kind not in functions:
        raise ValueError("Unknown analysis type")

    data = functions[kind](value)
    data["report"] = save_report(kind, data)
    return data
