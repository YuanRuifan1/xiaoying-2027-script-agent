# 评估结果

本报告通过 `python scripts/evaluate.py` 从实际保存的执行结果生成，按验收点索引对应运行记录。

## 真实模型验证

| 验收场景 | 模型 | 状态 | 工具调用 | 验证结果 | 证据 |
|---|---|---|---|---|---|
| 正常生成 | glm-4.7 | completed | 5 | 完整脚本，两项检查通过 | [结果](../examples/runs/glm_paid/normal/result.json) / [Trace](../examples/runs/glm_paid/normal/trace.jsonl) / [脚本](../examples/runs/glm_paid/normal/script.md) |
| 缺关键信息 | glm-4.7-flash | needs_input | 0 | 列出缺失字段，返回 needs_input | [结果](../examples/runs/glm/missing/result.json) / [Trace](../examples/runs/glm/missing/trace.jsonl) / [脚本](../examples/runs/glm/missing/script.md) |
| 无匹配素材 | glm-4.7-flash | needs_input | 2 | 根据零条检索结果请求补充 | [结果](../examples/runs/glm47_attempt/no_material/result.json) / [Trace](../examples/runs/glm47_attempt/no_material/trace.jsonl) / [脚本](../examples/runs/glm47_attempt/no_material/script.md) |
| 工具失败 | glm-4.7-flash | failed | 5 | 观察注入错误并重试，保留结果；随后 API 限流终止 | [结果](../examples/runs/glm/tool_failure/result.json) / [Trace](../examples/runs/glm/tool_failure/trace.jsonl) / [脚本](../examples/runs/glm/tool_failure/script.md) |
| 超时修订 | glm-4.7 | completed | 6 | 观察 44 秒初稿，修订为 26 秒并复查通过 | [结果](../examples/runs/glm_paid/over_duration/result.json) / [Trace](../examples/runs/glm_paid/over_duration/trace.jsonl) / [脚本](../examples/runs/glm_paid/over_duration/script.md) |
| 无依据主张 | glm-4.7-flash | completed | 12 | 识别并修正无依据表述，再次检查通过 | [结果](../examples/runs/glm/unsupported_claim/result.json) / [Trace](../examples/runs/glm/unsupported_claim/trace.jsonl) / [脚本](../examples/runs/glm/unsupported_claim/script.md) |
| 执行上限 | glm-4.7-flash | incomplete | 2 | 两次工具调用后返回 incomplete | [结果](../examples/runs/glm/step_limit/result.json) / [Trace](../examples/runs/glm/step_limit/trace.jsonl) / [脚本](../examples/runs/glm/step_limit/script.md) |

## 动态决策路径

- **正常生成**：search_materials → set_script → estimate_duration → check_script → finish；最终 `completed`。
- **缺关键信息**：输入校验后结束；最终 `needs_input`。
- **无匹配素材**：search_materials → finish；最终 `needs_input`。
- **工具失败**：search_materials[错误] → search_materials → set_script → estimate_duration → check_script；最终 `failed`。
- **超时修订**：estimate_duration[未通过] → search_materials → set_script → estimate_duration → check_script → finish；最终 `completed`。
- **无依据主张**：search_materials → set_script → check_script[未通过] → set_script → estimate_duration → set_script → check_script → estimate_duration → set_script → check_script → estimate_duration → finish；最终 `completed`。
- **执行上限**：search_materials → set_script；最终 `incomplete`。

## 付费模型追加验证

本地复现反馈限流问题后，项目选择 GLM-4.7 复测。两次运行沿用相同 Agent 代码、提示词、资料和输入，共 11 次模型请求返回 HTTP 200。

