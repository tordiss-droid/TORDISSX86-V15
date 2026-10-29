import os
import ast
import sys
import json
import secrets
import string
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import combination_engine_v15 as combo

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

app = Flask(__name__)

# LOCALHOST ONLY
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "4444"))

# Interactive module sessions
SESSIONS = {}
SESSION_LOCK = threading.RLock()



# PUBLIC DEPLOYMENT SECURITY
# Default mode is read-only for public visitors.
PUBLIC_READ_ONLY = os.environ.get(
    "TORDISSX86_PUBLIC_READ_ONLY", "1"
).strip().lower() in ("1", "true", "yes", "on")

PUBLIC_GET_PATHS = {
    "/",
    "/health",
    "/api/modules",
    "/network",
    "/api/osint/power",
    "/api/v15/status",
    "/api/v15/reports",
    "/api/system/ping",
}

PUBLIC_POST_PATHS = {"/api/v15/analyze"}

@app.before_request
def protect_public():
    if not PUBLIC_READ_ONLY:
        return None

    # Public static assets
    if request.endpoint == "static" and request.method == "GET":
        return None

    # Approved public GET endpoints
    if request.method == "GET" and request.path in PUBLIC_GET_PATHS:
        return None

    # Approved public POST endpoints
    if request.method == "POST" and request.path in PUBLIC_POST_PATHS:
        return None

    return jsonify({
        "error": "This feature requires authorized access"
    }), 403


# MODULE INVENTORY
# ==========================================

def find_modules():
    modules = []
    source = ROOT / "app.py"

    if source.exists():
        try:
            tree = ast.parse(source.read_text(errors="ignore"))

            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue

                found = any(
                    isinstance(target, ast.Name)
                    and target.id == "MODULES"
                    for target in node.targets
                )

                if not found:
                    continue

                data = ast.literal_eval(node.value)

                if not isinstance(data, dict):
                    continue

                for number, value in data.items():
                    strings = []

                    def collect(obj):
                        if isinstance(obj, str):
                            strings.append(obj)
                        elif isinstance(obj, (tuple, list)):
                            for item in obj:
                                collect(item)
                        elif isinstance(obj, dict):
                            for k, v in obj.items():
                                collect(k)
                                collect(v)

                    collect(value)

                    filename = next(
                        (x for x in strings if x.endswith(".py")),
                        None
                    )

                    if not filename:
                        continue

                    path = (ROOT / filename).resolve()

                    if path.parent != ROOT or not path.is_file():
                        continue

                    name = next(
                        (
                            x for x in strings
                            if x != filename
                            and not x.endswith(".py")
                        ),
                        Path(filename).stem.replace("_", " ").title()
                    )

                    if filename in ("app.py", "web_panel.py"):
                        continue

                    modules.append({
                        "number": str(number),
                        "name": name,
                        "file": filename,
                        "status": "READY"
                    })

                break

        except Exception as error:
            print("MODULE INVENTORY WARNING:", error)

    # Fallback inventory
    if not modules:
        excluded = {
            "app.py",
            "web_panel.py",
            "install_v12_unified.py"
        }

        for path in sorted(ROOT.glob("*.py")):
            if path.name in excluded:
                continue

            if path.name.startswith("v12_"):
                continue

            modules.append({
                "number": "-",
                "name": path.stem.replace("_", " ").title(),
                "file": path.name,
                "status": "FOUND"
            })

    return modules


def get_module(filename):
    for module in find_modules():
        if module["file"] == filename:
            path = (ROOT / filename).resolve()

            if path.parent == ROOT and path.is_file():
                return module, path

    return None, None


# ==========================================
# INTERACTIVE CLI ENGINE
# ==========================================

def read_process_output(session_id, process):
    try:
        for line in iter(process.stdout.readline, ""):
            with SESSION_LOCK:
                session = SESSIONS.get(session_id)

                if session:
                    session["output"] += line

                    if len(session["output"]) > 100000:
                        session["output"] = session["output"][-100000:]

    except Exception as error:
        with SESSION_LOCK:
            session = SESSIONS.get(session_id)
            if session:
                session["output"] += "\nOUTPUT ERROR: " + str(error)

    finally:
        process.stdout.close()

        with SESSION_LOCK:
            session = SESSIONS.get(session_id)

            if session:
                session["running"] = False
                session["exit_code"] = process.poll()


