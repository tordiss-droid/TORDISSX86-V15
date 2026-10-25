from pathlib import Path
from flask import Blueprint, render_template_string
import ast
import json
from datetime import date, datetime

integration = Blueprint(
    "v12_integration",
    __name__,
    url_prefix="/v12/integrations"
)

ROOT = Path(__file__).resolve().parent

EXCLUDED = {
    "__pycache__", ".git", ".venv",
    "venv", "backups", "recovered_versions"
}

def module_data():
    result = []

    try:
        tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))

        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue

            if not any(
                isinstance(target, ast.Name)
                and target.id == "MODULES"
                for target in node.targets
            ):
                continue

            modules = ast.literal_eval(node.value)

            for number, value in modules.items():
                name, filename = value
                path = ROOT / filename

                status = "MISSING"

                if path.is_file():
                    try:
                        ast.parse(path.read_text(encoding="utf-8"))
                        status = "SYNTAX OK"
                    except Exception:
                        status = "SYNTAX ERROR"

                result.append({
                    "number": number,
                    "name": name,
                    "file": filename,
                    "status": status
                })

            break

    except Exception as exc:
        result.append({
            "number": "-",
            "name": "Menu inspection error",
            "file": str(exc),
            "status": "ERROR"
        })

    return result


def case_data():
    folder = ROOT / "cases"
    files = []

    if folder.exists():
        files = [
            p for p in folder.rglob("*")
            if p.is_file()
        ]

    today = date.today()
    today_count = 0
    month_count = 0

    for path in files:
        try:
            modified = datetime.fromtimestamp(path.stat().st_mtime)
            if modified.date() == today:
                today_count += 1
            if modified.strftime("%Y-%m") == today.strftime("%Y-%m"):
                month_count += 1
        except OSError:
            pass

    return {
        "total": len(files),
        "today": today_count,
        "month": month_count
    }