| 场景 | 模型 | 状态 | 实际时长反馈 | 证据 |
|---|---|---|---|---|
| normal | glm-4.7 | completed | 27（通过） 秒 | [结果](../examples/runs/glm_paid/normal/result.json) / [Trace](../examples/runs/glm_paid/normal/trace.jsonl) / [脚本](../examples/runs/glm_paid/normal/script.md) |
| over_duration | glm-4.7 | completed | 44（超时） → 26（通过） 秒 | [结果](../examples/runs/glm_paid/over_duration/result.json) / [Trace](../examples/runs/glm_paid/over_duration/trace.jsonl) / [脚本](../examples/runs/glm_paid/over_duration/script.md) |

## 自动测试与离线验证

Python 3.12.3，执行 27 项测试，失败 0，错误 0，跳过 0。

[测试摘要](../examples/test-results/summary.json) / [完整输出](../examples/test-results/unittest.txt) / [干净副本复现](../examples/test-results/clean-reproduction.json)。

离线 Mock 使用固定策略验证工具、状态和错误处理；真实模型决策使用上面的运行记录。

| 场景 | 离线状态 | 工具调用 | 证据 |
|---|---|---|---|
| 正常生成 | completed | 5 | [结果](../examples/runs/mock/normal/result.json) / [Trace](../examples/runs/mock/normal/trace.jsonl) / [脚本](../examples/runs/mock/normal/script.md) |
| 缺关键信息 | needs_input | 0 | [结果](../examples/runs/mock/missing/result.json) / [Trace](../examples/runs/mock/missing/trace.jsonl) / [脚本](../examples/runs/mock/missing/script.md) |
| 无匹配素材 | needs_input | 2 | [结果](../examples/runs/mock/no_material/result.json) / [Trace](../examples/runs/mock/no_material/trace.jsonl) / [脚本](../examples/runs/mock/no_material/script.md) |
| 工具失败 | failed | 2 | [结果](../examples/runs/mock/tool_failure/result.json) / [Trace](../examples/runs/mock/tool_failure/trace.jsonl) / [脚本](../examples/runs/mock/tool_failure/script.md) |
| 超时修订 | completed | 6 | [结果](../examples/runs/mock/over_duration/result.json) / [Trace](../examples/runs/mock/over_duration/trace.jsonl) / [脚本](../examples/runs/mock/over_duration/script.md) |
| 无依据主张 | incomplete | 4 | [结果](../examples/runs/mock/unsupported_claim/result.json) / [Trace](../examples/runs/mock/unsupported_claim/trace.jsonl) / [脚本](../examples/runs/mock/unsupported_claim/script.md) |
| 执行上限 | incomplete | 2 | [结果](../examples/runs/mock/step_limit/result.json) / [Trace](../examples/runs/mock/step_limit/trace.jsonl) / [脚本](../examples/runs/mock/step_limit/script.md) |

## 运行问题与改进

| 观察到的问题 | 处理方式 | 运行记录 |
|---|---|---|
| 免费接口 HTTP 429 | 增加有界退避，保留失败状态；根据复现反馈切换 GLM-4.7 验证 | [早期记录](../examples/runs/glm/initial_429_failure/result.json) / [超时修订成功记录](../examples/runs/glm_paid/over_duration/result.json) |
| 产品句遗漏来源或引用不支持主张 | 检查工具返回问题位置和可匹配来源，由模型修改后复查 | [修订 Trace](../examples/runs/glm/unsupported_claim/trace.jsonl) |
| 初稿在观察前被提前编辑 | 加入先估算初稿再允许修改的前置条件 | [早期记录](../examples/runs/glm/over_duration_preemptive_edit/result.json) / [最终路径](../examples/runs/glm_paid/over_duration/trace.jsonl) |

早期完整运行继续保存在 `examples/runs/glm/`、`examples/runs/glm47_attempt/` 和 `examples/runs/glm_second_attempt/`。上表工具失败场景实际观察到注入错误和重试，最终因模型服务 HTTP 429 结束，状态为 failed。

用时与迭代记录见 [worklog.json](../examples/worklog.json)，个人贡献见 [AI 使用记录](04-ai-usage.md)，设计取舍和后续改进见 [复盘](05-retrospective.md)。
