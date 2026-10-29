"""Scan publishable files without printing secret values; .gitignore is authoritative."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
output = subprocess.check_output(["git", "-c", "core.quotepath=false", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT)
files = sorted(set(f for f in output.decode().split("\0") if f))
local_secrets = []
envfile = ROOT / ".env"
if envfile.exists():
    for line in envfile.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("GLM_API_KEY="):
            value = line.split("=", 1)[1].strip().strip("\"'")
            if value:
                local_secrets.append(value.encode())
problems = []
for name in files:
    path = ROOT / name
    if name == ".env" or name.startswith((".venv/", ".tools/", "private-runs/")):
        problems.append({"file": name, "reason": "private file included"})
    if not path.is_file():
        continue
    content = path.read_bytes()
    if any(secret in content for secret in local_secrets):
        problems.append({"file": name, "reason": "local API key found"})
    if re.search(rb"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}", content):
        problems.append({"file": name, "reason": "possible GitHub token found"})
report = {"files_checked": len(files), "passed": not problems, "problems": problems}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["passed"] else 1)
