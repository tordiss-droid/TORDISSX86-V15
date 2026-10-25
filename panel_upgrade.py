from pathlib import Path

p = Path("web_panel.py")
s = p.read_text(encoding="utf-8")

if 'def v12_reports()' not in s:
    routes = r'''

@app.route("/v12/reports")
def v12_reports():
    from pathlib import Path
    import json

    root = Path(__file__).resolve().parent
    folders = [
        "reports", "dns_reports", "domain_reports",
        "network_reports", "forensics_reports",
        "security_reports", "learning_reports", "exports"
    ]

    items = []
    for folder in folders:
        base = root / folder
        if base.exists():
            for f in base.rglob("*"):
                if f.is_file():
                    items.append({
                        "name": f.name,
                        "path": str(f.relative_to(root)),
                        "size": f.stat().st_size
                    })

    return render_template_string("""
    <html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Reports Center</title>
    <style>
    body{background:#050b07;color:#dfffe9;font-family:monospace;padding:20px}
    .card{background:#0b1710;border:1px solid #155b36;padding:15px;border-radius:14px;margin:12px 0}
    a{color:#00ff78}input{padding:12px;width:90%;background:#101d15;color:white}
    </style></head><body>
    <h2>REPORTS CENTER</h2>
    <input id="q" placeholder="Search report..." oninput="filter()">
    <p>TOTAL REPORTS: {{items|length}}</p>
    <div id="results">
    {% for item in items %}
      <div class="card">
      <b>{{item.name}}</b><br>
      {{item.path}}<br>
      {{item.size}} bytes
      </div>
    {% endfor %}
    </div>
    <script>
    function filter(){
      let q=document.getElementById('q').value.toLowerCase();
      document.querySelectorAll('#results .card').forEach(x=>{
        x.style.display=x.innerText.toLowerCase().includes(q)?'block':'none';
      });
    }
    </script>
    <a href="/">BACK TO DASHBOARD</a>
    </body></html>
    """, items=items)


@app.route("/v12/cases")
def v12_cases():
    from pathlib import Path
    root = Path(__file__).resolve().parent
    folder = root / "cases"
    files = list(folder.glob("*")) if folder.exists() else []

    return render_template_string("""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{background:#050b07;color:#dfffe9;font-family:monospace;padding:20px}
    .card{padding:14px;background:#0b1710;border:1px solid #155b36;margin:10px 0}
    a{color:#00ff78}</style></head><body>
    <h2>CASE MANAGEMENT</h2>
    <p>Case files found: {{files|length}}</p>
    {% for f in files %}
    <div class="card">{{f.name}}</div>
    {% endfor %}
    <a href="/">BACK</a>
    </body></html>
    """, files=files)


@app.route("/v12/evidence")
def v12_evidence():
    from pathlib import Path
    root = Path(__file__).resolve().parent
    folder = root / "evidence"
    files = list(folder.rglob("*")) if folder.exists() else []
    files = [f for f in files if f.is_file()]

    return render_template_string("""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{background:#050b07;color:#dfffe9;font-family:monospace;padding:20px}
    .card{padding:14px;background:#0b1710;border:1px solid #155b36;margin:10px 0}
    a{color:#00ff78}</style></head><body>
    <h2>EVIDENCE VAULT</h2>
    <p>Evidence files: {{files|length}}</p>
    {% for f in files %}
    <div class="card">{{f.name}}</div>
    {% endfor %}
    <a href="/">BACK</a>
    </body></html>
    """, files=files)

'''
    marker = '\nif __name__ == "__main__":'
    if marker not in s:
        raise SystemExit("Startup marker missing")
    s = s.replace(marker, routes + marker)

p.write_text(s, encoding="utf-8")
print("V12 WEB ROUTES INSTALLED")
