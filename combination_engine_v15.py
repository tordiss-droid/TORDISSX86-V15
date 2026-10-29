import re
import json
import socket
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports" / "combination_v15"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DOMAIN_PATTERN = re.compile(
    r"(?=.{1,253}$)"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,63}$"
)

ALLOWED_TYPES = {
    "domain", "email", "phone",
    "username", "dns", "url"
}


def validate_domain(value):
    value = value.strip().lower()

    if not DOMAIN_PATTERN.fullmatch(value):
        raise ValueError("Invalid public domain")

    return value


def save_report(kind, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{kind}_{timestamp}.json"
    path = REPORT_DIR / filename

    path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    return str(path.relative_to(ROOT))


def analyze_dns(value):
    domain = validate_domain(value)

    try:
        import dns.resolver
    except ImportError:
        raise ValueError("Install dnspython first")

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    resolver.timeout = 5
    resolver.lifetime = 10

    records = {}

    for record_type in ("A", "AAAA", "MX", "NS", "TXT", "CNAME"):
        try:
            answers = resolver.resolve(
                domain, record_type, lifetime=10
            )
            records[record_type] = [
                answer.to_text() for answer in answers
            ]
        except dns.resolver.NoAnswer:
            records[record_type] = []
        except dns.resolver.NXDOMAIN:
            raise ValueError("Domain does not exist")
        except Exception as error:
            records[record_type] = []
            records[record_type + "_note"] = str(error)[:200]

    return {
        "tool": "TORDISSX86 DNS Intelligence",
        "domain": domain,
        "records": records,
        "checked": datetime.now().isoformat()
    }


def analyze_url(value):
    value = value.strip()

    if len(value) > 2048:
        raise ValueError("URL is too long")

    if "://" not in value:
        value = "https://" + value

    parsed = urlparse(value)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not accepted")

    domain = validate_domain(parsed.hostname or "")

    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        raise ValueError("Invalid URL port")

    try:
        addresses = sorted({
            item[4][0]
            for item in socket.getaddrinfo(domain, port)
        })
    except OSError:
        addresses = []

    return {
        "tool": "TORDISSX86 URL Analyzer",
        "url": value,
        "scheme": parsed.scheme,
        "domain": domain,
        "port": port,
        "path": parsed.path or "/",
        "query_parameter_names": list(
            dict.fromkeys(
                key for key in parsed.query.split("&") if key
            )
        ),
        "dns_addresses": addresses,
        "checked": datetime.now().isoformat(),
        "note": "Metadata and DNS inspection only; no page exploitation."
    }


def analyze(kind, value):
    kind = str(kind).strip().lower()
    value = str(value).strip()

    if kind not in ALLOWED_TYPES:
        raise ValueError("Unsupported analysis type")

    if not value or len(value) > 2048:
        raise ValueError("Invalid or oversized input")

    if kind in ("domain", "email", "phone", "username"):
        import web_intel

        functions = {
            "domain": web_intel.domain_intel,
            "email": web_intel.email_intel,
            "phone": web_intel.phone_intel,
            "username": web_intel.username_intel
        }

        result = functions[kind](value)

    elif kind == "dns":
        result = analyze_dns(value)

    else:
        result = analyze_url(value)

    report = save_report(kind, result)
    result["report"] = report

    return result


def list_reports():
    files = sorted(
        REPORT_DIR.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    return [
        {
            "name": path.name,
            "size": path.stat().st_size
        }
        for path in files[:100]
    ]


def get_status():
    return {
        "engine": "TORDISSX86 V15",
        "status": "ready",
        "supported": sorted(ALLOWED_TYPES),
        "reports": len(list_reports())
    }


if __name__ == "__main__":
    print(json.dumps(get_status(), indent=4))
