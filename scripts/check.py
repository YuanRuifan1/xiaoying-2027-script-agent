"""Save actual executable test results without shell redirection encoding issues."""
import io
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
out = ROOT / "examples/test-results"
out.mkdir(parents=True, exist_ok=True)
(out / "unittest.txt").write_text(stream.getvalue(), encoding="utf-8")
summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
           "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
           "skipped": len(result.skipped), "passed": result.wasSuccessful()}
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary))
raise SystemExit(0 if result.wasSuccessful() else 1)
