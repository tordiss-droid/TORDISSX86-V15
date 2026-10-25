from pathlib import Path
from datetime import datetime
import shutil
import ast

p = Path("web_panel.py")
src = p.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'

if "v12_report_engine.engine" not in src:
    if marker not in src:
        raise SystemExit("Startup marker haijapatikana.")

    backup = p.with_name(
        "web_panel_before_report_engine_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    addition = """
# TORDISSX86 V12 REPORT ENGINE
from v12_report_engine import engine as v12_report_engine_blueprint
app.register_blueprint(v12_report_engine_blueprint)
# END REPORT ENGINE

"""
    updated = src.replace(marker, addition + marker, 1)
    ast.parse(updated)
    p.write_text(updated, encoding="utf-8")
    print("Report Engine integrated.")
    print("Backup:", backup.name)
else:
    print("Report Engine already integrated.")

ast.parse(p.read_text(encoding="utf-8"))
print("SYNTAX OK")
