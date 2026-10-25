from flask import Blueprint, render_template_string, request
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

engine = Blueprint("v12_reports_engine", __name__, url_prefix="/v12")

ROOT = Path(__file__).resolve().parent
REPORT_DIRS = [
    ROOT / "reports",
    ROOT / "dns_reports",
    ROOT / "domain_reports",
    ROOT / "network_reports",
    ROOT / "security_reports",
    ROOT / "forensics_reports",
    ROOT / "learning_reports",
    ROOT / "exports",
]

INDEX = ROOT / "v12_data" / "report_index.json"
INDEX.parent.mkdir(parents=True, exist_ok=True)

def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def scan_reports():
    records = []

    for folder in REPORT_DIRS:
        if not folder.exists():
            continue

        for path in folder.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue

            try:
                stat = path.stat()
                records.append({
                    "name": path.name,
                    "location": str(path.relative_to(ROOT)),
                    "extension": path.suffix.lower() or "none",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(
                        stat.st_mtime, timezone.utc
                    ).isoformat(),
                    "sha256": file_hash(path)
                })
            except (OSError, ValueError):
                continue

    records.sort(key=lambda x: x["modified"], reverse=True)

    INDEX.write_text(
        json.dumps({
            "generated": datetime.now(timezone.utc).isoformat(),
            "total": len(records),
            "reports": records
        }, indent=2),
        encoding="utf-8"
    )
    return records

PAGE = """
<!doctype html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORDISSX86 Report Engine</title>
<style>
body{background:#07110e;color:#eafff3;font-family:Arial;padding:18px}
h1,h2{color:#42e69b}
a{color:#42e69b}
input,button{padding:12px;border-radius:8px;margin:8px 0}
input{width:100%;box-sizing:border-box;background:#10251c;color:white;border:1px solid #347c59}
button{background:#176b43;color:white;border:0;font-weight:bold}
.card{background:#10251c;border:1px solid #236b4b;padding:14px;margin:10px 0;border-radius:10px;overflow-wrap:anywhere}
small{color:#a8cbb7}
</style></head><body>
<h1>TORDISSX86</h1>
<h2>V12 REPORT ENGINE</h2>
<p><a href="/v12">Main Center</a> |
<a href="/v12/modules">Modules</a> |
<a href="/v12/manage/">Workspace</a></p>

<h2>{{ reports|length }} Reports Indexed</h2>
<form method="get">
<input name="q" value="{{ query }}" placeholder="Search report name or location">
<button>SEARCH</button>
</form>
<form method="post" action="/v12/report-engine/refresh">
<button>REFRESH REPORT INDEX</button>
</form>
{% for r in reports %}
<div class="card">
<b>{{ r.name }}</b><br>
<small>{{ r.location }}</small><br>
<small>Type: {{ r.extension }} | Size: {{ r.size }} bytes</small><br>
<small>Modified: {{ r.modified }}</small><br>
<small>SHA-256: {{ r.sha256 }}</small>
</div>
{% else %}
<p>No reports found.</p>
{% endfor %}
</body></html>
"""

@engine.get("/report-engine")
def report_home():
    records = scan_reports()
    query = request.args.get("q", "").strip().lower()

    if query:
        records = [
            r for r in records
            if query in r["name"].lower()
            or query in r["location"].lower()
        ]

    return render_template_string(PAGE, reports=records, query=query)

@engine.post("/report-engine/refresh")
def report_refresh():
    from flask import redirect
    scan_reports()
    return redirect("/v12/report-engine")
