
import os
import json
import sqlite3
import socket
import subprocess
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request

network = Blueprint("network", __name__)
DB = os.path.join(os.path.dirname(__file__), "network.db")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            mac TEXT,
            hostname TEXT,
            seen TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT,
            ip TEXT UNIQUE
        )
    """)
    conn.commit()
    return conn


def discover_devices():
    devices = {}

    # Read-only local network neighbor discovery
    try:
        result = subprocess.run(
            ["ip", "neigh"],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.splitlines():
            parts = line.split()
            if not parts:
                continue

            ip = parts[0]
            mac = ""

            if "lladdr" in parts:
                i = parts.index("lladdr")
                if i + 1 < len(parts):
                    mac = parts[i + 1]

            if mac:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = "Unknown"

                devices[ip] = {
                    "ip": ip,
                    "mac": mac,
                    "hostname": hostname
                }
    except Exception:
        pass

    # Android ARP table fallback
    try:
        with open("/proc/net/arp", "r") as f:
            lines = f.readlines()[1:]

        for line in lines:
            parts = line.split()
            if len(parts) >= 4 and parts[3] != "00:00:00:00:00:00":
                ip, mac = parts[0], parts[3]
                if ip not in devices:
                    devices[ip] = {
                        "ip": ip,
                        "mac": mac,
                        "hostname": "Unknown"
                    }
    except Exception:
        pass

    return list(devices.values())


@network.route("/network")
def network_page():
    return render_template("network.html")


@network.route("/api/network/scan")
def scan():
    devices = discover_devices()
    now = datetime.now().isoformat(timespec="seconds")

    conn = db()
    for device in devices:
        conn.execute(
            """INSERT INTO history(ip, mac, hostname, seen)
               VALUES (?, ?, ?, ?)""",
            (device["ip"], device["mac"],
             device["hostname"], now)
        )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "count": len(devices),
        "devices": devices,
        "time": now
    })


@network.route("/api/network/history")
def history():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY id DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@network.route("/api/network/cameras", methods=["GET", "POST"])
def cameras():
    conn = db()

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        label = str(data.get("label", "")).strip()
        ip = str(data.get("ip", "")).strip()

        import ipaddress
        try:
            address = ipaddress.ip_address(ip)
            if not address.is_private:
                return jsonify(error="Private LAN IP required"), 400
        except ValueError:
            return jsonify(error="Invalid IP address"), 400

        if not label:
            return jsonify(error="Camera name required"), 400

        try:
            conn.execute(
                "INSERT INTO cameras(label, ip) VALUES (?, ?)",
                (label, ip)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify(error="Camera already registered"), 409

    rows = conn.execute(
        "SELECT * FROM cameras ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@network.route("/api/network/export")
def export_report():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY id DESC LIMIT 500"
    ).fetchall()
    cams = conn.execute("SELECT * FROM cameras").fetchall()
    conn.close()

    report = {
        "project": "TORDISSX86 OSINT",
        "generated": datetime.now().isoformat(),
        "devices": [dict(r) for r in rows],
        "authorized_camera_inventory": [dict(r) for r in cams]
    }

    return jsonify(report)
