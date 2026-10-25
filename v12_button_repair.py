from pathlib import Path
from flask import Blueprint, request, render_template_string, abort
import ast
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
button_bp = Blueprint("v12_button_repair", __name__, url_prefix="/v12/tools")

def local_only():
    if request.remote_addr not in ("127.0.0.1", "::1"):
        abort(403)

def get_modules():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "MODULES"
                   for t in node.targets):
                return ast.literal_eval(node.value)
    return {}

PAGE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORDISSX86 Button Repair</title>
<style>
body{background:#07110e;color:#eafff3;font-family:Arial;padding:15px}
.card{background:#10251c;border:1px solid #236b4b;border-radius:12px;padding:14px;margin:10px 0}
a,button{color:#42e69b}
a{display:inline-block;padding:9px}
textarea{width:100%;min-height:110px;background:#07110e;color:white;border:1px solid #42e69b;padding:9px}
button{background:#164b32;border:1px solid #42e69b;padding:12px;border-radius:8px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#07110e;padding:12px}
small{color:#a8cbb7}
</style>
</head>
<body>
<h1>TORDISSX86</h1>
<h2>V12 BUTTON REPAIR CENTER</h2>
<p><a href="/v12/integrations/">Integration Center</a>
<a href="/v12/control">Control Center</a></p>

{% if selected %}
<div class="card">
<h3>{{ selected[0] }}</h3>
<p><small>{{ selected[1] }}</small></p>
<form method="post">
<label>Input ya module (weka majibu kwa mistari tofauti):</label>
<textarea name="module_input" placeholder="Andika input inayohitajika na module..."></textarea>
<br><br><button type="submit">RUN MODULE</button>
</form>
</div>
{% endif %}

{% if output is not none %}
<div class="card">
<h3>Execution Result</h3>
<p>Status: {{ status }}</p>
<pre>{{ output }}</pre>
</div>
{% endif %}

<h2>Available Modules</h2>
{% for number, name, filename in modules %}
<div class="card">
<b>{{ number }}. {{ name }}</b><br>
<small>{{ filename }}</small><br>
<a href="/v12/tools/{{ number }}">OPEN MODULE</a>
</div>
{% endfor %}
<p><small>Modules zinaendeshwa ndani ya project. Tumia network tools kwenye mifumo unayomiliki au umepewa ruhusa ya kuijaribu.</small></p>
</body>
</html>
"""

@button_bp.route("/", methods=["GET"])
def index():
    local_only()
    modules = get_modules()
    items = [(k, v[0], v[1]) for k, v in modules.items()]
    return render_template_string(PAGE, modules=items,
                                  selected=None, output=None, status=None)

@button_bp.route("/<int:number>", methods=["GET", "POST"])
def run_module(number):
    local_only()
    modules = get_modules()

    if number not in modules:
        abort(404)

    name, filename = modules[number]
    path = (ROOT / filename).resolve()

    if path.parent != ROOT or not path.is_file() or path.suffix != ".py":
        abort(404)

    output = None
    status = None

    if request.method == "POST":
        supplied = request.form.get("module_input", "")
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                input=supplied + "\n",
                text=True,
                capture_output=True,
                cwd=str(ROOT),
                timeout=20
            )
            output = (result.stdout or "") + (result.stderr or "")
            status = "EXIT " + str(result.returncode)
            if not output.strip():
                output = "Module imemaliza bila kutoa maandishi."
        except subprocess.TimeoutExpired:
            output = "Module imezidi muda wa sekunde 20. Jaribu input fupi."
            status = "TIMEOUT"
        except Exception as exc:
            output = str(exc)
            status = "ERROR"

    return render_template_string(
        PAGE,
        modules=[(k, v[0], v[1]) for k, v in modules.items()],
        selected=(name, filename),
        output=output,
        status=status
    )
