from pathlib import Path
from flask import Blueprint, render_template_string, request, redirect
import tarfile
import hashlib
import json
import time

recovery = Blueprint("v12_recovery", __name__, url_prefix="/v12/recovery")

ROOT = Path(__file__).resolve().parent
BACKUPS = ROOT / "backups"
RESTORES = ROOT / "recovered_versions"
RESTORES.mkdir(exist_ok=True)

def inspect_archive(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getmembers()
            safe = all(
                not Path(m.name).is_absolute()
                and ".." not in Path(m.name).parts
                and not m.issym()
                and not m.islnk()
                for m in members
            )
            return {
                "valid": safe,
                "files": len(members),
                "sha256": digest
            }
    except Exception:
        return {"valid": False, "files": 0, "sha256": digest}

@recovery.get("/")
def home():
    items = []
    for path in sorted(BACKUPS.glob("*.tar.gz"), reverse=True):
        result = inspect_archive(path)
        items.append({
            "name": path.name,
            "valid": result["valid"],
            "files": result["files"],
            "sha256": result["sha256"]
        })

    return render_template_string("""
    <!doctype html><html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>TORDISSX86 Recovery</title>
    <style>
    body{background:#07110e;color:#eafff3;font-family:Arial;padding:18px}
    h1,h2{color:#42e69b}
    .card{background:#10251c;border:1px solid #236b4b;
    border-radius:10px;padding:15px;margin:12px 0;overflow-wrap:anywhere}
    button{background:#176b43;color:white;padding:12px;border:0;border-radius:7px}
    small{color:#a8cbb7}
    </style></head><body>
    <h1>TORDISSX86 V12</h1><h2>Recovery Center</h2>
    <p><a href="/v12/control" style="color:#42e69b">Control Center</a></p>
    {% for x in items %}
    <div class="card">
    <b>{{ x.name }}</b><br>
    <p>Status: {{ "VALID" if x.valid else "INVALID" }}</p>
    <small>Files: {{ x.files }}</small><br>
    <small>SHA256: {{ x.sha256 }}</small>
    {% if x.valid %}
    <form method="post" action="/v12/recovery/restore">
    <input type="hidden" name="archive" value="{{ x.name }}">
    <button>RESTORE TO NEW FOLDER</button>
    </form>
    {% endif %}
    </div>
    {% else %}
    <p>No backup archives found.</p>
    {% endfor %}
    </body></html>
    """, items=items)

@recovery.post("/restore")
def restore():
    name = Path(request.form.get("archive", "")).name
    if name != request.form.get("archive", ""):
        return "Invalid archive name", 400

    source = BACKUPS / name
    if not source.is_file() or not name.endswith(".tar.gz"):
        return "Backup not found", 404

    result = inspect_archive(source)
    if not result["valid"]:
        return "Archive validation failed", 400

    destination = RESTORES / (source.stem + "_" + str(int(time.time())))
    destination.mkdir(parents=True, exist_ok=False)

    try:
        with tarfile.open(source, "r:gz") as archive:
            archive.extractall(destination, filter="data")
    except Exception as exc:
        return f"Restore failed: {exc}", 500

    return (
        "Restore completed in: " + str(destination.relative_to(ROOT)) +
        ". Current project was not overwritten."
    )
