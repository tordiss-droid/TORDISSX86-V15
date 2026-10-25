from pathlib import Path
from datetime import datetime
import shutil
import ast

p = Path("web_panel.py")
src = p.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'
tag = "# TORDISSX86 V12 HEALTH CENTER"

if tag not in src:
    if marker not in src:
        raise SystemExit("Startup marker missing; no changes made.")

    backup = p.with_name(
        "web_panel_before_health_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    code = """
# TORDISSX86 V12 HEALTH CENTER
from v12_health import health as v12_health_blueprint
app.register_blueprint(v12_health_blueprint)
"""
    updated = src.replace(marker, code + "\n" + marker, 1)
    ast.parse(updated)
    p.write_text(updated, encoding="utf-8")
    print("Health Center integrated.")
    print("Backup:", backup.name)
else:
    print("Health Center already integrated.")

ast.parse(p.read_text(encoding="utf-8"))
print("SYNTAX OK")
