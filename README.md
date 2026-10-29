# 短视频脚本 Agent

根据主题、受众、平台、目标时长和风格生成可编辑分镜脚本。模型检索产品资料、调用时长和规则检查工具，再根据反馈修订脚本，输出脚本、来源引用和完整执行记录。演示产品及资料均为合成数据。

## 运行结果与阅读入口

| 场景 | 实际结果 | 查看材料 |
|---|---|---|
| 正常生成 | GLM-4.7 生成 27 秒脚本，两项检查通过 | [脚本](examples/runs/glm_paid/normal/script.md) / [Trace](examples/runs/glm_paid/normal/trace.jsonl) |
| 超时修订 | 先观察 44 秒初稿，再修订为 26 秒并复查通过 | [脚本](examples/runs/glm_paid/over_duration/script.md) / [Trace](examples/runs/glm_paid/over_duration/trace.jsonl) |
| 产品主张修正 | 识别无依据的效果表述，修改后完成 | [脚本](examples/runs/glm/unsupported_claim/script.md) / [Trace](examples/runs/glm/unsupported_claim/trace.jsonl) |

项目文档：[需求与验收](docs/01-requirements.md) · [方案设计](docs/02-solution.md) · [评估报告](docs/03-evaluation.md) · [个人贡献与 AI 使用](docs/04-ai-usage.md) · [复盘](docs/05-retrospective.md)。

## 环境与离线运行

Python >=3.10，开发验证环境为 Windows / Python 3.12.3。运行和测试使用 Python 标准库，无第三方运行依赖。在仓库根目录执行 PowerShell 命令：

```powershell
python -m venv .venv
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m script_agent --provider mock --input examples/inputs/normal.json --output private-runs/demo
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

离线模式无需配置密钥，用于验证工具、状态和错误处理流程；真实模型决策记录见上表。已有虚拟环境时可跳过创建步骤。

Linux/macOS 使用 `export PYTHONPATH="$PWD/src"` 和 `.venv/bin/python`。也可通过 `python -m pip install -e .` 安装 `script-agent` 命令。数据默认从当前目录的 `data/` 读取，可使用 `--data` 指定目录。

## 真实模型运行

首次配置时复制模板，在编辑器中填写本地密钥：

```powershell
if (!(Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
```

使用已验证的付费模型 GLM-4.7（需要可用账户额度）：

```powershell
$env:GLM_MODEL = 'glm-4.7'
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m script_agent --provider glm --input examples/inputs/normal.json --output private-runs/real
.\.venv\Scripts\python.exe -m script_agent --provider glm --input examples/inputs/over_duration.json --output private-runs/over-duration
```

也可直接在 `.env` 设置 `GLM_MODEL=glm-4.7`。配置模板提供 `glm-4.7-flash` 选项；进程环境变量优先于 `.env`，模型切换由配置显式控制。密钥仅用于 HTTPS 请求头，`.env` 已由 Git 排除。

接口参考：[GLM-4.7](https://docs.bigmodel.cn/cn/guide/models/text/glm-4.7) · [函数调用](https://docs.bigmodel.cn/cn/guide/capabilities/function-calling) · [对话接口](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)。

## 输入、输出与状态

输入必填字段为 `theme`、`audience`、`platform`、`target_seconds`、`style`，可选 `initial_draft` 用于修改已有脚本。目标时长按上限校验。

每次运行生成三个文件：

- `script.md`：标题、分镜、旁白/字幕、逐镜头预计时长和检查结果。
- `result.json`：完整输入、最终状态、脚本、来源引用和工具报告。
- `trace.jsonl`：每步工具参数、观察结果、简要动作依据及请求用量。

`completed` 退出码为 0；`needs_input`、`incomplete`、`failed` 退出码为 2。缺少必要字段会返回待补充项。默认最多 16 次模型轮次和 16 次工具调用，可通过 `--max-calls` 设置；HTTP 429 最多尝试 3 次，达到执行上限后明确返回未完成。

## 场景验证与复现

```powershell
# 批量离线样例，并保存实际结果
.\.venv\Scripts\python.exe scripts/run_examples.py --provider mock
# 注入一次工具故障
.\.venv\Scripts\python.exe -m script_agent --provider glm --input examples/inputs/normal.json --fail-tool search_materials --output private-runs/tool-failure
# 测试报告与证据索引
.\.venv\Scripts\python.exe scripts/check.py
.\.venv\Scripts\python.exe scripts/evaluate.py
```

覆盖正常生成、缺信息、无素材、工具失败、超时修订、无依据主张和执行上限。批量样例命令会更新同名记录目录；个人复现可像上述命令一样输出到 `private-runs/`。

27 项自动测试已有通过记录。[干净代码副本复现报告](examples/test-results/clean-reproduction.json) 记录了被验证的 commit、测试数量和离线 CLI 结果；可通过 `python scripts/reproduce_clean.py` 复现。

## 项目交付

公开仓库：[短视频脚本 Agent](https://github.com/YuanRuifan1/xiaoying-2027-script-agent)。提交时使用 `git rev-parse HEAD` 获取最终 commit SHA，并与远程 main 核对。项目用时与迭代记录见 [worklog.json](examples/worklog.json)，设计取舍和下一步见 [复盘](docs/05-retrospective.md)。
