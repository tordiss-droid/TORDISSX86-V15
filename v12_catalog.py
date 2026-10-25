
from flask import Blueprint, render_template_string
from pathlib import Path
import ast

catalog = Blueprint("v12_catalog", __name__, url_prefix="/v12")
ROOT = Path(__file__).resolve().parent

GROUPS = {
    "OSINT & Intelligence": [
        "osint", "profile", "username", "posts",
        "master_search", "advanced_osint",
        "osint_search", "domain_intel", "dns_intel",
        "url_analyzer", "web_intel"
    ],
    "Cases & Evidence": [
        "case_manager", "case_search", "case_analytics",
        "evidence_vault", "forensics", "timeline", "reports"
    ],
    "Network & Security": [
        "network", "network_diagnostics", "network_security",
        "security_audit", "system_info", "system_health",
        "integrity_monitor", "file_integrity", "log_analyzer"
    ],
    "Tools & Learning": [
        "diagnostics", "password_lab", "password_generator",
        "encryption_lab", "learning_center", "image_meta",
        "export", "unified_reports"
    ]
}

def category(filename):
    stem = Path(filename).stem.lower()
    for group, names in GROUPS.items():
        if stem in names:
            return group
    return "Other Modules"

def launcher_modules():
    tree = ast.parse(
        (ROOT / "app.py").read_text(encoding="utf-8")
    )

    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(t, ast.Name) and t.id == "MODULES"
                for t in node.targets
            ):
                return ast.literal_eval(node.value)

    return {}

@catalog.get("/modules")
def modules():
    launcher = launcher_modules()
    mapped = {
        str(value[1]): (number, value[0])
        for number, value in launcher.items()
    }

    files = sorted(
        p for p in ROOT.glob("*.py")
        if not p.name.startswith((
            "web_panel_before_", "app_before_",
            "v12_catalog_before_", "backup"
        ))
    )

    items = []

    for p in files:
        entry = mapped.get(p.name)
        items.append({
            "name": p.stem.replace("_", " ").title(),
            "file": p.name,
            "group": category(p.name),
            "number": entry[0] if entry else None,
            "available": entry is not None
        })

    return render_template_string("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORDISSX86 Module Center</title>
<style>
body{background:#07110e;color:#eafff3;font-family:Arial;padding:16px}
h1,h2{color:#42e69b}
a{color:#42e69b}
.nav a{margin-right:12px}
.card{background:#10251c;border:1px solid #236b4b;
border-radius:10px;padding:14px;margin:10px 0}
small{color:#a8cbb7}
input{width:100%;box-sizing:border-box;padding:12px;
background:#10251c;color:white;border:1px solid #347c59;
border-radius:8px}
.action{display:inline-block;background:#164b32;
border:1px solid #42e69b;padding:10px 14px;
border-radius:8px;text-decoration:none;margin-top:10px}
.status{font-size:12px;color:#42e69b}
.disabled{color:#a8cbb7}
</style>
</head>
<body>
<h1>TORDISSX86 V12</h1>
<h2>UNIFIED MODULE CENTER</h2>

<div class="nav">
<a href="/v12">Main Center</a>
<a href="/v12/manage/">Workspace</a>
<a href="/v12/reports">Reports</a>
<a href="/v12/cases">Cases</a>
<a href="/v12/tools/">Tool Runner</a>
<a href="/v12/integrations/">Integration Center</a>
</div>

<p>Modules discovered: {{ items|length }}</p>
<p>Runnable launcher modules: {{ runnable }}</p>

<input id="filter" placeholder="Search modules..."
oninput="filterModules()">

{% for group in groups %}
<h2>{{ group }}</h2>
{% for item in items if item.group == group %}
<div class="card module">
<b>{{ item.name }}</b><br>
<small>{{ item.file }}</small><br>

{% if item.available %}
<span class="status">LAUNCHER MAPPED</span><br>
<a class="action" href="/v12/tools/{{ item.number }}">
OPEN & RUN
</a>
{% else %}
<p class="disabled">SOURCE ONLY — haijaunganishwa kwenye launcher.</p>
{% endif %}
</div>
{% endfor %}
{% endfor %}

<script>
function filterModules(){
 const q=document.getElementById('filter').value.toLowerCase();
 document.querySelectorAll('.module').forEach(el=>{
  el.style.display=el.innerText.toLowerCase().includes(q)
   ? 'block':'none';
 });
}
</script>
</body>
</html>
""",
        items=items,
        groups=list(GROUPS.keys()) + ["Other Modules"],
        runnable=sum(x["available"] for x in items)
    )