@app.route("/api/modules")
def api_modules():
    modules = find_modules()

    return jsonify({
        "count": len(modules),
        "modules": modules
    })


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(silent=True) or {}
    filename = str(data.get("file", ""))

    module, path = get_module(filename)

    if not module:
        return jsonify({"error": "Module not found or not allowed"}), 404

    try:
        process = subprocess.Popen(
            [sys.executable, "-u", str(path)],
            cwd=str(ROOT),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        session_id = secrets.token_urlsafe(18)

        with SESSION_LOCK:
            SESSIONS[session_id] = {
                "process": process,
                "output": "TORDISSX86 MODULE SESSION\n"
                          "Module: " + module["name"] + "\n"
                          "File: " + filename + "\n"
                          "------------------------------\n",
                "running": True,
                "exit_code": None
            }

        thread = threading.Thread(
            target=read_process_output,
            args=(session_id, process),
            daemon=True
        )
        thread.start()

        return jsonify({
            "success": True,
            "session": session_id,
            "module": module["name"]
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/output/<session_id>")
def api_output(session_id):
    with SESSION_LOCK:
        session = SESSIONS.get(session_id)

        if not session:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({
            "output": session["output"],
            "running": session["running"],
            "exit_code": session["exit_code"]
        })


@app.route("/api/input/<session_id>", methods=["POST"])
def api_input(session_id):
    data = request.get_json(silent=True) or {}
    value = str(data.get("input", ""))

    if len(value) > 10000:
        return jsonify({"error": "Input too long"}), 400

    with SESSION_LOCK:
        session = SESSIONS.get(session_id)

        if not session or not session["running"]:
            return jsonify({"error": "Session is not running"}), 400

        try:
            process = session["process"]
            process.stdin.write(value + "\n")
            process.stdin.flush()

            return jsonify({"success": True})

        except Exception as error:
            return jsonify({"error": str(error)}), 500


@app.route("/api/stop/<session_id>", methods=["POST"])
def api_stop(session_id):
    with SESSION_LOCK:
        session = SESSIONS.get(session_id)

        if not session:
            return jsonify({"error": "Session not found"}), 404

        process = session["process"]

        if process.poll() is None:
            process.terminate()

        return jsonify({"success": True})


# ==========================================
# PASSWORD GENERATOR GUI
# ==========================================

@app.route("/api/password", methods=["POST"])
def password_generator():
    data = request.get_json(silent=True) or {}

    try:
        length = int(data.get("length", 20))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid length"}), 400

    if not 12 <= length <= 64:
        return jsonify({"error": "Length must be 12-64"}), 400

    chars = string.ascii_letters + string.digits + "!@#$%^&*_-+="

    password = "".join(
        secrets.choice(chars) for _ in range(length)
    )

    return jsonify({
        "success": True,
        "password": password,
        "length": length
    })


# ==========================================
# REPORT ENGINE
# ==========================================

@app.route("/reports")
def reports_page():
    files = sorted(
        REPORTS.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return jsonify({
        "reports": [
            {
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(
                    f.stat().st_mtime
                ).isoformat()
            }
            for f in files
        ]
    })


# ==========================================
# MAIN WEB INTERFACE
# ==========================================

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>TORDISSX86 V14</title>

<style>

:root {
    --blue: #168bff;
    --cyan: #36d9ff;
    --bg: #030914;
    --panel: #091a2d;
    --border: #14528a;
    --text: #dcecff;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: Arial, sans-serif;
}

header {
    background: #061426;
    border-bottom: 1px solid var(--blue);
    padding: 20px;
}

.logo {
    color: var(--cyan);
    font-size: 26px;
    font-weight: bold;
    animation: blueBlink 1.6s infinite;
}

@keyframes blueBlink {
    0%,100% {
        text-shadow: 0 0 5px #168bff;
        opacity: 1;
    }
    50% {
        text-shadow: 0 0 22px #36d9ff;
        opacity: .72;
    }
}

.subtitle {
    color: #83b9e9;
    font-size: 12px;
    letter-spacing: 3px;
    margin-top: 8px;
}

nav {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 13px;
    background: #06101d;
    border-bottom: 1px solid #123b62;
}

nav button, .action {
    background: #0c2540;
    border: 1px solid var(--border);
    color: var(--cyan);
    padding: 11px 15px;
    border-radius: 6px;
    cursor: pointer;
}

nav button:hover, .action:hover {
    background: #123e68;
}

main {
    padding: 16px;
    max-width: 1200px;
    margin: auto;
}

h2 {
    color: var(--cyan);
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
    gap: 13px;
}

.card {
    background: var(--panel);
    border: 1px solid #174a78;
    border-radius: 9px;
    padding: 17px;
    margin: 12px 0;
    box-shadow: 0 0 9px #071d35;
}

.stat {
    font-size: 27px;
    font-weight: bold;
    color: var(--cyan);
}

.module {
    background: #09192a;
    border: 1px solid #14528a;
    border-radius: 8px;
    padding: 15px;
}

.module h3 {
    color: #66caff;
}

input, select {
    width: 100%;
    background: #020b16;
    color: white;
    border: 1px solid #1762a0;
    border-radius: 6px;
    padding: 12px;
    margin: 8px 0;
}

button {
    cursor: pointer;
}

.primary {
    background: #0879dc;
    color: white;
    padding: 12px 17px;
    border: 1px solid #36baff;
    border-radius: 6px;
    font-weight: bold;
}

.danger {
    background: #75222d;
    color: white;
    padding: 10px;
    border: 1px solid #d84a5a;
    border-radius: 6px;
}

.terminal {
    background: #01060d;
    color: #8ee0ff;
    border: 1px solid #168bff;
    border-radius: 8px;
    padding: 14px;
    height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    font-family: monospace;
    font-size: 13px;
}

.muted {
    color: #83a5c4;
    font-size: 12px;
}

.hidden {
    display: none;
}

.status {
    color: #36d9ff;
}

footer {
    padding: 25px;
    text-align: center;
    color: #5f8bb6;
}


/* TORDISSX86 V15 */
.v15-card {
    background: rgba(0, 25, 12, .92);
    border: 1px solid #087b43;
    border-radius: 18px;
    padding: 20px;
    margin: 16px 0;
    box-shadow: 0 0 18px rgba(0,255,100,.08);
}
.v15-card input, .v15-card select {
    width: 100%;
    box-sizing: border-box;
    margin: 10px 0;
    padding: 13px;
    border-radius: 12px;
    border: 1px solid #16834c;
    background: #06150d;
    color: #eaffef;
}
.v15-result {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: #020a05;
    border: 1px solid #17633b;
    border-radius: 12px;
    padding: 14px;
    min-height: 100px;
    color: #75ffad;
}
.v15-muted { color: #9bb9a5; }
.v15-button {
    background: #087b43;
    color: white;
    border: 0;
    border-radius: 12px;
    padding: 13px 20px;
    cursor: pointer;
    margin: 5px;
}

</style>
</head>

<body>

<header>
    <div class="logo">TORDISSX86</div>
    <div class="subtitle">
        CYBER OSINT COMMAND CENTER — VERSION 14
    </div>
</header>

<nav>
    <button onclick="showPage('dashboard')">Dashboard</button>
    <button onclick="showPage('modules')">Module Center</button>
<button onclick="showPage('v15lab')">V15 Combination Lab</button>
    <button onclick="showPage('terminal')">Interactive Terminal</button>
    <button onclick="showPage('password')">Password Generator</button>
    <button onclick="showPage('reports')">Reports</button>
    <button onclick="showPage('system')">System Status</button>
</nav>

<main>

<section id="dashboard">
    <h2>COMMAND DASHBOARD</h2>

    <div class="grid">
        <div class="card">
            <div class="stat" id="moduleCount">0</div>
            Detected Modules
        </div>

        <div class="card">
            <div class="stat">ONLINE</div>
            Local Web Server
        </div>

        <div class="card">
            <div class="stat">4444</div>
            Active Port
        </div>

        <div class="card">
            <div class="stat" id="reportCount">0</div>
            Saved Reports
        </div>
    </div>

    <div class="card">
        <h2>MODULE CONTROL</h2>
        <p>Launch your registered tools directly from this interface.</p>
        <button class="primary" onclick="showPage('modules')">
            OPEN MODULE CENTER
        </button>
    </div>

    <div class="card">
        <h2>LIVE SYSTEM STATUS</h2>
        <p id="systemStatus" class="status">Initializing...</p>
    </div>
</section>


<section id="modules" class="hidden">
    <h2>MODULE CENTER</h2>

    <input
        id="search"
        placeholder="Search modules..."
        oninput="renderModules()"
    >

    <div id="moduleGrid" class="grid"></div>
</section>



<section id="v15lab" class="hidden">
    <h2>TORDISSX86 V15 COMBINATION LAB</h2>

    <div class="v15-card">
        <h3>COMBINATION ENGINE</h3>
        <p class="v15-muted">
            Public-source research and basic technical intelligence.
            Use information you own or are authorized to examine.
        </p>
        <p id="v15Status" class="status">Checking engine...</p>

        <label for="v15Type">Analysis Type</label>
        <select id="v15Type">
            <option value="domain">Domain Intelligence</option>
            <option value="dns">DNS Records</option>
            <option value="email">Email Format / MX Check</option>
            <option value="phone">Phone Number Metadata</option>
            <option value="url">URL Analysis</option>
            <option value="username">Public Username Leads</option>
        </select>

        <label for="v15Value">Input</label>
        <input
            id="v15Value"
            type="text"
            maxlength="2048"
            placeholder="Enter a domain, URL, email, phone or username"
            autocomplete="off"
        >

        <button class="v15-button" id="v15Run" onclick="runV15Analysis()">
            RUN ANALYSIS
        </button>
        <button class="v15-button" onclick="loadV15Reports()">
            REFRESH REPORTS
        </button>
    </div>

    <div class="v15-card">
        <h3>ANALYSIS OUTPUT</h3>
        <pre id="v15Output" class="v15-result">Waiting for analysis...</pre>
    </div>

    <div class="v15-card">
        <h3>SAVED V15 REPORTS</h3>
        <div id="v15ReportList" class="v15-result">No reports loaded.</div>
    </div>
</section>

<section id="terminal" class="hidden">
    <h2>INTERACTIVE MODULE TERMINAL</h2>

    <div class="card">
        <p id="activeModule">No module selected</p>

        <div class="terminal" id="terminalOutput">
TORDISSX86 INTERACTIVE TERMINAL
Select a module from Module Center.
        </div>

        <input
            id="terminalInput"
            placeholder="Enter module input here..."
        >

        <button class="primary" onclick="sendInput()">
            SEND INPUT
        </button>

        <button class="danger" onclick="stopModule()">
            STOP MODULE
        </button>
    </div>
</section>


<section id="password" class="hidden">
    <h2>SECURE PASSWORD GENERATOR</h2>

    <div class="card">
        <label>Password Length</label>

        <input
            type="number"
            id="passLength"
            min="12"
            max="64"
            value="20"
        >

        <button class="primary" onclick="generatePassword()">
            GENERATE PASSWORD
        </button>

        <input id="passwordResult" readonly placeholder="Generated password">

        <button onclick="copyPassword()">COPY PASSWORD</button>
    </div>
</section>


<section id="reports" class="hidden">
    <h2>REPORT CENTER</h2>
    <div id="reportList"></div>
</section>


<section id="system" class="hidden">
    <h2>SYSTEM DIAGNOSTICS</h2>

    <div class="card">
        <p>Project: TORDISSX86</p>
        <p>Interface: V14</p>
        <p>Server Port: 4444</p>
        <p>Execution: Local Python subprocess</p>
        <p id="diagnosticModules"></p>
        <p id="diagnosticStatus"></p>
    </div>
</section>


<section id="osintPower" class="card">
<h2>OSINT POWER CONTROL</h2>
<p id="powerStatus" class="status">SYSTEM STANDBY</p>
<button class="primary" onclick="setOSINT('ON')">OSINT ON</button>
<button class="danger" onclick="setOSINT('OFF')">OSINT OFF</button>
</section>
<script>
async function setOSINT(command) {
    const response = await fetch("/api/osint/power", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({command})
    });
    const data = await response.json();
    document.getElementById("powerStatus").textContent =
        data.osint === "ON" ? "OSINT SYSTEM ACTIVE" : "OSINT SYSTEM STANDBY";
}
</script>

</main>

<footer>
    TORDISSX86 V14 | LOCAL CYBER RESEARCH PLATFORM
</footer>


<script>

let modules = [];
let activeSession = null;
let pollTimer = null;

function showPage(id) {
    document.querySelectorAll("main section").forEach(
        section => section.classList.add("hidden")
    );

    document.getElementById(id).classList.remove("hidden");

    if (id === "reports") loadReports();
    if (id === "v15lab") { loadV15Status(); loadV15Reports(); }
    if (id === "system") loadSystem();
}

async function loadModules() {
    const response = await fetch("/api/modules");
    const data = await response.json();

    modules = data.modules || [];

    document.getElementById("moduleCount").textContent =
        modules.length;

    renderModules();
    loadReports();
    document.getElementById("systemStatus").textContent =
        "Dashboard operational";
}

function renderModules() {
    const query = document.getElementById("search").value.toLowerCase();

    const grid = document.getElementById("moduleGrid");
    grid.innerHTML = "";

    modules.filter(m =>
        (m.name + " " + m.file).toLowerCase().includes(query)
    ).forEach(m => {
        const card = document.createElement("div");
        card.className = "module";

        const title = document.createElement("h3");
        title.textContent = m.number + " — " + m.name;

        const file = document.createElement("p");
        file.className = "muted";
        file.textContent = m.file;

        const status = document.createElement("p");
        status.className = "status";
        status.textContent = m.status;

        const run = document.createElement("button");
        run.className = "primary";
        run.textContent = "RUN IN GUI";

        run.onclick = () => runModule(m.file, m.name);

        card.append(title, file, status, run);
        grid.appendChild(card);
    });
}

async function runModule(file, name) {
    showPage("terminal");

    document.getElementById("activeModule").textContent =
        "Running: " + name;

    document.getElementById("terminalOutput").textContent =
        "Starting module...\n";

    const response = await fetch("/api/run", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({file:file})
    });

    const data = await response.json();

    if (!response.ok) {
        document.getElementById("terminalOutput").textContent =
            data.error || "Module launch failed";
        return;
    }

    activeSession = data.session;

    if (pollTimer) clearInterval(pollTimer);

    pollTimer = setInterval(pollOutput, 700);
}

async function pollOutput() {
    if (!activeSession) return;

    const response = await fetch(
        "/api/output/" + activeSession
    );

    const data = await response.json();

    if (!response.ok) return;

    document.getElementById("terminalOutput").textContent =
        data.output;

    const terminal = document.getElementById("terminalOutput");
    terminal.scrollTop = terminal.scrollHeight;

    if (!data.running) {
        clearInterval(pollTimer);
        pollTimer = null;

        document.getElementById("activeModule").textContent =
            "Module finished. Exit code: " + data.exit_code;
    }
}

async function sendInput() {
    if (!activeSession) {
        alert("Start a module first.");
        return;
    }

    const input = document.getElementById("terminalInput");
    const value = input.value;

    if (!value) return;

    const response = await fetch(
        "/api/input/" + activeSession,
        {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({input:value})
        }
    );

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Input failed");
        return;
    }

    input.value = "";
    input.focus();
}

async function stopModule() {
    if (!activeSession) return;

    await fetch("/api/stop/" + activeSession, {
        method:"POST"
    });

    activeSession = null;

    if (pollTimer) clearInterval(pollTimer);
    pollTimer = null;
}

async function generatePassword() {
    const length = document.getElementById("passLength").value;

    const response = await fetch("/api/password", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({length:length})
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error);
        return;
    }

    document.getElementById("passwordResult").value =
        data.password;
}

async function copyPassword() {
    const value = document.getElementById("passwordResult").value;

    if (!value) return;

    await navigator.clipboard.writeText(value);
    alert("Password copied.");
}

async function loadReports() {
    const response = await fetch("/reports");
    const data = await response.json();

    const reports = data.reports || [];

    document.getElementById("reportCount").textContent =
        reports.length;

    const list = document.getElementById("reportList");
    list.innerHTML = "";

    reports.forEach(report => {
        const card = document.createElement("div");
        card.className = "card";
        card.textContent =
            report.name + " | " + report.size + " bytes";
        list.appendChild(card);
    });

    if (!reports.length) {
        list.textContent = "No saved reports found.";
    }
}

async function loadSystem() {
    document.getElementById("diagnosticModules").textContent =
        "Detected modules: " + modules.length;

    document.getElementById("diagnosticStatus").textContent =
        "Web interface is operational.";
}


// ==========================================
// TORDISSX86 V15 COMBINATION INTERFACE
// ==========================================

async function loadV15Status() {
    const status = document.getElementById("v15Status");
    try {
        const response = await fetch("/api/v15/status");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Status request failed");
        }

        status.textContent =
            data.engine + " | " + data.status +
            " | Supported: " + data.supported.join(", ");
    } catch (error) {
        status.textContent = "V15 unavailable: " + error.message;
    }
}

