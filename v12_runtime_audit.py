import subprocess
import sys
import json
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

tests = {
    "profile.py": "test_public\n\n",
    "username.py": "test_public\n\n",
    "posts.py": "https://www.instagram.com/p/example/\nTest note\n\n",
    "image_meta.py": "/nonexistent_test_image.jpg\n\n",
    "reports.py": "0\n",
    "master_search.py": "0\n",
    "case_manager.py": "0\n",
    "case_analytics.py": "0\n",
    "diagnostics.py": "\n"
}

results = []

print("\n===== V12 RUNTIME SMOKE TEST =====")

for filename, user_input in tests.items():
    print(f"\nTesting: {filename}")

    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / filename)],
            input=user_input,
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=15,
            env={**os.environ, "TERM": "dumb"}
        )

        passed = result.returncode == 0

        item = {
            "module": filename,
            "return_code": result.returncode,
            "status": "PASS" if passed else "FAIL",
            "output_tail": result.stdout[-500:],
            "error_tail": result.stderr[-500:]
        }

        print("[PASS]" if passed else "[FAIL]",
              "Exit:", result.returncode)

        if result.stderr.strip():
            print("ERROR:", result.stderr[-250:])

    except subprocess.TimeoutExpired:
        item = {
            "module": filename,
            "status": "TIMEOUT"
        }
        print("[TIMEOUT]")

    except Exception as exc:
        item = {
            "module": filename,
            "status": "ERROR",
            "error": str(exc)
        }
        print("[ERROR]", exc)

    results.append(item)

passed = sum(x["status"] == "PASS" for x in results)

report = {
    "project": "TORDISSX86",
    "version": "V12",
    "test": "Runtime smoke test",
    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "passed": passed,
    "failed": len(results) - passed,
    "results": results
}

out = ROOT / "v12_data" / "RUNTIME_AUDIT.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n===== RESULTS =====")
print("PASSED:", passed, "/", len(results))
print("FAILED:", len(results) - passed)
print("REPORT:", out)
