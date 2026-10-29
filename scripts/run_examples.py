"""Run actual examples. Mock policy is explicitly NOT real model evidence."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from script_agent.agent import run
from script_agent.cli import save_result
from script_agent.providers import GLMProvider, MockProvider, load_env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["mock", "glm"], default="mock")
    parser.add_argument("--case", help="One case; defaults to all")
    args = parser.parse_args()
    load_env(ROOT / ".env")
    cases = [("normal", "normal", {}, 16), ("missing", "missing", {}, 16),
             ("no_material", "no_material", {}, 16), ("tool_failure", "normal", {"search_materials": 1}, 16),
             ("over_duration", "over_duration", {}, 16), ("unsupported_claim", "unsupported_claim", {}, 16),
             ("step_limit", "normal", {}, 2)]
    summaries = []
    if args.case and args.case not in {c[0] for c in cases}:
        parser.error("unknown case")
    for name, filename, failures, limit in cases:
        if args.case and name != args.case:
            continue
        request = json.loads((ROOT / f"examples/inputs/{filename}.json").read_text(encoding="utf-8"))
        provider = GLMProvider() if args.provider == "glm" else MockProvider(request)
        result = run(request, provider, ROOT / "data", max_calls=limit, failures=failures)
        result["harness"] = {"injected_failures": failures, "case": name, "initial_draft_supplied": "initial_draft" in request}
        out = ROOT / "examples/runs" / args.provider / name
        save_result(result, out)
        summary = {"case": name, "provider": args.provider, "status": result["status"], "tool_calls": result["tool_calls"]}
        summaries.append(summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    return summaries


if __name__ == "__main__":
    main()
