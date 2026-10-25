from pathlib import Path
import re

files = [
    Path("web_panel.py"),
    Path("v12_integrations.py"),
    Path("v12_button_repair.py"),
    Path("v12_control.py"),
    Path("v12_catalog.py"),
]

for p in files:
    print(f"\n===== {p} =====")
    if not p.exists():
        print("FILE MISSING")
        continue

    src = p.read_text(errors="replace")

    for i, line in enumerate(src.splitlines(), 1):
        if re.search(
            r'<button|<a |onclick=|addEventListener|@.*route|href=|type="submit"',
            line, re.I
        ):
            print(f"{i}: {line.strip()[:220]}")
