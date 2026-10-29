"""Verify committed code in a clean archive with no .env, venv or installed package."""
import io
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tools = ROOT / ".tools"
tools.mkdir(exist_ok=True)
sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
archive = subprocess.check_output(["git", "archive", "--format=zip", "HEAD"], cwd=ROOT)
with tempfile.TemporaryDirectory(prefix="clean-review-", dir=tools) as directory:
    clean = Path(directory)
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        for name in package.namelist():
            if not (clean / name).resolve().is_relative_to(clean.resolve()):
                raise RuntimeError("unsafe archive member")
        package.extractall(clean)
    assert not (clean / ".env").exists()
    env = {**os.environ, "PYTHONPATH": str(clean / "src")}
    tests = subprocess.run([sys.executable, "scripts/check.py"], cwd=clean, env=env, capture_output=True, text=True)
    cli = subprocess.run([sys.executable, "-m", "script_agent", "--provider", "mock", "--input", "examples/inputs/normal.json",
                          "--output", "private-runs/clean"], cwd=clean, env=env, capture_output=True, text=True)
    resultpath = clean / "private-runs/clean/result.json"
    status = json.loads(resultpath.read_text(encoding="utf-8"))["status"] if resultpath.exists() else "not_generated"
    stats = json.loads((clean / "examples/test-results/summary.json").read_text(encoding="utf-8"))
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "source_commit": sha,
              "no_env_file": True, "tests": stats, "cli_exit_code": cli.returncode,
              "cli_status": status, "passed": tests.returncode == cli.returncode == 0 and status == "completed"}
out = ROOT / "examples/test-results/clean-reproduction.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
