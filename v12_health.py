from flask import Blueprint, render_template_string
from pathlib import Path
import importlib.util
import sys
import hashlib
import json

health = Blueprint("v12_health", __name__, url_prefix="/v12/health")
ROOT = Path(__file__).resolve().parent

REQUIRED_FOLDERS = [
    "reports", "cases", "evidence", "exports",
    "v12_data", "static", "templates"
]

DEPENDENCIES = [
    "flask", "requests", "dns", "phonenumbers", "PIL"
]

def inspect_project():
    modules = sorted(
        p for p in ROOT.glob("*.py")
        if not p.name.startswith("web_panel_before_")
        and not p.name.startswith("backup")
    )

    module_results = []
    for p in modules:
        try:
            source = p.read_bytes()
            compile(source, str(p), "exec")
            module_results.append({
                "name": p.name,
                "status": "OK",
                "hash": hashlib.sha256(source).hexdigest()
            })
        except Exception as exc:
            module_results.append({
                "name": p.name,
                "status": "ERROR",
                "hash": str(exc)
            })

    folders = [
        {"name": name, "status": "READY" if (ROOT / name).is_dir() else "MISSING"}
        for name in REQUIRED_FOLDERS
    ]

    dependencies = [
        {
            "name": name,
            "status": "INSTALLED" if importlib.util.find_spec(name) else "MISSING"
        }
        for name in DEPENDENCIES
    ]

    return module_results, folders, dependencies

@health.get("/")
def home():
    modules, folders, dependencies = inspect_project()
    errors = sum(x["status"] == "ERROR" for x in modules)
    missing = sum(x["status"] == "MISSING" for x in folders)
    missing += sum(x["status"] == "MISSING" for x in dependencies)

    status = "HEALTHY" if errors == 0 and missing == 0 else "CHECK REQUIRED"

    return render_template_string("""
    <!doctype html>
    <html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>TORDISSX86 Health Center</title>
    <style>
    body{background:#07110e;color:#eafff3;font-family:Arial;padding:18px}
    h1,h2{color:#42e69b}
    a{color:#42e69b}
    .card{background:#10251c;border:1px solid #236b4b;
    border-radius:10px;padding:14px;margin:10px 0;overflow-wrap:anywhere}
    .ok{color:#42e69b}.bad{color:#ff7777}
    small{color:#a8cbb7}
    </style></head><body>
    <h1>TORDISSX86 V12</h1>
    <h2>System Health & Integrity</h2>
    <p><a href="/v12">Main Center</a> |
    <a href="/v12/modules">Modules</a> |
    <a href="/v12/report-engine">Reports</a></p>

    <div class="card">
    <h2>{{ status }}</h2>
    <p>Python: {{ python }}</p>
    <p>Modules: {{ modules|length }}</p>
    <p>Module errors: {{ errors }}</p>
    </div>

    <h2>Module Integrity</h2>
    {% for x in modules %}
    <div class="card">
    <b>{{ x.name }}</b> —
    <span class="{{ 'ok' if x.status == 'OK' else 'bad' }}">{{ x.status }}</span>
    {% if x.status == 'OK' %}<br><small>SHA-256: {{ x.hash }}</small>
    {% else %}<br><small>{{ x.hash }}</small>{% endif %}
    </div>
    {% endfor %}

    <h2>Project Folders</h2>
    {% for x in folders %}
    <div class="card">{{ x.name }} —
    <span class="{{ 'ok' if x.status == 'READY' else 'bad' }}">{{ x.status }}</span>
    </div>
    {% endfor %}

    <h2>Dependencies</h2>
    {% for x in dependencies %}
    <div class="card">{{ x.name }} —
    <span class="{{ 'ok' if x.status == 'INSTALLED' else 'bad' }}">{{ x.status }}</span>
    </div>
    {% endfor %}
    </body></html>
    """, modules=modules, folders=folders,
       dependencies=dependencies, errors=errors,
       status=status, python=sys.version.split()[0])
