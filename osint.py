
import socket
import ssl
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime

GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"

def banner():
    print(GREEN + r"""
 _____ ___  ____  ____ ___ ____ ____  ____
|_   _/ _ \|  _ \|  _ \_ _/ ___/ ___|/ ___|
  | || | | | |_) | | | | |\___ \___ \___ \
  | || |_| |  _ <| |_| | | ___) |__) |__) |
  |_| \___/|_| \_\____/___|____/____/____/
    """ + RESET)
    print(CYAN + "       OSINT RECON DASHBOARD v1.0")
    print("       Developer: TORDISSX86")
    print("=" * 45 + RESET)

def get_domain():
    value = input("\nEnter public domain: ").strip()
    value = re.sub(r"^https?://", "", value, flags=re.I)
    value = value.split("/")[0].split(":")[0].strip().lower()

    try:
        value = value.encode("idna").decode("ascii")
    except Exception:
        return None

    if not re.fullmatch(
        r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}",
        value
    ):
        return None

    return value

def request_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TORDISSX86-OSINT/1.0"}
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode())

def dns_lookup(domain):
    print(GREEN + "\n[ DNS RECORDS ]" + RESET)

    for record in ["A", "AAAA", "MX", "NS", "TXT"]:
        try:
            url = (
                "https://dns.google/resolve?"
                + urllib.parse.urlencode({
                    "name": domain,
                    "type": record
                })
            )
            data = request_json(url)
            answers = data.get("Answer", [])

            print(CYAN + f"\n{record}:" + RESET)

            if answers:
                for answer in answers[:8]:
                    print("  " + answer["data"][:200])
            else:
                print("  No records returned")

        except Exception as error:
            print(f"  Lookup unavailable: {error}")

def ip_lookup(domain):
    print(GREEN + "\n[ IP INFORMATION ]" + RESET)

    try:
        results = socket.getaddrinfo(
            domain, 443, type=socket.SOCK_STREAM
        )

        ips = sorted(set(item[4][0] for item in results))

        for ip in ips:
            print("IP Address:", ip)

            try:
                hostname = socket.gethostbyaddr(ip)[0]
                print("Reverse DNS:", hostname)
            except Exception:
                print("Reverse DNS: Not available")

    except Exception as error:
        print(RED + "IP lookup failed: " + str(error) + RESET)

def website_headers(domain):
    print(GREEN + "\n[ WEBSITE HEADERS ]" + RESET)

    url = "https://" + domain + "/"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TORDISSX86-OSINT/1.0"},
        method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            print("HTTP Status:", response.status)

            for key, value in response.headers.items():
                print(f"{key}: {value}")

    except Exception as error:
        print("Website request failed:", error)

def ssl_lookup(domain):
    print(GREEN + "\n[ SSL CERTIFICATE ]" + RESET)

    try:
        context = ssl.create_default_context()

        with socket.create_connection(
            (domain, 443), timeout=10
        ) as sock:
            with context.wrap_socket(
                sock, server_hostname=domain
            ) as secure_sock:

                cert = secure_sock.getpeercert()

                print("TLS Version:", secure_sock.version())
                print("Subject:", cert.get("subject"))
                print("Issuer:", cert.get("issuer"))
                print("Valid from:", cert.get("notBefore"))
                print("Expires:", cert.get("notAfter"))

    except Exception as error:
        print("SSL lookup failed:", error)

def rdap_lookup(domain):
    print(GREEN + "\n[ DOMAIN REGISTRATION - RDAP ]" + RESET)

    try:
        url = "https://rdap.org/domain/" + urllib.parse.quote(domain)
        data = request_json(url)

        print("Domain:", data.get("ldhName", domain))
        print("Handle:", data.get("handle", "Unavailable"))
        print("Status:", data.get("status", []))

        for event in data.get("events", []):
            print(
                event.get("eventAction"),
                event.get("eventDate")
            )

        nameservers = data.get("nameservers", [])

        print("Nameservers:")
        for ns in nameservers:
            print(" ", ns.get("ldhName", "Unknown"))

    except Exception as error:
        print("RDAP lookup unavailable:", error)

def main():
    while True:
        banner()

        print("""
1. Domain information (RDAP)
2. DNS records
3. IP address lookup
4. Website HTTP headers
5. SSL certificate
6. Run all checks
0. Exit
""")

        choice = input("TORDISSX86 >> ").strip()

        if choice == "0":
            print("Dashboard closed.")
            break

        if choice not in ["1", "2", "3", "4", "5", "6"]:
            print("Invalid option.")
            input("\nPress Enter...")
            continue

        domain = get_domain()

        if not domain:
            print(RED + "Invalid domain format." + RESET)
            input("\nPress Enter...")
            continue

        print(CYAN + "\nTarget:", domain, RESET)

        if choice in ["1", "6"]:
            rdap_lookup(domain)

        if choice in ["2", "6"]:
            dns_lookup(domain)

        if choice in ["3", "6"]:
            ip_lookup(domain)

        if choice in ["4", "6"]:
            website_headers(domain)

        if choice in ["5", "6"]:
            ssl_lookup(domain)

        print("\n" + "=" * 45)
        input("Press Enter to return to menu...")

if __name__ == "__main__":
    main()
