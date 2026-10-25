
import os
import socket
import urllib.request

GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"

def clear():
    os.system("clear")

def banner():
    clear()
    os.system("figlet -f standard TORDISSX86")
    print(GREEN + "ADVANCED OSINT TERMINAL v3.0" + RESET)
    print(CYAN + "=" * 38 + RESET)

def ip_info():
    print("\n[IP INFORMATION]")
    try:
        print("Local IP:", socket.gethostbyname(socket.gethostname()))
    except Exception as e:
        print("Error:", e)

def network():
    print("\n[NETWORK DISCOVERY]")
    os.system("ip neigh")

def history():
    print("\n[DEVICE HISTORY]")
    os.system("python -c \"import sqlite3; c=sqlite3.connect('network.db'); print(*c.execute('SELECT ip,mac,seen FROM history ORDER BY id DESC LIMIT 20'),sep='\\n')\"")

def camera():
    print("\n[AUTHORIZED CAMERA INVENTORY]")
    os.system("curl -s http://127.0.0.1:5001/api/network/cameras")

def audit():
    print("\n[SECURITY AUDIT]")
    os.system("ip route")
    os.system("ip addr")

def reports():
    print("\n[REPORT CENTER]")
    os.system("mkdir -p reports")
    os.system("curl -s http://127.0.0.1:5001/api/network/export > reports/network_report.json")
    print("Report saved in reports/network_report.json")

def dashboard():
    os.system("termux-open-url http://127.0.0.1:5001/network")

while True:
    banner()
    print("""
[1] IP INFORMATION
[2] NETWORK DISCOVERY
[3] DEVICE HISTORY
[4] CAMERA INVENTORY
[5] SECURITY AUDIT
[6] REPORT CENTER
[7] OPEN WEB DASHBOARD
[0] EXIT
""")
    choice = input("TORDISSX86 >> ")

    if choice == "1":
        ip_info()
    elif choice == "2":
        network()
    elif choice == "3":
        history()
    elif choice == "4":
        camera()
    elif choice == "5":
        audit()
    elif choice == "6":
        reports()
    elif choice == "7":
        dashboard()
    elif choice == "0":
        break
    else:
        print("Invalid option!")

    input("\nPress ENTER to return to menu...")
