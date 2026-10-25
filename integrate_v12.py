from pathlib import Path
from datetime import datetime
import shutil
import ast

p = Path("web_panel.py")
if not p.exists():
    raise SystemExit("ERROR: web_panel.py haipo")

src = p.read_text()
backup = p.with_name("web_panel_before_integration_" +
                     datetime.now().strftime("%Y%m%d_%H%M%S") + ".py")
shutil.copy2(p, backup)

portal = r'''

# ===== TORDISSX86 V12 UNIFIED PORTAL =====
@app.route("/v12")
def tordiss_v12_portal():
    links = [
        ("/intelligence", "OSINT INTELLIGENCE", "Domain, email, phone and username analysis"),
        ("/v12/reports", "REPORTS CENTER", "Browse generated reports"),
        ("/v12/cases", "CASE MANAGER", "Browse case records"),
        ("/v12/evidence", "EVIDENCE VAULT", "Browse evidence files"),
        ("/module/16", "SYSTEM DIAGNOSTICS", "Project diagnostics"),
        ("/", "MAIN DASHBOARD", "Return to the original dashboard"),
    ]
    cards = "".join(
        f'<a class="v12-card" href="{url}"><b>{name}</b><small>{desc}</small></a>'
        for url, name, desc in links
    )
    return render_template_string("""
    <!doctype html>
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>TORDISSX86 V12</title>
    <style>
    body{margin:0;background:#07110e;color:#e8fff4;font-family:Arial;padding:22px}
    header{padding:22px 0;border-bottom:1px solid #1d5740}
    h1{color:#42e69b;letter-spacing:2px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:24px}
    .v12-card{display:block;text-decoration:none;color:#e8fff4;background:#10251c;
    border:1px solid #236b4b;border-radius:12px;padding:20px;min-height:75px}
    .v12-card b{display:block;color:#42e69b;margin-bottom:12px}
    .v12-card small{color:#b7d6c5}
    .v12-card:hover{background:#173b2a;border-color:#42e69b}
    footer{margin-top:30px;color:#83a997;font-size:12px}
    </style></head><body>
    <header><h1>TORDISSX86</h1><p>V12 • UNIFIED SECURITY WORKSPACE</p></header>
    <main class="grid">""" + cards + """</main>
    <footer>Local dashboard • Authorized and ethical security research only</footer>
    </body></html>
    """)

# Add a navigation link to the original home page.
_TORDISS_V12_NAV = "TORDISSX86_V12_NAV_INJECTOR"
if _TORDISS_V12_NAV not in globals():
    @app.after_request
    def tordiss_v12_home_navigation(response):
        if request.path == "/" and response.mimetype == "text/html":
            page = response.get_data(as_text=True)
            link = (
                '<div style="position:sticky;top:0;z-index:9999;'
                'background:#10251c;padding:12px;text-align:center">'
                '<a href="/v12" style="color:#42e69b;font-weight:bold;'
                'text-decoration:none">OPEN TORDISSX86 V12 UNIFIED CENTER</a></div>'
            )
            if "/v12" not in page:
                if "</body>" in page:
                    page = page.replace("</body>", link + "</body>", 1)
                else:
                    page += link
                response.set_data(page)
        return response
    globals()[_TORDISS_V12_NAV] = True

# ===== END TORDISSX86 V12 UNIFIED PORTAL =====
'''

if "def tordiss_v12_portal" not in src:
    marker = 'if __name__ == "__main__":'
    if marker not in src:
        raise SystemExit("ERROR: startup marker haijapatikana; backup imehifadhiwa")
    src = src.replace(marker, portal + "\n" + marker, 1)

p.write_text(src)

try:
    ast.parse(src)
    print("SUCCESS: V12 portal integrated")
    print("Backup:", backup.name)
    print("Open: http://127.0.0.1:5055/v12")
except SyntaxError as e:
    shutil.copy2(backup, p)
    raise SystemExit(f"Syntax error; original restored: {e}")
