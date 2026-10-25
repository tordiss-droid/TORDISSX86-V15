from pathlib import Path
from datetime import datetime
import shutil
import ast

p = Path("web_panel.py")
if not p.exists():
    raise SystemExit("ERROR: web_panel.py haipo")

src = p.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'

if "v12_catalog.catalog" in src:
    print("Module Center tayari imeunganishwa.")
else:
    if marker not in src:
        raise SystemExit("Startup marker haijapatikana.")

    backup = p.with_name(
        "web_panel_before_catalog_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    addition = """
# TORDISSX86 V12 MODULE CATALOG
from v12_catalog import catalog as v12_catalog_blueprint
app.register_blueprint(v12_catalog_blueprint)
# END MODULE CATALOG

"""
    updated = src.replace(marker, addition + marker, 1)

    try:
        ast.parse(updated)
        p.write_text(updated, encoding="utf-8")
        print("Module Center integrated.")
        print("Backup:", backup.name)
    except SyntaxError as exc:
        raise SystemExit(f"Syntax error: {exc}")

ast.parse(p.read_text(encoding="utf-8"))
print("SUCCESS: syntax verified")
