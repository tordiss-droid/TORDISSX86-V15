from pathlib import Path
import ast
import importlib.util
import json

ROOT = Path(__file__).resolve().parent

print("\n========== TORDISSX86 V12 VERIFICATION ==========\n")

# 1. Python syntax
pyfiles = list(ROOT.glob("*.py"))
syntax_errors = []

for file in pyfiles:
    try:
        ast.parse(file.read_text(encoding="utf-8"))
    except Exception as exc:
        syntax_errors.append((file.name, str(exc)))

print(f"[{'OK' if not syntax_errors else 'ERROR'}] Python files: {len(pyfiles)}")
for name, error in syntax_errors:
    print("  ERROR:", name, error)

# 2. Required project files
required = [
    "web_panel.py", "v12_workspace.py", "v12_catalog.py",
    "v12_report_engine.py", "v12_health.py", "v12_control.py"
]

missing = [name for name in required if not (ROOT / name).is_file()]
print(f"[{'OK' if not missing else 'ERROR'}] Integration files")
for name in missing:
    print("  MISSING:", name)

# 3. Flask route tests
if not syntax_errors and not missing:
    try:
        spec = importlib.util.spec_from_file_location(
            "tordiss_web_panel", ROOT / "web_panel.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        client = module.app.test_client()
        routes = [
            "/v12",
            "/v12/control",
            "/v12/modules",
            "/v12/manage/",
            "/v12/report-engine",
            "/v12/health/",
            "/v12/reports",
            "/v12/cases",
            "/v12/evidence",
            "/intelligence"
        ]

        failed = []
        for route in routes:
            try:
                response = client.get(route)
                ok = response.status_code < 500
                print(
                    f"[{'OK' if ok else 'ERROR'}] "
                    f"{route} -> HTTP {response.status_code}"
                )
                if not ok:
                    failed.append(route)
            except Exception as exc:
                print("[ERROR]", route, str(exc))
                failed.append(route)

        print("\nROUTE FAILURES:", len(failed))

    except Exception as exc:
        print("[ERROR] Flask integration:", repr(exc))

print("\n========== VERIFICATION COMPLETE ==========\n")
