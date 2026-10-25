from pathlib import Path
import ast
import json
import time

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app.py"
OUT = ROOT / "v12_data"
OUT.mkdir(exist_ok=True)

def find_python_files(value):
    found = []
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        if value.value.endswith(".py"):
            found.append(value.value)
    elif isinstance(value, (ast.Tuple, ast.List, ast.Set)):
        for item in value.elts:
            found.extend(find_python_files(item))
    elif isinstance(value, ast.Dict):
        for item in value.values:
            found.extend(find_python_files(item))
    return found

def audit_file(path):
    result = {
        "file": str(path.relative_to(ROOT)),
        "exists": path.is_file(),
        "syntax": "UNKNOWN",
        "entrypoint": False,
        "status": "MISSING"
    }

    if not path.is_file():
        return result

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        result["syntax"] = "OK"

        has_main = any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "main"
            for node in ast.walk(tree)
        )

        has_launcher = any(
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and "__name__" in ast.dump(node.test)
            for node in ast.walk(tree)
        )

        result["entrypoint"] = has_main or has_launcher
        result["status"] = (
            "READY" if result["entrypoint"] else "NEEDS REVIEW"
        )

    except Exception as exc:
        result["syntax"] = "ERROR"
        result["error"] = str(exc)
        result["status"] = "SYNTAX ERROR"

    return result

print("\n===== TORDISSX86 V12 TOOL AUDIT =====")

menu_items = []
unmapped = []

if APP.exists():
    try:
        app_tree = ast.parse(APP.read_text(encoding="utf-8"))

        for node in app_tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = (
                    node.targets if isinstance(node, ast.Assign)
                    else [node.target]
                )
                if any(
                    isinstance(t, ast.Name) and t.id == "MODULES"
                    for t in targets
                ):
                    value = node.value
                    if isinstance(value, ast.Dict):
                        for key, item in zip(value.keys, value.values):
                            try:
                                option = ast.literal_eval(key)
                            except Exception:
                                option = "UNKNOWN"

                            files = find_python_files(item)

                            if files:
                                for filename in files:
                                    menu_items.append({
                                        "option": str(option),
                                        "file": filename
                                    })
                            else:
                                unmapped.append(str(option))
                    break
    except Exception as exc:
        print("MENU PARSE ERROR:", exc)

results = []
seen = set()

for item in menu_items:
    filename = item["file"]
    path = (ROOT / filename).resolve()

    if ROOT not in path.parents and path != ROOT:
        continue

    key = str(path)
    if key in seen:
        continue
    seen.add(key)

    result = audit_file(path)
    result["menu_option"] = item["option"]
    results.append(result)

all_python = []
excluded = {
    "__pycache__", "backups", "recovered_versions",
    ".git", ".venv", "venv"
}

for path in ROOT.rglob("*.py"):
    if any(part in excluded for part in path.parts):
        continue
    if path.name.startswith("web_panel_before_"):
        continue
    all_python.append(path)

counts = {
    "READY": sum(x["status"] == "READY" for x in results),
    "NEEDS REVIEW": sum(x["status"] == "NEEDS REVIEW" for x in results),
    "MISSING": sum(x["status"] == "MISSING" for x in results),
    "SYNTAX ERROR": sum(x["status"] == "SYNTAX ERROR" for x in results)
}

report = {
    "project": "TORDISSX86",
    "version": "V12",
    "audit_type": "STATIC - NO MODULES EXECUTED",
    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "launcher_menu_entries_mapped": len(menu_items),
    "unique_mapped_files": len(results),
    "unmapped_menu_options": unmapped,
    "python_files_in_project": len(all_python),
    "counts": counts,
    "modules": results
}

json_path = OUT / "TOOL_AUDIT.json"
txt_path = OUT / "TOOL_AUDIT.txt"

json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "TORDISSX86 V12 TOOL AUDIT",
    "=========================",
    f"Menu entries mapped: {len(menu_items)}",
    f"Unique mapped files: {len(results)}",
    f"Python files in project: {len(all_python)}",
    "",
    "STATUS COUNTS:"
]

for name, count in counts.items():
    lines.append(f"{name}: {count}")

lines.extend(["", "MODULE DETAILS:"])

for item in results:
    lines.append(
        f"[{item['status']}] Option {item['menu_option']} "
        f"-> {item['file']} | Syntax: {item['syntax']} "
        f"| Entry point: {item['entrypoint']}"
    )

lines.extend(["", "UNMAPPED MENU OPTIONS:"])
lines.extend(unmapped or ["None"])

lines.extend([
    "",
    "NOTE: Static audit only. READY does not prove runtime functionality."
])

txt_path.write_text("\n".join(lines), encoding="utf-8")

print("MENU ENTRIES:", len(menu_items))
print("UNIQUE MAPPED FILES:", len(results))
print("PROJECT PYTHON FILES:", len(all_python))

for name, count in counts.items():
    print(f"{name}: {count}")

print("\nMODULE DETAILS:")
for item in results:
    print(
        f"[{item['status']}] Option {item['menu_option']} "
        f"-> {item['file']}"
    )

print("\nREPORTS SAVED:")
print(json_path)
print(txt_path)
print("\n===== AUDIT COMPLETE =====")
