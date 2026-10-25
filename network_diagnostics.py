import os
import socket
import subprocess
import json
from datetime import datetime

def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "Unavailable"
    finally:
        sock.close()

def get_interfaces():
    try:
        result = subprocess.run(
            ["ip", "-brief", "addr"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() or "No interface information"
    except (OSError, subprocess.TimeoutExpired):
        return "Interface information unavailable"

def test_internet():
    try:
        connection = socket.create_connection(
            ("example.com", 443), timeout=5
        )
        connection.close()
        return "CONNECTED"
    except OSError:
        return "NOT CONNECTED"

def get_dns():
    try:
        with open("/etc/resolv.conf", "r") as file:
            lines = [
                line.strip() for line in file
                if line.strip().startswith("nameserver")
            ]
        return lines or ["DNS information unavailable"]
    except OSError:
        return ["Unable to read DNS configuration"]

def run_diagnostics():
    print("\nRunning network diagnostics...")

    results = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "local_ip": get_local_ip(),
        "internet_status": test_internet(),
        "interfaces": get_interfaces(),
        "dns": get_dns()
    }

    print("\n" + "=" * 45)
    print("TORDISSX86 NETWORK DIAGNOSTICS")
    print("=" * 45)
    print("Local IP:", results["local_ip"])
    print("Internet:", results["internet_status"])
    print("\nNetwork Interfaces:")
    print(results["interfaces"])
    print("\nDNS Configuration:")

    for item in results["dns"]:
        print(item)

    print("=" * 45)

    save = input("\nSave diagnostic report? (y/n): ").lower()

    if save == "y":
        os.makedirs("network_reports", exist_ok=True)

        filename = datetime.now().strftime(
            "NETWORK_%Y%m%d_%H%M%S.json"
        )

        path = os.path.join("network_reports", filename)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)

        print("\nReport saved:", path)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 NETWORK DIAGNOSTICS v4.1")
        print("=" * 45)
        print("[1] Run Network Diagnostics")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            run_diagnostics()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