async function runV15Analysis() {
    const kind = document.getElementById("v15Type").value;
    const value = document.getElementById("v15Value").value.trim();
    const output = document.getElementById("v15Output");
    const button = document.getElementById("v15Run");

    if (!value) {
        output.textContent = "Please enter an input first.";
        return;
    }

    button.disabled = true;
    button.textContent = "ANALYZING...";
    output.textContent = "Analysis running...";

    try {
        const response = await fetch("/api/v15/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({kind: kind, value: value})
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis request failed");
        }

        output.textContent = JSON.stringify(data.result, null, 2);
        await loadV15Reports();

    } catch (error) {
        output.textContent = "ERROR: " + error.message;
    } finally {
        button.disabled = false;
        button.textContent = "RUN ANALYSIS";
    }
}

async function loadV15Reports() {
    const list = document.getElementById("v15ReportList");

    try {
        const response = await fetch("/api/v15/reports");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Reports request failed");
        }

        const count = Number(data.count || 0);
        list.textContent = count +
            " reports saved. Report details are private.";

    } catch (error) {
        list.textContent = "Unable to load reports: " + error.message;
    }
}

// ==========================================
// END V15 INTERFACE
// ==========================================


loadModules();

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "version": "14",
        "port": PORT,
        "modules": len(find_modules())
    })


