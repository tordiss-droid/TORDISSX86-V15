import importlib.util
from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parent
TARGETS = [
    "/",
    "/v12",
    "/v12/control",
    "/v12/modules",
    "/v12/manage/",
    "/v12/report-engine",
    "/v12/health/",
    "/v12/status/",
    "/v12/status/api",
    "/v12/recovery/",
    "/v12/reports",
    "/v12/cases",
    "/v12/evidence",
    "/intelligence",
]

spec = importlib.util.spec_from_file_location(
    "tordiss_panel_test", ROOT / "web_panel.py"
)
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)

client = panel.app.test_client()
results = []

print("\n===== TORDISSX86 V12 FINAL TEST =====")

for route in TARGETS:
    try:
        response = client.get(route)
        status = response.status_code
        ok = status == 200
        results.append({
            "route": route,
            "http": status,
            "status": "PASS" if ok else "FAIL"
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {route} -> {status}")
    except Exception as exc:
        results.append({
            "route": route,
            "http": None,
            "status": "ERROR",
            "error": str(exc)
        })
        print(f"[ERROR] {route}: {exc}")

passed = sum(x["status"] == "PASS" for x in results)
failed = len(results) - passed

report = {
    "project": "TORDISSX86",
    "version": "V12",
    "tested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "passed": passed,
    "failed": failed,
    "results": results
}

out = ROOT / "v12_data" / "FINAL_TEST_REPORT.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\nPASSED:", passed)
print("FAILED:", failed)
print("REPORT:", out)
print("===== TEST COMPLETE =====")
