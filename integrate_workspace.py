from pathlib import Path
from datetime import datetime
import shutil
import ast

p = Path("web_panel.py")
if not p.exists():
    raise SystemExit("web_panel.py haipo")

src = p.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'

if "workspace.register_blueprint(app)" in src:
    print("Workspace tayari imeunganishwa.")
else:
    if marker not in src:
        raise SystemExit("Startup marker haijapatikana; hakuna kilichobadilishwa.")

    backup = p.with_name(
        "web_panel_before_workspace_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    addition = """
# TORDISSX86 V12 WORKSPACE INTEGRATION
from v12_workspace import workspace
workspace.register_blueprint(app)
# END WORKSPACE INTEGRATION

"""
    updated = src.replace(marker, addition + marker, 1)

    try:
        ast.parse(updated)
        p.write_text(updated, encoding="utf-8")
        print("Workspace integrated.")
        print("Backup:", backup.name)
    except SyntaxError as exc:
        raise SystemExit(f"Integration failed: {exc}")

ast.parse(p.read_text(encoding="utf-8"))
print("SUCCESS: Python syntax verified.")
print("WORKSPACE: http://127.0.0.1:5055/v12/manage")