def report_data():
    folders = [
        "reports",
        "dns_reports",
        "domain_reports",
        "forensics_reports",
        "learning_reports",
        "network_reports",
        "security_reports",
        "evidence"
    ]

    files = []

    for name in folders:
        folder = ROOT / name
        if folder.exists():
            files.extend(
                p for p in folder.rglob("*")
                if p.is_file()
            )

    files = sorted(
        set(files),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return {
        "total": len(files),
        "recent": [
            {
                "name": p.name,
                "folder": str(p.parent.relative_to(ROOT)),
                "date": datetime.fromtimestamp(
                    p.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M")
            }
            for p in files[:15]
        ]
    }


def diagnostics():
    files = [
        p for p in ROOT.rglob("*.py")
        if not any(part in EXCLUDED for part in p.parts)
    ]

    good = 0
    bad = 0

    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            good += 1
        except Exception:
            bad += 1

    return {
        "total": len(files),
        "good": good,
        "bad": bad
    }


def test_data():
    folder = ROOT / "v12_data"
    names = [
        "FINAL_TEST_REPORT.json",
        "RUNTIME_AUDIT.json",
        "TOOL_AUDIT.json"
    ]

    data = {}

    for name in names:
        path = folder / name
        if path.exists():
            try:
                data[name] = json.loads(
                    path.read_text(encoding="utf-8")
                )
            except Exception:
                data[name] = {"error": "Cannot read report"}

    return data


@integration.get("/")
def home():
    modules = module_data()
    cases = case_data()
    reports = report_data()
    health = diagnostics()
    tests = test_data()

    ready = sum(x["status"] == "SYNTAX OK" for x in modules)
    missing = sum(x["status"] == "MISSING" for x in modules)
    errors = sum(x["status"] == "SYNTAX ERROR" for x in modules)

    return render_template_string("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TORDISSX86 Integration Center</title>
<style>
body {
 background:#07110e;color:#eafff3;
 font-family:Arial,sans-serif;padding:16px
}
h1,h2 {color:#42e69b}
.card {
 background:#10251c;border:1px solid #236b4b;
 border-radius:12px;padding:15px;margin:12px 0;
 overflow-wrap:anywhere
}
.grid {
 display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
 gap:10px
}
.metric {
 background:#10251c;border:1px solid #236b4b;
 border-radius:10px;padding:13px
}
.number {font-size:25px;color:#42e69b;font-weight:bold}
small {color:#a8cbb7}
table {width:100%;border-collapse:collapse}
td,th {
 text-align:left;padding:9px;border-bottom:1px solid #28513e;
 font-size:13px
}
a {color:#42e69b}
.good {color:#42e69b}
.bad {color:#ff8585}
.warn {color:#ffd479}
</style>
</head>
<body>

<h1>TORDISSX86 V12</h1>
<h2>INTEGRATION CENTER</h2>\n<p><a href="/v12/tools/">OPEN BUTTON REPAIR CENTER</a></p>
<p><a href="/v12/control">Control Center</a> |
<a href="/v12/modules">Module Center</a> |
<a href="/v12/report-engine">Report Engine</a></p>

<div class="grid">
 <div class="metric">
  <div class="number">{{ modules|length }}</div>
  <small>Menu Modules</small>
 </div>
 <div class="metric">
  <div class="number">{{ ready }}</div>
  <small>Syntax OK</small>
 </div>
 <div class="metric">
  <div class="number">{{ cases.total }}</div>
  <small>Case Files</small>
 </div>
 <div class="metric">
  <div class="number">{{ reports.total }}</div>
  <small>Report Files</small>
 </div>
 <div class="metric">
  <div class="number">{{ health.good }}</div>
  <small>Python Syntax OK</small>
 </div>
</div>

<div class="card">
<h2>Module Status</h2>
<p class="good">Syntax OK: {{ ready }}</p>
<p class="bad">Missing: {{ missing }}</p>
<p class="warn">Syntax errors: {{ errors }}</p>
<table>
<tr><th>Option</th><th>Module</th><th>Status</th></tr>
{% for m in modules %}
<tr>
<td>{{ m.number }}</td>
<td>{{ m.name }}<br><small>{{ m.file }}</small></td>
<td>{{ m.status }}</td>
</tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>Case Analytics</h2>
<p>Total case files: <b>{{ cases.total }}</b></p>
<p>Modified today: {{ cases.today }}</p>
<p>Modified this month: {{ cases.month }}</p>
<a href="/v12/cases">Open Case Center</a> |
<a href="/v12/manage/">Workspace</a>
</div>

<div class="card">
<h2>Unified Reports</h2>
<p>Total discovered report/evidence files: {{ reports.total }}</p>
<a href="/v12/reports">Open Reports Center</a>
<table>
<tr><th>File</th><th>Folder</th><th>Date</th></tr>
{% for r in reports.recent %}
<tr>
<td>{{ r.name }}</td>
<td>{{ r.folder }}</td>
<td>{{ r.date }}</td>
</tr>
{% else %}
<tr><td colspan="3">No report files found.</td></tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>System Diagnostics</h2>
<p>Python files: {{ health.total }}</p>
<p class="good">Syntax OK: {{ health.good }}</p>
<p class="bad">Syntax errors: {{ health.bad }}</p>
<a href="/v12/health/">Open Health Center</a>
</div>

<div class="card">
<h2>Test Reports</h2>
{% for name, data in tests.items() %}
<p><b>{{ name }}</b></p>
{% if data.passed is defined %}
<p class="good">Passed: {{ data.passed }}</p>
<p>Failed: {{ data.failed }}</p>
{% elif data.counts is defined %}
<p>{{ data.counts }}</p>
{% else %}
<p>Report available.</p>
{% endif %}
{% else %}
<p>No test reports found.</p>
{% endfor %}
</div>

<p><small>
TORDISSX86 V12 | Integration Center |
Static diagnostics do not prove runtime functionality.
</small></p>
</body>
</html>
""",
        modules=modules,
        ready=ready,
        missing=missing,
        errors=errors,
        cases=cases,
        reports=reports,
        health=health,
        tests=tests
    )
