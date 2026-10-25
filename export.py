import os
import json
from datetime import datetime

folder = "reports"
os.makedirs(folder, exist_ok=True)

data = []

for filename in os.listdir(folder):
    path = os.path.join(folder, filename)

    if os.path.isfile(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            data.append({
                "filename": filename,
                "content": f.read()
            })

os.makedirs("exports", exist_ok=True)

output = "exports/TORDISSX86_" + datetime.now().strftime(
    "%Y%m%d_%H%M%S"
) + ".json"

with open(output, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("[+] EXPORT SUCCESSFUL")
print("[+] FILE:", output)
print("[+] REPORTS:", len(data))
