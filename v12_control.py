from flask import Blueprint, render_template_string
from pathlib import Path

control = Blueprint("v12_control", __name__, url_prefix="/v12")
ROOT = Path(__file__).resolve().parent

PAGE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORDISSX86 Control Center</title>
<style>
body{background:#07110e;color:#eafff3;font-family:Arial;padding:18px}
h1{color:#42e69b;letter-spacing:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.card{display:block;background:#10251c;border:1px solid #236b4b;
border-radius:12px;padding:18px;text-decoration:none;color:white}
.card b{color:#42e69b;display:block;margin-bottom:10px}
small{color:#a8cbb7}
.card:hover{background:#173b2a}
.status{color:#42e69b;font-size:12px}
</style>
</head>
<body>
<h1>TORDISSX86</h1>
<p>V12 UNIFIED CONTROL CENTER</p>
<p>All project systems in one place.</p>
<div class="grid">
{% for x in items %}
<a class="card" href="{{ x.url }}">
<b>{{ x.name }}</b>
<small>{{ x.description }}</small><br><br>
<span class="status">{{ x.status }}</span>
</a>
{% endfor %}
</div>
<p style="margin-top:30px;color:#83a997">TORDISSX86 • Local Security Workspace</p>
</body>
</html>
"""

@control.get("/control")
def home():
    links = [
        ("Main Dashboard", "/v12", "Unified project dashboard"),
        ("Module Center", "/v12/modules", "Browse available Python modules"),
        ("OSINT Intelligence", "/intelligence", "Public information analysis"),
        ("Workspace", "/v12/manage/", "Cases and evidence notes"),
        ("Reports Engine", "/v12/report-engine", "Search and verify report files"),
        ("System Health", "/v12/health/", "Project integrity and dependencies"),
        ("Reports", "/v12/reports", "Existing report files"),
        ("Cases", "/v12/cases", "Existing case files"),
        ("Evidence", "/v12/evidence", "Existing evidence files"),
        ("Diagnostics", "/module/16", "Project diagnostics"),
    ]

    items = []
    for name, url, description in links:
        if url == "/v12":
            status = "AVAILABLE"
        elif url == "/intelligence":
            status = "CHECK ROUTE"
        else:
            status = "OPEN SECTION"
        items.append({
            "name": name, "url": url,
            "description": description, "status": status
        })

    return render_template_string(PAGE, items=items)
