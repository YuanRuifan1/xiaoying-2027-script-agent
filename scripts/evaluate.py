"""Build the submission evidence index from actual saved execution records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("normal", "正常生成", "glm_paid/normal", "完整脚本，两项检查通过"),
    ("missing", "缺关键信息", "glm/missing", "列出缺失字段，返回 needs_input"),
    ("no_material", "无匹配素材", "glm47_attempt/no_material", "根据零条检索结果请求补充"),
    ("tool_failure", "工具失败", "glm/tool_failure", "观察注入错误并重试，保留结果；随后 API 限流终止"),
    ("over_duration", "超时修订", "glm_paid/over_duration", "观察 44 秒初稿，修订为 26 秒并复查通过"),
    ("unsupported_claim", "无依据主张", "glm/unsupported_claim", "识别并修正无依据表述，再次检查通过"),
    ("step_limit", "执行上限", "glm/step_limit", "两次工具调用后返回 incomplete"),
]


def read_result(folder):
    return json.loads((ROOT / "examples/runs" / folder / "result.json").read_text(encoding="utf-8"))


def links(folder):
    base = "../examples/runs/" + folder
    return f"[结果]({base}/result.json) / [Trace]({base}/trace.jsonl) / [脚本]({base}/script.md)"


def sequence(result):
    names = []
    for step in result["trace"]:
        if step.get("kind") != "tool":
            continue
        observation = step["observation"]
        suffix = "[错误]" if not observation.get("ok") else "[未通过]" if observation.get("passed") is False else ""
        names.append(step["tool"] + suffix)
    return " → ".join(names) or "输入校验后结束"


rows = ["# 评估结果", "", "本报告通过 `python scripts/evaluate.py` 从实际保存的执行结果生成，按验收点索引对应运行记录。", "",
        "## 真实模型验证", "", "| 验收场景 | 模型 | 状态 | 工具调用 | 验证结果 | 证据 |", "|---|---|---|---|---|---|"]
for case, label, folder, conclusion in CASES:
    result = read_result(folder)
    rows.append(f"| {label} | {result['model']} | {result['status']} | {result['tool_calls']} | {conclusion} | {links(folder)} |")

rows.extend(["", "## 动态决策路径", ""])
for case, label, folder, conclusion in CASES:
    result = read_result(folder)
    rows.append(f"- **{label}**：{sequence(result)}；最终 `{result['status']}`。")

rows.extend(["", "## 付费模型追加验证", "", "本地复现反馈限流问题后，项目选择 GLM-4.7 复测。两次运行沿用相同 Agent 代码、提示词、资料和输入，共 11 次模型请求返回 HTTP 200。", "",
             "| 场景 | 模型 | 状态 | 实际时长反馈 | 证据 |", "|---|---|---|---|---|"])
for case in ("normal", "over_duration"):
    folder = "glm_paid/" + case
    result = read_result(folder)
    estimates = [str(s["observation"]["total_seconds"]) + ("（通过）" if s["observation"]["passed"] else "（超时）")
                 for s in result["trace"] if s.get("tool") == "estimate_duration" and s["observation"].get("ok")]
    rows.append(f"| {case} | {result['model']} | {result['status']} | {' → '.join(estimates)} 秒 | {links(folder)} |")

rows.extend(["", "## 自动测试与离线验证", ""])
stats = json.loads((ROOT / "examples/test-results/summary.json").read_text(encoding="utf-8"))
rows.extend([f"Python {stats['python']}，执行 {stats['tests_run']} 项测试，失败 {stats['failures']}，错误 {stats['errors']}，跳过 {stats['skipped']}。",
             "", "[测试摘要](../examples/test-results/summary.json) / [完整输出](../examples/test-results/unittest.txt) / [干净副本复现](../examples/test-results/clean-reproduction.json)。", "",
             "离线 Mock 使用固定策略验证工具、状态和错误处理；真实模型决策使用上面的运行记录。", "",
             "| 场景 | 离线状态 | 工具调用 | 证据 |", "|---|---|---|---|"])
for case, label, folder, conclusion in CASES:
    mock_folder = "mock/" + case
    result = read_result(mock_folder)
    rows.append(f"| {label} | {result['status']} | {result['tool_calls']} | {links(mock_folder)} |")

rows.extend(["", "## 运行问题与改进", "",
             "| 观察到的问题 | 处理方式 | 运行记录 |", "|---|---|---|",
             "| 免费接口 HTTP 429 | 增加有界退避，保留失败状态；根据复现反馈切换 GLM-4.7 验证 | [早期记录](../examples/runs/glm/initial_429_failure/result.json) / [超时修订成功记录](../examples/runs/glm_paid/over_duration/result.json) |",
             "| 产品句遗漏来源或引用不支持主张 | 检查工具返回问题位置和可匹配来源，由模型修改后复查 | [修订 Trace](../examples/runs/glm/unsupported_claim/trace.jsonl) |",
             "| 初稿在观察前被提前编辑 | 加入先估算初稿再允许修改的前置条件 | [早期记录](../examples/runs/glm/over_duration_preemptive_edit/result.json) / [最终路径](../examples/runs/glm_paid/over_duration/trace.jsonl) |", "",
             "早期完整运行继续保存在 `examples/runs/glm/`、`examples/runs/glm47_attempt/` 和 `examples/runs/glm_second_attempt/`。上表工具失败场景实际观察到注入错误和重试，最终因模型服务 HTTP 429 结束，状态为 failed。", "",
             "用时与迭代记录见 [worklog.json](../examples/worklog.json)，个人贡献见 [AI 使用记录](04-ai-usage.md)，设计取舍和后续改进见 [复盘](05-retrospective.md)。", ""])
(ROOT / "docs/03-evaluation.md").write_text("\n".join(rows), encoding="utf-8")
print("Updated docs/03-evaluation.md from saved execution evidence")
