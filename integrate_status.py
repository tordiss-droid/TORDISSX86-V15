from pathlib import Path
from datetime import datetime
import shutil
import ast

p = Path("web_panel.py")
src = p.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'
tag = "# TORDISSX86 V12 LIVE MONITOR"

if tag not in src:
    if marker not in src:
        raise SystemExit("Startup marker haijapatikana.")

    backup = p.with_name(
        "web_panel_before_status_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    addition = """
# TORDISSX86 V12 LIVE MONITOR
from v12_status import status_bp
app.register_blueprint(status_bp)
"""
    updated = src.replace(marker, addition + "\\n" + marker, 1)
    ast.parse(updated)
    p.write_text(updated, encoding="utf-8")
    print("Live Monitor integrated. Backup:", backup.name)
else:
    print("Live Monitor already integrated.")

ast.parse(p.read_text(encoding="utf-8"))
print("SYNTAX OK")
