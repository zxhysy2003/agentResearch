# 运行 AgentResearch 最小评测闭环

首版流程为：固定题目 → DeepSeek 原生工具调用 → 保存回答和证据 → 人工评分 → 汇总报告。默认使用 `github_lookup_v1` 的十道开发题，结果不能代表整个互联网的搜索能力。

## 准备与运行

按项目要求使用 Python 3.12–3.14、uv 0.12.5 和锁定依赖。在本地 `.env` 或进程环境中配置 `DEEPSEEK_API_KEY`，不要提交密钥。只有 `run` 需要该密钥；`validate`、`schema`、`grade` 不读取服务模型配置。

```bash
uv sync --frozen
PYTHONPATH=src uv run python -m benchmark validate \
  benchmarks/datasets/github_lookup_v1/cases/*.json \
  --manifest benchmarks/snapshots/github_lookup_v1/manifest.json
```

先运行一题验证接入，然后运行十题。每个输出目录代表一个独立实验，必须选择尚不存在的目录。

```bash
PYTHONPATH=src uv run python -m benchmark run \
  --case-id github_lookup_04 --output benchmark_runs/smoke-release

PYTHONPATH=src uv run python -m benchmark run \
  --case-id github_lookup_08 --output benchmark_runs/smoke-readme

PYTHONPATH=src uv run python -m benchmark run \
  --model deepseek-flash --repeat 1 --output benchmark_runs/baseline-v1
```

`--case-id` 可以重复传入。`--cases-dir` 与 `--manifest` 可以指定另一套经过校验的快照，默认不会递归混入教学题。真实推理调用产生模型 API 费用；工具只访问 manifest 中的本地资料，不访问 GitHub MCP 或真实网页。

## 工具与预算

| 工具 | 输入与行为 |
| --- | --- |
| `web_search` | 输入 `query`；检索所有快照，最多返回五条 URL、采集时间和 500 字符摘要。查询优先使用仓库名或英文技术词。 |
| `fetch_page` | 输入精确 `url` 和可选 `offset`；每次读取最多 12,000 字符。 |
| `github_read` | 输入 `repository`、`resource`，以及可选 `path`、`offset`。资源类型为 `repository`、`latest_release`、`issues`、`file`；文件必须指定相对路径。 |

原文返回 `next_offset`、总字符数、资料 ID、来源 URL 和采集时间。需要更多内容时继续读取，直到 `next_offset` 为 null。Issue 数据仅代表来源 URL 中记录的查询范围；文件使用采集时的分支内容。未收录的资源返回未找到，不回退联网。

模型固定为 `deepseek-flash`，关闭思考模式和流式输出，temperature 为 0，关闭 SDK 自动重试。模型只收到 `case.agent_input()` 和工具返回资料；题目时间用于解释“最新”和统计值。通过 API 的 `response_format={"type":"json_object"}` 约束最终输出，再校验 `answer` 与 `outcome` 字段；工具调用仍使用模型原生协议。格式错误或空输出仍会保存并记录为运行错误。

每题使用独立会话，按题目配置限制总时间及工具调用次数。一次模型响应中多个调用按顺序分别计数，失败的工具调用也计入预算。模型可以根据工具错误继续尝试。超时或超出调用预算标记 `budget_exceeded`；推理错误或最终 JSON 无效标记 `agent_error`。单题失败后继续运行其余题目，并返回非零退出码。

## 查看记录与填写评分

输出根目录保存实验配置、快照清单及 `summary.json`、`summary.md`。每个 `run-0001` 等子目录保存：

- `run.json`：符合 `BenchmarkRun` 的回答、状态、轨迹、耗时和用量。
- `messages.json`：完整对话，包含原生工具调用 ID 和结果消息。
- `error.json`：模型或运行错误；正常运行时为 null。
- `case.json`：供评分者查看的题目、参考答案和评分规则副本，不提供给 Agent。
- `review.json`：待填写的人工评分表，分数初始为 null。
- `evaluation.json`：当前评分状态或汇总成绩。

先查看 `case.json` 的检查项、参考答案和评分锚点，再核对 `run.json` 的回答与轨迹。尤其要确认引用支持结论，而且原文确实被读取，而非只有搜索摘要。

编辑每个 `review.json`：填写 `reviewer`，为每个检查项填写 `score` 和非空 `reason`，可在 `evidence_refs` 填入 `case.json` 中的证据 ID，如 `e_1`。不要修改关联标识及哈希。例如，一个评分项可以填写为：

```json
{
  "check_id": "c_citations",
  "score": 1,
  "reason": "引用的 Release 原文支持回答，轨迹记录显示实际查阅了该来源。",
  "evidence_refs": ["e_1", "e_2"]
}
```

然后重新生成报告：

```bash
PYTHONPATH=src uv run python -m benchmark grade \
  --run-dir benchmark_runs/baseline-v1
```

未填完分数的记录保持未评分，不按零分计。重复或缺失检查项、超范围分数、未知证据 ID、缺少评分理由，以及评分表与运行记录不匹配，均标为评分错误。修改已保存的回答或题目会使旧评分表失效。重跑 `grade` 会重新检查评分表，避免沿用过期结果。

报告分别列出运行失败、未评分、评分错误和有效成绩，展示评分覆盖率。成功率与平均质量分仅统计有效评分；运行失败不能通过既有汇总规则。耗时、调用次数与 token 用量单列；缺失用量标记未知，不计算为零或免费。

## 建立后续基线

接入稳定后，每题重复三次并分别人工评分：

```bash
PYTHONPATH=src uv run python -m benchmark run \
  --repeat 3 --output benchmark_runs/baseline-v1-repeat3
```

比较版本时使用相同题目、快照、模型参数、预算及评分规则，同时检查覆盖率和逐题失败原因。记录包含代码及提示词哈希、工具版本、包版本和模型返回的版本信息。模型服务若未提供可锁定版本，应同期重跑旧 Agent。

`benchmark_runs/` 已加入 Git 忽略规则。原始题目、评分规则与快照哈希不应为了改善成绩而更改。后续扩大资料集合时建立新的快照版本，并在同一版本内比较不同 Agent。
