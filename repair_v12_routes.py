from pathlib import Path
import ast
import shutil
from datetime import datetime

p = Path("web_panel.py")
src = p.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'

if marker not in src:
    raise SystemExit("ERROR: Flask startup marker missing")

# Correct the reversed Workspace registration
src = src.replace(
    "workspace.register_blueprint(app)",
    "app.register_blueprint(workspace)"
)

# Prepare missing imports and registrations
additions = []

if "from v12_workspace import workspace" not in src:
    additions.append("from v12_workspace import workspace")

if "from v12_status import status_bp" not in src:
    additions.append("from v12_status import status_bp")

if "app.register_blueprint(workspace)" not in src:
    additions.append("app.register_blueprint(workspace)")

if "app.register_blueprint(status_bp)" not in src:
    additions.append("app.register_blueprint(status_bp)")

if additions:
    backup = p.with_name(
        "web_panel_before_route_repair_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(p, backup)

    block = (
        "\n# TORDISSX86 V12 ROUTE REPAIR\n"
        + "\n".join(additions)
        + "\n\n"
    )
    src = src.replace(marker, block + marker, 1)

ast.parse(src)
p.write_text(src, encoding="utf-8")

print("ROUTE REPAIR COMPLETE")
if additions:
    print("Backup:", backup.name)
else:
    print("Routes already integrated")
