"""CLI: python -m script_agent --input ... --provider mock|glm."""
import argparse
import json
from pathlib import Path

from .agent import run
from .providers import GLMProvider, MockProvider, ProviderError, load_env


def markdown(result):
    rows = ["# 短视频脚本", "", "> 产品资料为虚构；时长为规则估算。", "",
            f"状态：{result['status']}", "", f"说明：{result['reason']}", "",
            f"运行模式：{result['provider']} / {result['model']}", ""]
    script = result.get("script")
    if script:
        rows.extend([f"## {script['title']}", "", "| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |",
                     "|---|---|---|---|---|"])
        estimates = (result.get("duration") or {}).get("shots", [])
        for i, shot in enumerate(script["shots"], 1):
            lines = " ".join(p["text"] for p in shot["lines"])
            sources = ", ".join(f"{p['source_id']}/{p['fact_id']}" for p in shot["lines"] if p.get("source_id")) or "非产品主张"
            seconds = estimates[i-1]["seconds"] if len(estimates) >= i else "未估算"
            clean = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
            rows.append("| " + " | ".join(map(clean, [i, shot["visual"], lines, sources, seconds])) + " |")
    rows.extend(["", "## 时长检查", "", "```json", json.dumps(result.get("duration"), ensure_ascii=False, indent=2), "```",
                 "", "## 规则检查、引用及风险", "", "```json", json.dumps(result.get("rule_check"), ensure_ascii=False, indent=2), "```"])
    return "\n".join(rows) + "\n"


def save_result(result, output):
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    (root / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (root / "trace.jsonl").write_text("".join(json.dumps(t, ensure_ascii=False, allow_nan=False) + "\n" for t in result["trace"]), encoding="utf-8")
    (root / "script.md").write_text(markdown(result), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Grounded short-video script agent (synthetic product data)")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--provider", choices=["mock", "glm"], default="mock")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("private-runs/latest"))
    parser.add_argument("--max-calls", type=int, default=16)
    parser.add_argument("--fail-tool", choices=["search_materials", "set_script", "estimate_duration", "check_script"], help="Inject one tool failure; test harness only")
    args = parser.parse_args()
    try:
        load_env(".env")
        request = json.loads(args.input.read_text(encoding="utf-8-sig"))
        provider = GLMProvider() if args.provider == "glm" else MockProvider(request)
        result = run(request, provider, args.data, max_calls=args.max_calls,
                     failures={args.fail_tool: 1} if args.fail_tool else None)
        save_result(result, args.output)
    except (ProviderError, ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(json.dumps({"status": result["status"], "reason": result["reason"],
                      "tool_calls": result["tool_calls"], "model_calls": result["model_calls"],
                      "output": str(args.output)}, ensure_ascii=False))
    return 0 if result["status"] == "completed" else 2
