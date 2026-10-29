# 验证结果与证据

本报告由 `python scripts/evaluate.py` 从实际结果生成。Mock 仅验证流程；真实模型证据以 glm 列为准。

| 场景 | 模式/模型 | 实际状态 | 工具调用 | 预计秒数 | 结果和 Trace |
|---|---|---|---|---|---|
| normal | mock/offline-fixed-policy-v1 | completed | 5 | 11 | [结果](../examples/runs/mock/normal/result.json) / [Trace](../examples/runs/mock/normal/trace.jsonl) / [脚本](../examples/runs/mock/normal/script.md) |
| missing | mock/offline-fixed-policy-v1 | needs_input | 0 | — | [结果](../examples/runs/mock/missing/result.json) / [Trace](../examples/runs/mock/missing/trace.jsonl) / [脚本](../examples/runs/mock/missing/script.md) |
| no_material | mock/offline-fixed-policy-v1 | needs_input | 2 | — | [结果](../examples/runs/mock/no_material/result.json) / [Trace](../examples/runs/mock/no_material/trace.jsonl) / [脚本](../examples/runs/mock/no_material/script.md) |
| tool_failure | mock/offline-fixed-policy-v1 | failed | 2 | — | [结果](../examples/runs/mock/tool_failure/result.json) / [Trace](../examples/runs/mock/tool_failure/trace.jsonl) / [脚本](../examples/runs/mock/tool_failure/script.md) |
| over_duration | mock/offline-fixed-policy-v1 | completed | 6 | 11 | [结果](../examples/runs/mock/over_duration/result.json) / [Trace](../examples/runs/mock/over_duration/trace.jsonl) / [脚本](../examples/runs/mock/over_duration/script.md) |
| unsupported_claim | mock/offline-fixed-policy-v1 | incomplete | 4 | 5 | [结果](../examples/runs/mock/unsupported_claim/result.json) / [Trace](../examples/runs/mock/unsupported_claim/trace.jsonl) / [脚本](../examples/runs/mock/unsupported_claim/script.md) |
| step_limit | mock/offline-fixed-policy-v1 | incomplete | 2 | — | [结果](../examples/runs/mock/step_limit/result.json) / [Trace](../examples/runs/mock/step_limit/trace.jsonl) / [脚本](../examples/runs/mock/step_limit/script.md) |
| normal | glm/glm-4.7-flash | completed | 5 | 30 | [结果](../examples/runs/glm/normal/result.json) / [Trace](../examples/runs/glm/normal/trace.jsonl) / [脚本](../examples/runs/glm/normal/script.md) |
| missing | glm/glm-4.7-flash | needs_input | 0 | — | [结果](../examples/runs/glm/missing/result.json) / [Trace](../examples/runs/glm/missing/trace.jsonl) / [脚本](../examples/runs/glm/missing/script.md) |
| no_material | glm/glm-4.7-flash | failed | 3 | — | [结果](../examples/runs/glm/no_material/result.json) / [Trace](../examples/runs/glm/no_material/trace.jsonl) / [脚本](../examples/runs/glm/no_material/script.md) |
| tool_failure | glm/glm-4.7-flash | failed | 5 | 19.0 | [结果](../examples/runs/glm/tool_failure/result.json) / [Trace](../examples/runs/glm/tool_failure/trace.jsonl) / [脚本](../examples/runs/glm/tool_failure/script.md) |
| over_duration | glm/glm-4.7-flash | failed | 0 | — | [结果](../examples/runs/glm/over_duration/result.json) / [Trace](../examples/runs/glm/over_duration/trace.jsonl) / [脚本](../examples/runs/glm/over_duration/script.md) |
| unsupported_claim | glm/glm-4.7-flash | completed | 12 | 23.75 | [结果](../examples/runs/glm/unsupported_claim/result.json) / [Trace](../examples/runs/glm/unsupported_claim/trace.jsonl) / [脚本](../examples/runs/glm/unsupported_claim/script.md) |
| step_limit | glm/glm-4.7-flash | incomplete | 2 | — | [结果](../examples/runs/glm/step_limit/result.json) / [Trace](../examples/runs/glm/step_limit/trace.jsonl) / [脚本](../examples/runs/glm/step_limit/script.md) |

## 测试预期

normal 应完成并通过两项检查；missing 应列出缺失项；no_material 应补查或请求资料；tool_failure 应观察错误并恢复或明确失败；over_duration 应检查初稿超时并修正复查，或明确未完成；unsupported_claim 应识别无依据主张并修正或明确未完成；step_limit 应触顶后返回 incomplete。模型服务错误只能证明故障处理，不能替代相应业务验收。

