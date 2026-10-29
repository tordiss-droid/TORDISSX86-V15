import ast
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

EXCLUDED_PREFIXES = (
    "web_panel_", "dashboard_", "app_",
    "advanced_osint_v", "v12_", "integrate_",
    "repair_", "install_", "panel_upgrade"
)

EXCLUDED_FILES = {
    "combination_engine.py",
    "module_compat_audit.py",
    "button_diagnostic.py",
    "diagnostics.py",
    "app.py",
    "dashboard.py",
    "menu.py",
    "export.py",
}

def is_backup(name):
    low = name.lower()
    return (
        low in EXCLUDED_FILES
        or low.endswith("_backup.py")
        or low.endswith("_before_integration.py")
        or low.startswith(EXCLUDED_PREFIXES)
    )

def inspect_module(path):
    result = {
        "name": path.stem,
        "file": path.name,
        "status": "UNKNOWN",
        "functions": [],
        "imports": [],
        "requires_input": False,
        "has_main": False,
        "error": None
    }

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        functions = []
        imports = set()
        requires_input = False

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.col_offset == 0:
                    functions.append({
                        "name": node.name,
                        "async": isinstance(node, ast.AsyncFunctionDef),
                        "line": node.lineno
                    })

            elif isinstance(node, ast.Import):
                for item in node.names:
                    imports.add(item.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("input", "getpass"):
                        requires_input = True

        has_main = any(
            isinstance(node, ast.If)
            and "__name__" in ast.unparse(node.test)
            for node in tree.body
        )

        result.update({
            "status": "SYNTAX_OK",
            "functions": functions,
            "imports": sorted(imports),
            "requires_input": requires_input,
            "has_main": has_main
        })

        if not functions:
            result["compatibility"] = "REVIEW_REQUIRED"
        elif requires_input:
            result["compatibility"] = "INPUT_ADAPTER_REQUIRED"
        else:
            result["compatibility"] = "CANDIDATE"

    except Exception as error:
        result["status"] = "ERROR"
        result["compatibility"] = "NOT_READY"
        result["error"] = str(error)

    return result


def build_registry():
    modules = []

    for path in sorted(ROOT.glob("*.py")):
        if is_backup(path.name):
            continue

        modules.append(inspect_module(path))

    return {
        "project": "TORDISSX86",
        "engine": "V15 Combination Engine",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "total": len(modules),
        "ready_candidates": sum(
            m["compatibility"] == "CANDIDATE" for m in modules
        ),
        "input_adapters_needed": sum(
            m["compatibility"] == "INPUT_ADAPTER_REQUIRED"
            for m in modules
        ),
        "review_required": sum(
            m["compatibility"] == "REVIEW_REQUIRED"
            for m in modules
        ),
        "errors": sum(m["status"] == "ERROR" for m in modules),
        "modules": modules
    }


def save_registry():
    data = build_registry()
    output = ROOT / "module_registry.json"

    output.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    return data


def show_summary(data):
    print("\n====================================")
    print("       TORDISSX86 COMBINATION")
    print("====================================")
    print("Total modules:", data["total"])
    print("Candidates:", data["ready_candidates"])
    print("Input adapters needed:", data["input_adapters_needed"])
    print("Review required:", data["review_required"])
    print("Errors:", data["errors"])
    print("====================================")


if __name__ == "__main__":
    registry = save_registry()
    show_summary(registry)
    print("Registry saved: module_registry.json")
