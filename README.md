# 短视频脚本 Agent · 小影科技 2027 校招第 4 题

为创作者生成有来源、满足预计时长上限的可编辑分镜脚本。产品“剪映星球”与全部资料均为合成，与真实产品无关。

## 评审入口

1. 阅读 [需求与验收映射](docs/01-requirements.md) 和 [实现与取舍](docs/02-solution.md)。
2. 运行下方离线入口及自动测试，查看 [评估报告](docs/03-evaluation.md)。
3. 查看 `examples/runs/glm/` 的真实模型结果与 Trace；`examples/runs/mock/` 仅是固定策略的工程验证，不能作为模型决策证据。
4. 阅读 [AI 使用记录](docs/04-ai-usage.md) 与 [复盘](docs/05-retrospective.md)。

## 环境和安装

Python >=3.10，开发环境为 Windows / Python 3.12.3。运行与测试只依赖标准库；不需要安装第三方框架。
从仓库根目录执行以下 PowerShell 命令：

```powershell
python -m venv .venv
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m script_agent --provider mock --input examples/inputs/normal.json --output private-runs/demo
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Linux/macOS 对应设置 `export PYTHONPATH="$PWD/src"`，解释器使用 `.venv/bin/python`。
也可执行 `python -m pip install -e .` 安装 CLI 后使用 `script-agent`。该方式需要可用的 setuptools 构建工具；上述 PYTHONPATH 方式完全不需要下载依赖。数据默认从当前目录的 `data/` 读取，请在仓库根目录运行，或显式设置 `--data`。

## 真实模型入口

```powershell
Copy-Item .env.example .env
# 在编辑器中填写 GLM_API_KEY；不要把密钥放进命令或聊天。
$env:PYTHONPATH = "$PWD\src"
python -m script_agent --provider glm --input examples/inputs/normal.json --output private-runs/real
```

默认 `glm-4.7-flash`，不自动切换付费模型。模型是否仍免费、账户可用性和限流以智谱控制台为准。
进程环境变量优先于 `.env`。不需要密钥即可运行离线入口。真实请求使用 HTTPS 和官方接口；密钥仅用于请求头，不存入运行记录。

GLM 参考：[官方免费模型系列与工具支持](https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash)、[函数调用协议](https://docs.bigmodel.cn/cn/guide/capabilities/function-calling)、[接口文档](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)。查阅日期 2026-10-29。

## 输入和输出

输入字段：`theme`、`audience`、`platform`、`target_seconds`、`style`；可选 `initial_draft` 用于修改已有脚本。
缺少必要字段时返回 `needs_input`；无效数值和非法输入返回非零退出码。

每次输出目录包含：

- `result.json`：输入、最终脚本、任务状态、逐镜头时长、引用、风险、完整 Trace。
- `trace.jsonl`：逐步骤工具参数、返回值、简要依据、token 用量和网络请求次数。
- `script.md`：可编辑分镜表及检查报告。

`completed` 退出码为 0；`needs_input`、`incomplete`、`failed` 退出码为 2。仅有脚本文件不代表通过验收，请看任务状态。

## 复现验收样例

```powershell
python scripts/run_examples.py --provider mock
python scripts/run_examples.py --provider glm
# 只复现超时修订：
python scripts/run_examples.py --provider glm --case over_duration
# 单次注入工具故障：
python -m script_agent --provider glm --input examples/inputs/normal.json --fail-tool check_script --output private-runs/failure
python scripts/check.py
```

真实模型输出具有随机性；验证检查通过与状态正确，不断言固定措辞或固定工具调用顺序。样例命令会覆盖同名运行目录，保留重要历史运行前请另存目录。

默认最多 16 次模型轮次和 16 次工具调用（包含结束动作），可用 `--max-calls` 设置 1..100。每次模型请求最多 3 次 HTTP 尝试，只有 429 做有界退避，均写入 Trace；网络重试不算模型业务决策。

## 已知限制

- 首版采用受控文案：事实句逐字引用资料，标题、非事实句和画面说明使用允许列表。创作自由度有限，不支持任意文案的语义事实验证。
- 受众、平台和风格用于允许选项的选择，不保证开放式风格生成。
- 检索为小规模中文关键词匹配，不是向量检索；改写长查询不一定命中。
- 时长按语速规则估算，未经 TTS 或真实配音测量；目标解释为时长上限，不承诺恰好填满。
- 不制作视频、不真实发布、不提供 Web UI 或部署。
- 当前候选人的代码审阅与独立复现情况见 AI 使用记录，尚未完成的步骤不标记为完成。

## GitHub 交付

公开仓库：[YuanRuifan1/xiaoying-2027-script-agent](https://github.com/YuanRuifan1/xiaoying-2027-script-agent)。提交题号为第 4 题。最终 SHA 使用 `git rev-parse HEAD` 获取，并与远程 main 核对；后续修改必须更新提交 SHA。

干净副本复现结果见 [clean-reproduction.json](examples/test-results/clean-reproduction.json)。`python scripts/reproduce_clean.py` 会从当前已提交版本导出干净代码，运行测试及离线 CLI，不携带 `.env`、虚拟环境或本地安装包。记录的 source_commit 指向实际被验证的版本。