## 真实路径

- **normal**：search_materials → set_script → estimate_duration → check_script → finish。最终 `completed`。
- **missing**：无工具执行。最终 `needs_input`。
- **no_material**：search_materials → search_materials → search_materials。最终 `failed`。
- **tool_failure**：search_materials[失败] → search_materials → set_script → estimate_duration → check_script。最终 `failed`。
- **over_duration**：无工具执行。最终 `failed`。
- **unsupported_claim**：search_materials → set_script → check_script[未通过] → set_script → estimate_duration → set_script → check_script → estimate_duration → set_script → check_script → estimate_duration → finish。最终 `completed`。
- **step_limit**：search_materials → set_script。最终 `incomplete`。

## 自动测试

实际运行 27 项，失败 0，错误 0，跳过 0。Python 3.12.3。
[机器摘要](../examples/test-results/summary.json) / [完整测试输出](../examples/test-results/unittest.txt)。

## 失败与限制

保留的早期失败：`examples/runs/glm47_attempt/`、`examples/runs/glm_second_attempt/`，以及 glm 下的 initial_429_failure、flash250414_protocol_failure、title_caption_failure。这些是实际失败，不应计为成功路径。

免费模型出现过 HTTP 429（服务返回代码 1305），旧版免费模型也出现过普通文本代替函数调用。有限重试不能保证服务可用。真实样例不是稳定成功率测量，未在大量独立样本上评估。

修正包括：对遗漏来源 ID 的问题返回精确匹配候选；批准的安全标题允许用作旁白/字幕；每次修改使检查失效。新检查结果不能追溯性地改写旧运行文件。

文案采用允许列表和逐字事实匹配；检索为关键词，时长为规则估算。没有任意自然语言事实校验、真实配音测量、UI、视频制作或线上部署。候选人独立复现情况见 AI 使用记录。

## 其他有效证据

无素材场景的一次较早真实运行成功返回 needs_input：[结果](../examples/runs/glm47_attempt/no_material/result.json) / [Trace](../examples/runs/glm47_attempt/no_material/trace.jsonl)。模型先检索，观察到零条资料后请求补充。后续同输入仍可能遭遇服务限流，上表如实列出最近一次结果。

`examples/runs/glm/over_duration_preemptive_edit/` 是模型先修改后检查的旧运行，不能单独证明超时反馈后的修订。最终代码已要求先观察初稿，后续复现请看上表 over_duration 的实际步骤。

较早的免费模型真实超时反馈路径：[结果](../examples/runs/glm/over_duration_429_failure/result.json) / [Trace](../examples/runs/glm/over_duration_429_failure/trace.jsonl)。工具依次返回 44、34、31 秒，模型确实据反馈修订，但仍未满足 30 秒上限，随后因模型服务限流明确失败。免费模型的三次有界复测也保留在 over_duration_final_attempt_1..3，均未获得超时修订成功验证。付费模型追加结果见下节（如已运行）。

干净代码副本的 [复现报告](../examples/test-results/clean-reproduction.json) 包含被验证的代码 commit、测试数量和离线 CLI 结果。实际用时记录见 [worklog.json](../examples/worklog.json)。

## 付费模型追加验证

候选人明确授权付费模型复测后，切换 GLM-4.7。Agent 代码、提示词、输入和规则不因切换而修改；旧免费模型结果保留。此次小样本只能证明所记录的执行，不代表稳定成功率或付费必然消除限流。

| 场景 | 模型 | 状态 | 工具调用 | 实际估算反馈（秒） | 证据 |
|---|---|---|---|---|---|
| normal | glm-4.7 | completed | 5 | 27（通过） | [结果](../examples/runs/glm_paid/normal/result.json) / [Trace](../examples/runs/glm_paid/normal/trace.jsonl) / [脚本](../examples/runs/glm_paid/normal/script.md) |
| over_duration | glm-4.7 | completed | 6 | 44（超时） → 26（通过） | [结果](../examples/runs/glm_paid/over_duration/result.json) / [Trace](../examples/runs/glm_paid/over_duration/trace.jsonl) / [脚本](../examples/runs/glm_paid/over_duration/script.md) |

真实动作路径：

- **normal**：search_materials → set_script → estimate_duration → check_script → finish；最终 `completed`。
- **over_duration**：estimate_duration[未通过] → search_materials → set_script → estimate_duration → check_script → finish；最终 `completed`。
