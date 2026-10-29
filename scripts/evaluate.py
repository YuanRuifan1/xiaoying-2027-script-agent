"""Generate an evidence index from actual saved results. Does not invent expected runs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cases = ["normal", "missing", "no_material", "tool_failure", "over_duration", "unsupported_claim", "step_limit"]
rows = ["# 验证结果与证据", "", "本报告由 `python scripts/evaluate.py` 从实际结果生成。Mock 仅验证流程；真实模型证据以 glm 列为准。", "",
        "| 场景 | 模式/模型 | 实际状态 | 工具调用 | 预计秒数 | 结果和 Trace |",
        "|---|---|---|---|---|---|"]
for mode in ("mock", "glm"):
    for case in cases:
        folder = ROOT / f"examples/runs/{mode}/{case}"
        file = folder / "result.json"
        if not file.exists():
            rows.append(f"| {case} | {mode} | 未运行 | — | — | — |")
            continue
        result = json.loads(file.read_text(encoding="utf-8"))
        duration = (result.get("duration") or {}).get("total_seconds", "—")
        base = f"../examples/runs/{mode}/{case}"
        rows.append(f"| {case} | {mode}/{result['model']} | {result['status']} | {result['tool_calls']} | {duration} | [结果]({base}/result.json) / [Trace]({base}/trace.jsonl) / [脚本]({base}/script.md) |")

rows.extend(["", "## 测试预期", "",
             "normal 应完成并通过两项检查；missing 应列出缺失项；no_material 应补查或请求资料；tool_failure 应观察错误并恢复或明确失败；over_duration 应检查初稿超时并修正复查，或明确未完成；unsupported_claim 应识别无依据主张并修正或明确未完成；step_limit 应触顶后返回 incomplete。模型服务错误只能证明故障处理，不能替代相应业务验收。", "",
             "## 真实路径", ""])
for case in cases:
    path = ROOT / f"examples/runs/glm/{case}/result.json"
    if not path.exists():
        continue
    result = json.loads(path.read_text(encoding="utf-8"))
    tools = [step for step in result["trace"] if step.get("kind") == "tool"]
    sequence = " → ".join(step["tool"] + ("[失败]" if not step["observation"].get("ok") else "[未通过]" if step["observation"].get("passed") is False else "") for step in tools) or "无工具执行"
    rows.append(f"- **{case}**：{sequence}。最终 `{result['status']}`。")

summary = ROOT / "examples/test-results/summary.json"
if summary.exists():
    stats = json.loads(summary.read_text(encoding="utf-8"))
    rows.extend(["", "## 自动测试", "", f"实际运行 {stats['tests_run']} 项，失败 {stats['failures']}，错误 {stats['errors']}，跳过 {stats['skipped']}。Python {stats['python']}。",
                 "[机器摘要](../examples/test-results/summary.json) / [完整测试输出](../examples/test-results/unittest.txt)。"])
rows.extend(["", "## 失败与限制", "",
             "保留的早期失败：`examples/runs/glm47_attempt/`、`examples/runs/glm_second_attempt/`，以及 glm 下的 initial_429_failure、flash250414_protocol_failure、title_caption_failure。这些是实际失败，不应计为成功路径。", "",
             "免费模型出现过 HTTP 429（服务返回代码 1305），旧版免费模型也出现过普通文本代替函数调用。有限重试不能保证服务可用。真实样例不是稳定成功率测量，未在大量独立样本上评估。", "",
             "修正包括：对遗漏来源 ID 的问题返回精确匹配候选；批准的安全标题允许用作旁白/字幕；每次修改使检查失效。新检查结果不能追溯性地改写旧运行文件。", "",
             "文案采用允许列表和逐字事实匹配；检索为关键词，时长为规则估算。没有任意自然语言事实校验、真实配音测量、UI、视频制作或线上部署。候选人独立复现情况见 AI 使用记录。", ""])
(ROOT / "docs/03-evaluation.md").write_text("\n".join(rows), encoding="utf-8")
print("Updated docs/03-evaluation.md from saved evidence")
