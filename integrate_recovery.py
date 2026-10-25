from pathlib import Path
import ast
from datetime import datetime
import shutil

p = Path("web_panel.py")
src = p.read_text(encoding="utf-8")
tag = "# TORDISSX86 V12 RECOVERY CENTER"
marker = 'if __name__ == "__main__":'

if tag not in src:
    if marker not in src:
        raise SystemExit("Startup marker missing.")

    backup = p.with_name(
        "web_panel_before_recovery_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    code = """
# TORDISSX86 V12 RECOVERY CENTER
from v12_recovery import recovery
app.register_blueprint(recovery)
"""
    updated = src.replace(marker, code + "\n" + marker, 1)
    ast.parse(updated)
    p.write_text(updated, encoding="utf-8")
    print("Recovery Center integrated.")
    print("Backup:", backup.name)
else:
    print("Recovery Center already integrated.")

ast.parse(p.read_text(encoding="utf-8"))
print("SYNTAX OK")