# ==========================================
# START SERVER
# ==========================================


# TORDISSX86_OSINT_POWER_CONTROL
OSINT_ACTIVE = False

@app.route("/api/osint/power", methods=["GET", "POST"])
def osint_power():
    global OSINT_ACTIVE

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        command = str(data.get("command", "")).upper()

        if command == "ON":
            OSINT_ACTIVE = True
        elif command == "OFF":
            OSINT_ACTIVE = False
        else:
            return jsonify({"error": "Use ON or OFF"}), 400

    return jsonify({
        "osint": "ON" if OSINT_ACTIVE else "OFF",
        "active": OSINT_ACTIVE
    })

# END TORDISSX86_OSINT_POWER_CONTROL



# ==========================================
# TORDISSX86 V15 COMBINATION API
# ==========================================

@app.route("/api/v15/status", methods=["GET"])
def v15_status():
    return jsonify(combo.get_status())


@app.route("/api/v15/analyze", methods=["POST"])
def v15_analyze():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    kind = data.get("kind")
    value = data.get("value")

    if not isinstance(kind, str) or not isinstance(value, str):
        return jsonify({"error": "kind and value must be strings"}), 400

    if len(value) > 2048:
        return jsonify({"error": "Input too long"}), 400

    kind = kind.strip().lower()

    if kind not in combo.ALLOWED_TYPES:
        return jsonify({
            "error": "Supported types: Email, Username, Phone, Domain, DNS and URL"
        }), 403

    try:
        result = combo.analyze(kind, value)
        return jsonify({"success": True, "result": result})

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("V15 analysis failed")
        return jsonify({"error": "Analysis failed; check server logs"}), 500


@app.route("/api/v15/reports", methods=["GET"])
def v15_reports():
    reports = combo.list_reports()
    return jsonify({
        "count": len(reports),
        "message": "Report details are private."
    })

# END TORDISSX86 V15 COMBINATION API



@app.route("/api/system/ping", methods=["GET"])
def system_ping():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    print("=" * 45)
    print(" TORDISSX86 V14 CYBER OSINT COMMAND CENTER")
    print("=" * 45)
    print("Dashboard: http://127.0.0.1:4444")
    print("Module GUI: ENABLED")
    print("Interactive CLI: ENABLED")
    print("Password Generator: ENABLED")
    print("=" * 45)

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )
