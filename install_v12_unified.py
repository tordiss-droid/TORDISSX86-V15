from pathlib import Path
import re
import shutil
import sys

root = Path(__file__).resolve().parent
panel = root / "web_panel.py"

if not panel.exists():
    sys.exit("ERROR: web_panel.py haipo")

source = panel.read_text()

marker = "# TORDISSX86_UNIFIED_REGISTRATION"
if marker not in source:
    block = '''
# TORDISSX86_UNIFIED_REGISTRATION
try:
    from v12_catalog import catalog
    from v12_button_repair import button_bp
    from v12_integrations import integration
    from v12_hub import hub_bp

    for _bp in (catalog, button_bp, integration, hub_bp):
        if _bp.name not in app.blueprints:
            app.register_blueprint(_bp)
except Exception as _v12_error:
    print("TORDISSX86 V12 registration warning:", _v12_error)
# END TORDISSX86_UNIFIED_REGISTRATION

'''
    match = re.search(r"(?m)^if __name__\s*==\s*['\"]__main__['\"]\s*:", source)
    if not match:
        sys.exit("ERROR: Sijaona sehemu ya if __name__ == '__main__' ndani ya web_panel.py. Hakuna mabadiliko yaliyofanywa.")

    source = source[:match.start()] + block + source[match.start():]
    panel.write_text(source)
    print("[OK] Blueprints registration imeongezwa.")
else:
    print("[OK] Registration tayari ipo; hakuna duplicate iliyoongezwa.")

print("[DONE] Installer imekamilika.")
