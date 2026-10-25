import ast
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

FILES = [
    "profile.py",
    "username.py",
    "posts.py",
    "image_meta.py",
    "reports.py",
    "master_search.py",
    "case_manager.py",
    "case_analytics.py",
    "diagnostics.py"
]

report = []

print("\n===== TORDISSX86 DEEP INSPECTION =====")

for filename in FILES:
    path = ROOT / filename
    item = {
        "file": filename,
        "exists": path.exists(),
        "functions": [],
        "classes": [],
        "imports": [],
        "main_guard": False,
        "syntax": "UNKNOWN"
    }

    print(f"\n========== {filename} ==========")

    if not path.exists():
        print("[MISSING]")
        report.append(item)
        continue

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        item["syntax"] = "OK"

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                item["functions"].append(node.name)
                print("FUNCTION:", node.name)

            elif isinstance(node, ast.ClassDef):
                item["classes"].append(node.name)
                print("CLASS:", node.name)

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                text = ast.get_source_segment(source, node)
                item["imports"].append(text)
                print("IMPORT:", text)

            elif isinstance(node, ast.If):
                if "__name__" in ast.dump(node.test):
                    item["main_guard"] = True

        print("MAIN GUARD:", item["main_guard"])
        print("SYNTAX: OK")

    except Exception as exc:
        item["syntax"] = "ERROR"
        item["error"] = str(exc)
        print("SYNTAX ERROR:", exc)

    report.append(item)

out = ROOT / "v12_data" / "DEEP_INSPECTION.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n===== APP MENU REFERENCES =====")

app = ROOT / "app.py"
if app.exists():
    for number, line in enumerate(
        app.read_text(encoding="utf-8").splitlines(), 1
    ):
        if any(name in line for name in FILES):
            print(f"{number}: {line.strip()}")

print("\nREPORT:", out)
print("===== INSPECTION COMPLETE =====")
