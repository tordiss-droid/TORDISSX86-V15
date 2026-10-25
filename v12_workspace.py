from flask import Blueprint, request, redirect, url_for, render_template_string, flash
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import re

workspace = Blueprint("workspace", __name__, url_prefix="/v12/manage")

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
EVIDENCE = ROOT / "evidence"
REPORTS = ROOT / "reports"

for folder in (CASES, EVIDENCE, REPORTS):
    folder.mkdir(parents=True, exist_ok=True)

PAGE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORDISSX86 Workspace</title>
<style>
body{margin:0;background:#07110e;color:#eafff3;font-family:Arial;padding:18px}
h1,h2{color:#42e69b}
nav a{color:#42e69b;margin-right:14px}
.panel{background:#10251c;border:1px solid #236b4b;border-radius:12px;padding:16px;margin:16px 0}
input,textarea,button{box-sizing:border-box;width:100%;padding:12px;margin:7px 0;
border-radius:7px;border:1px solid #347c59;background:#071a12;color:white}
button{background:#176b43;font-weight:bold;cursor:pointer}
.item{padding:10px;border-bottom:1px solid #24513c;overflow-wrap:anywhere}
small{color:#a8cbb7}
a{color:#56e6a1}
</style>
</head>
<body>
<h1>TORDISSX86 V12</h1>
<nav><a href="/v12">Main Center</a><a href="/">Original Dashboard</a></nav>

<div class="panel">
<h2>Create Case</h2>
<form method="post" action="{{ url_for('workspace.create_case') }}">
<input name="title" placeholder="Case title" maxlength="80" required>
<textarea name="description" placeholder="Case description" maxlength="2000"></textarea>
<button type="submit">CREATE CASE</button>
</form>
</div>

<div class="panel">
<h2>Save Evidence Note</h2>
<form method="post" action="{{ url_for('workspace.create_evidence') }}">
<input name="case_id" placeholder="Case ID" required>
<input name="title" placeholder="Evidence title" maxlength="80" required>
<textarea name="content" placeholder="Evidence notes / observations" maxlength="10000" required></textarea>
<button type="submit">SAVE EVIDENCE + SHA256</button>
</form>
</div>

<div class="panel">
<h2>Cases ({{ cases|length }})</h2>
{% for c in cases %}
<div class="item"><b>{{ c.title }}</b><br>
<small>ID: {{ c.id }} | Created: {{ c.created }}</small><br>
{{ c.description }}
</div>
{% else %}<small>No cases created yet.</small>{% endfor %}
</div>

<div class="panel">
<h2>Evidence Records ({{ evidence|length }})</h2>
{% for e in evidence %}
<div class="item"><b>{{ e.title }}</b><br>
<small>Case: {{ e.case_id }} | {{ e.created }}</small><br>
<small>SHA-256: {{ e.sha256 }}</small>
</div>
{% else %}<small>No evidence records yet.</small>{% endfor %}
</div>

<div class="panel">
<h2>Reports ({{ reports|length }})</h2>
{% for r in reports %}
<div class="item">{{ r.name }}<br><small>{{ r.path }}</small></div>
{% else %}<small>No reports found.</small>{% endfor %}
</div>
</body></html>
"""

def safe_id(value):
    return re.sub(r"[^a-zA-Z0-9_-]", "", value)[:60]

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

@workspace.get("/")
def home():
    cases = []
    for p in CASES.glob("*/case.json"):
        data = load_json(p)
        if data:
            cases.append(data)
    cases.sort(key=lambda x: x.get("created", ""), reverse=True)

    evidence = []
    for p in EVIDENCE.glob("*/*.json"):
        data = load_json(p)
        if data:
            evidence.append(data)
    evidence.sort(key=lambda x: x.get("created", ""), reverse=True)

    reports = []
    for p in REPORTS.rglob("*"):
        if p.is_file():
            reports.append({"name": p.name, "path": str(p.relative_to(ROOT))})
    reports.sort(key=lambda x: x["path"], reverse=True)

    return render_template_string(
        PAGE, cases=cases[:100], evidence=evidence[:100], reports=reports[:100]
    )

@workspace.post("/case/create")
def create_case():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title:
        return "Case title is required", 400

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = safe_id(title.lower().replace(" ", "_")) or "case"
    case_id = f"{stamp}_{slug}"
    folder = CASES / case_id
    folder.mkdir(parents=True, exist_ok=False)

    data = {
        "id": case_id,
        "title": title[:80],
        "description": description[:2000],
        "created": datetime.now(timezone.utc).isoformat()
    }
    (folder / "case.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return redirect(url_for("workspace.home"))

@workspace.post("/evidence/create")
def create_evidence():
    case_id = safe_id(request.form.get("case_id", "").strip())
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not case_id or not title or not content:
        return "Missing required fields", 400
    if not (CASES / case_id / "case.json").is_file():
        return "Case ID not found. Create the case first.", 404

    created = datetime.now(timezone.utc).isoformat()
    raw = content.encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    record_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    folder = EVIDENCE / case_id
    folder.mkdir(parents=True, exist_ok=True)

    data = {
        "id": record_id,
        "case_id": case_id,
        "title": title[:80],
        "content": content[:10000],
        "created": created,
        "sha256": digest
    }
    (folder / f"{record_id}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return redirect(url_for("workspace.home"))
