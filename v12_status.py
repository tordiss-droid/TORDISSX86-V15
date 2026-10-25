from flask import Blueprint, current_app, jsonify, render_template_string
from pathlib import Path
import os
import time

status_bp = Blueprint("v12_status", __name__, url_prefix="/v12/status")
ROOT = Path(__file__).resolve().parent
STARTED = time.time()

@status_bp.get("/")
def dashboard():
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        routes.append({
            "path": str(rule),
            "endpoint": rule.endpoint,
            "methods": ", ".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        })

    modules = sorted(ROOT.glob("*.py"))
    return render_template_string("""
    <!doctype html>
    <html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>TORDISSX86 Live Monitor</title>
    <style>
    body{background:#07110e;color:#eafff3;font-family:Arial;padding:18px}
    h1,h2{color:#42e69b}
    .card{background:#10251c;border:1px solid #236b4b;
    border-radius:10px;padding:14px;margin:10px 0;overflow-wrap:anywhere}
    small{color:#a8cbb7}
    a{color:#42e69b}
    </style></head><body>
    <h1>TORDISSX86</h1><h2>V12 LIVE SYSTEM MONITOR</h2>
    <p><a href="/v12/control">Control Center</a> |
    <a href="/v12">Main Center</a></p>
    <div class="card">
    <b>SERVER STATUS: ONLINE</b>
    <p>Registered routes: {{ routes|length }}</p>
    <p>Python modules: {{ modules|length }}</p>
    <p>Process ID: {{ pid }}</p>
    </div>
    <h2>Registered Routes</h2>
    {% for r in routes %}
    <div class="card">
    <b>{{ r.path }}</b><br>
    <small>{{ r.endpoint }} | {{ r.methods }}</small>
    </div>
    {% endfor %}
    <h2>Project Modules</h2>
    {% for m in modules %}
    <div class="card">{{ m }}</div>
    {% endfor %}
    </body></html>
    """, routes=routes, modules=[m.name for m in modules],
       pid=os.getpid())

@status_bp.get("/api")
def api():
    return jsonify({
        "application": "TORDISSX86",
        "version": "V12",
        "status": "online",
        "routes": [
            {"path": str(r), "endpoint": r.endpoint}
            for r in current_app.url_map.iter_rules()
            if r.endpoint != "static"
        ]
    })
