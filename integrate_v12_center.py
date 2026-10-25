from pathlib import Path
from datetime import datetime
import ast
import shutil

panel = Path("web_panel.py")
appfile = Path("app.py")

src = panel.read_text(encoding="utf-8")
marker = 'if __name__ == "__main__":'

if marker not in src:
    raise SystemExit("Flask startup marker missing")

if "app.register_blueprint(integration)" not in src:
    backup = panel.with_name(
        "web_panel_before_integration_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(panel, backup)

    block = """
# TORDISSX86 V12 INTEGRATION CENTER
from v12_integrations import integration
app.register_blueprint(integration)

"""
    src = src.replace(marker, block + marker, 1)
    ast.parse(src)
    panel.write_text(src, encoding="utf-8")
    print("Flask integration registered.")
    print("Backup:", backup.name)
else:
    print("Flask integration already registered.")

src = appfile.read_text(encoding="utf-8")

if '"33"' not in src:
    backup = appfile.with_name(
        "app_before_integration_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
    )
    shutil.copy2(appfile, backup)

    menu_marker = 'print("[31] Project Inventory")'
    if menu_marker not in src:
        raise SystemExit("Launcher menu marker missing")

    src = src.replace(
        menu_marker,
        menu_marker + '\n        print("[33] V12 Integration Center")',
        1
    )

    branch_marker = '        elif choice == "0":'
    branch = """
        elif choice == "33":
            print("\\\\nV12 INTEGRATION CENTER")
            print("Start Web Panel: python web_panel.py")
            print("Open: http://127.0.0.1:5055/v12/integrations/")
            input("\\\\nENTER...")

"""
    if branch_marker not in src:
        raise SystemExit("Launcher exit marker missing")

    src = src.replace(branch_marker, branch + branch_marker, 1)
    ast.parse(src)
    appfile.write_text(src, encoding="utf-8")
    print("Launcher option 33 added.")
    print("Backup:", backup.name)
else:
    print("Launcher option 33 already exists.")

ast.parse(panel.read_text(encoding="utf-8"))
ast.parse(appfile.read_text(encoding="utf-8"))
print("INTEGRATION SYNTAX OK")
