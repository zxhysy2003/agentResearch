# AgentResearch 评测入门

这个目录存放 AgentResearch 的**评测题目、参考答案、评分规则和供检索的资料**。先读懂一条题目，再看数据格式和代码，会更容易理解。

**开始做 MVP，请先打开 [GitHub 信息检索数据集](datasets/github_lookup_v1/README.md)：10 道已由用户确认人工审阅通过的题目，配套 10 份真实资料快照。**

`examples/` 中的 5 条题目及 `snapshots/demo-v1/` 是虚构教学数据，用于演示格式和验证程序。原始 50 条任务保留在 [真实资料审阅目录](../research_data_review/agentresearch_real_v1/README.md)；本次只选用其中的 GitHub 类，其余 40 条未纳入 MVP。原审阅目录保持原样，新的审阅确认记录见 [review.json](datasets/github_lookup_v1/review.json)。

## 1. Agent 评测到底在做什么？

你可以把一次评测理解为一次允许查资料的考试：

| 考试中的东西 | 本项目中的名字 | 作用 |
| --- | --- | --- |
| 题目 | `task` | 告诉 Agent 要解决什么问题 |
| 可查阅的资料 | `snapshots` | 提供文档、仓库信息等材料 |
| 参考答案及依据 | `ground_truth` | 说明哪些事实和结论是正确的 |
| 评分标准 | `evaluation_rule` | 决定哪些地方给分、什么情况下通过 |
| 答卷和操作记录 | `BenchmarkRun` | 保存实际回答、工具调用和耗时 |
| 成绩单 | `EvaluationResult` | 保存各项得分、理由和是否通过 |

**Benchmark 就是一套可以反复使用的题目与评测规则。** 改了 Agent 的提示词、模型或搜索策略后，用相同题目和资料重新测试，才能比较它是否进步。

研究 Agent 不仅要答对，还应提供支持结论的来源，并在需要时实际查证。答案碰巧正确、引用却无关，也可能无法通过。

## 2. 各文件夹和文件分别做什么？

```text
benchmarks/
├── README.md                    # 你正在读的说明
├── datasets/                    # 用于实际实验的数据集
│   └── github_lookup_v1/        # GitHub 检索 MVP
│       ├── README.md            # 题目索引、使用说明
│       ├── review.json          # 人工审阅确认与版本记录
│       ├── validation.json      # 数据完整性检查结果
│       └── cases/               # 10 道题，各自包含问题、答案和评分规则
├── examples/                    # 5 道完整教学题，每个 JSON 文件是一道题
│   ├── github_release_001.json  # GitHub 版本查询
│   ├── official_docs_001.json   # 官方文档理解
│   ├── comparison_001.json      # 技术方案比较
│   ├── multi_hop_001.json       # 多步检索与信息关联
│   └── edge_case_001.json       # 查询遇到异常后的处理
├── snapshots/                   # 做题时允许查阅的固定资料
│   ├── github_lookup_v1/        # MVP 使用的真实资料
│   │   ├── README.md
│   │   ├── manifest.json       # 10 份原始资料的清单
│   │   └── sources/            # 原始响应、可读文本和采集信息
│   └── demo-v1/                 # 一套名为 demo-v1 的教学资料
│       ├── manifest.json       # 资料清单、文件指纹和模拟故障配置
│       ├── release.json        # 两条版本发布记录
│       ├── docs.json           # 关于会话状态恢复的说明
│       ├── comparison.json     # 两个虚构产品的功能资料
│       ├── frameworks.json     # 四个虚构框架的资料
│       └── recovery.json       # 模拟超时恢复后可获取的仓库信息
└── schema.json                 # 程序检查题目格式时使用的规则
```

### datasets/：MVP 使用的真实题目

`datasets/github_lookup_v1/cases/` 是当前实验选用的 10 道题。其目录中的 README 有逐题入口，`review.json` 记录用户的审阅确认，`validation.json` 只记录数据检查结果。配套资料放在 `snapshots/github_lookup_v1/`。实际运行应明确选择这套题，不要把教学题一起加载。

### examples/：题目、答案和评分标准放在一起

每个文件都是一条完整的评测样本，包含 `task`、`environment`、`ground_truth` 和 `evaluation_rule`。参考答案没有单独放在另一个文件夹。

这些完整文件供出题者和评测程序使用。**运行 Agent 时，不能把整个文件直接塞进提示词，否则会把答案泄露给它。** 代码中的 `case.agent_input()` 只返回题目、允许工具及预算。

### snapshots/：保存做题用的原始资料

快照（snapshot）就是保存下来的某个时刻的资料。比如今天查到的最新版本是 1.4，明天发布了 1.5；若每次直接联网，同一道题的答案就变了。固定资料能让不同运行具有可比性。

`demo-v1/` 是一套资料的名字。将来新增一套资料，可以使用新的目录和快照 ID。这里是人工构造的演示资料；真实快照可以保存实际抓取的官方文档或 API 响应。

`manifest.json` 相当于资料目录，记录：

- **ID 和文件路径**：例如资料 `release` 对应 `release.json`。
- **来源地址和采集时间**：说明材料来自哪里、何时保存。教学数据中的 `example.invalid` 是占位地址，不用联网访问。
- **SHA-256**：文件内容的“指纹”，用于发现资料是否被改过；它不能证明资料内容本身正确。
- **faults**：可选的模拟故障配置。这里的 `timeout_once` 让指定查询第一次匹配调用超时，用于测试恢复行为。这是教学场景，不能当作真实网络故障记录。

### schema.json：题目格式说明，不是题库

Schema 可以理解为“填表规则”：哪些字段必填、允许什么类型、可以使用哪些分类。它不包含某道题的参考答案，也不判断技术事实是否正确。

这个文件由 Python 数据模型生成。普通标注工作编辑 `datasets/` 中的实际题目或 `examples/` 中的教学题，不需要手工修改它。

### 评测代码在哪里？

`benchmarks/` 放数据，执行逻辑在目录外：

| 位置 | 作用 |
| --- | --- |
| [src/benchmark/models.py](../src/benchmark/models.py) | 定义题目、运行记录和成绩单的字段，并检查字段关系 |
| [src/benchmark/dataset.py](../src/benchmark/dataset.py) | 读取题目、检查快照指纹、检索资料、辅助模拟故障 |
| [src/benchmark/evaluation.py](../src/benchmark/evaluation.py) | 提供事实匹配、实体关联检查和总分计算 |
| [tests/benchmark/](../tests/benchmark/) | 检查上述程序是否按预期工作 |

## 3. 跟着一道题走一遍

先打开 [github_release_001.json](examples/github_release_001.json)。它问的是：

> 查询 example-org/demo-agent 最新稳定 Release 的版本和 UTC 发布日期；排除 draft 和 prerelease。

这是一个虚构项目，配套的 [release.json](snapshots/demo-v1/release.json) 有两条记录：

| 版本 | 发布时间（UTC） | 是否预发布 |
| --- | --- | --- |
| v1.4.0 | 2026-08-20 08:00:00 | 否 |
| v1.5.0rc1 | 2026-08-25 08:00:00 | 是 |

虽然第二条发布时间更晚，但题目要求稳定版，因此参考答案是 **v1.4.0，发布日期 2026-08-20**。

这道题的四部分分别表达：

| 字段 | 在这道题里的含义 |
| --- | --- |
| `task` | 问什么，以及“最新”截至哪个时间；`as_of` 在这里是 2026-09-01 |
| `environment` | 使用 `demo-v1` 资料，最多调用工具 15 次，最长运行 120 秒 |
| `ground_truth` | 版本应为 v1.4.0、发布日期应为 2026-08-20，并注明支撑资料 |
| `evaluation_rule` | 分别检查版本、日期、引用是否支持答案，以及工具记录是否显示查阅了依据 |

文件里的几个 ID 只是用来连起这些部分：

```text
c_version（版本检查）
  → target: f_version（要检查的事实）
  → evidence_ids: e_release（该事实的证据）
  → artifact_id: release（清单中的资料 ID）
  → manifest.json 中的 path: release.json（实际文件）
```

因此，`f_version` 不是版本号，它是这条事实的名字。真正的参考值在 `expected.value` 中。

完整评测应先让 Agent 查资料和回答，再拿它的回答与这些规则比较。**当前命令行的 `validate` 只检查数据，不执行这个做题过程。**

## 4. 五类题为什么不能只匹配一段标准答案？

| 类别 | 想测什么 | 参考答案如何组织 |
| --- | --- | --- |
| GitHub 信息检索 | 能否找到正确版本、日期、许可证等 | 列出可直接核对的事实（`facts`） |
| 官方文档检索 | 能否理解用法、条件和限制 | 列出回答必须解释的要点（`rubrics`） |
| 多来源技术比较 | 能否按需求比较，并用事实支持建议 | 列出比较维度及事实要求，不设唯一“赢家” |
| 多跳 Research | 能否把多个来源里的同一项目正确关联 | 规定项目条件、数量及关联字段（`entity_requirements`） |
| 异常／边界任务 | 遇到失败或信息不足时是否如实处理 | 规定预期状态、恢复行为和不能编造的内容 |

`rubric` 就是“评分要点”。例如，解释状态恢复时，应同时说明如何识别同一会话、使用什么存储、重启后能否保留数据。意思正确即可，不要求逐字复述。

`ground_truth.expected_outcome` 表示期望 Agent 最终如何回应：完整回答（`answered`）、部分回答（`partial`）、请求澄清（`needs_clarification`）或说明证据不足（`insufficient_evidence`）。诚实说明信息不足可以是正确行为，不能统一视为失败。

## 5. 分数怎么算？

每个检查项的得分范围是 0～1。语义评分项的 `anchors` 给出 0、0.5、1 分各自应满足的条件；真实题目需要写清具体条件，不能只写“回答得好”。

分数分为三个维度：

- **correctness（正确性）**：事实和解释是否正确、要求是否覆盖。
- **evidence（证据）**：引用的内容是否真的支持结论，而不只是附了一个链接。
- **process（过程）**：工具调用记录是否体现必要的查证或异常恢复，不要求读取模型内部思维链。

先在各维度内部按检查项权重求平均，再按维度权重算总分。上面的版本题使用：

```text
总分 = 正确性 × 70% + 证据 × 20% + 过程 × 10%
```

假设版本、日期和引用检查都得满分，但过程检查为 0，则总分为 0.9。**这道题仍不通过**，因为过程检查标有 `required: true`，表示必须拿满分。

通过还要求：达到题目阈值（示例为 0.8）、所有必要项满分、回答状态符合预期、运行完成且没有超出预算。分数与“是否通过”是两个不同结果。

评测程序出错也要单独记录。例如语义评委不可用，应标为 `evaluation_error`，不能给 Agent 算成零分。

## 6. 第一次使用，建议按这个顺序

### 第一步：读一题，再读对应资料

先看 [版本查询示例](examples/github_release_001.json) 和 [版本资料](snapshots/demo-v1/release.json)，按照第 3 节找到题目、事实、证据及检查项。暂时不用通读 `schema.json`。

### 第二步：检查这五道题是否填写正确

以下命令在**仓库根目录**运行。假设项目依赖已安装，`.venv/bin/python` 存在；这项检查不需要 API key，也不联网。

```sh
PYTHONPATH=src .venv/bin/python -m benchmark validate \
  benchmarks/examples/*.json \
  --manifest benchmarks/snapshots/demo-v1/manifest.json
```

成功时，每道题会输出一行 `Valid: ...`。这表示字段、引用和快照完整性检查通过，**不表示 Agent 答对了，也不表示参考答案经过了事实核验**。

### 第三步：确认评测辅助程序的测试通过

```sh
.venv/bin/pytest tests/benchmark -q
```

这是程序的单元测试。测试通过说明已覆盖的程序行为符合预期，不是 Agent 的能力得分。

### 第四步：审阅真实来源的题目

当前已有 [10 条人工审阅通过的 GitHub 题](datasets/github_lookup_v1/README.md)，可按其 README 的命令检查 MVP 数据。其他类别仍可从 [50 条原始任务的审阅入口](../research_data_review/agentresearch_real_v1/README.md) 查看；未纳入本次实验。

只有修改了 Python 数据模型，才需要重新导出格式文件；下面这条命令会写入 `schema.json`：

```sh
PYTHONPATH=src .venv/bin/python -m benchmark schema benchmarks/schema.json
```

## 7. 目前能做什么，完整评测还缺什么？

目前已具备题目格式、示例资料、数据校验、事实与实体匹配辅助函数、评分扩展接口和总分计算。

**已支持命令行快照运行与人工评分。** `run` 执行题目并保存回答、完整轨迹及待填写评分表；`grade` 校验人工评分并生成报告。使用方法见 [最小评测闭环](../docs/Benchmark_Run.md)。

默认使用十道 GitHub MVP 开发题和 DeepSeek 非思考模式。模型评委、实时联网评测和更大规模的检索资料仍需后续建设；数据校验通过不等于 Agent 答题通过。

快照检索遇到没有的资料时，应明确记录未找到，不能悄悄联网补充，否则不同运行面对的资料不再相同。当前的快照读取类本身不会阻止 Agent 使用其他联网工具，隔离需要在运行适配器中落实。

## 8. 开始编写题目或接入代码时再看这里

### 常用字段和评测器

| 名称 | 含义或使用注意 |
| --- | --- |
| `revision` | 题目版本；修改答案或规则时递增 |
| `snapshot_id` | 使用哪套资料；修改资料时建立新快照版本 |
| `evidence_ids` / `artifact_id` | 前者引用答案证据，后者引用快照中的原始文件 |
| `locator` | 指出证据在原文中的位置；当前不会自动解析该定位描述 |
| `fact_match` | 比较提取出的事实；支持版本前缀、日期精度、数值容差和集合规则 |
| `rubric_judge` | 根据要点和评分档位判断语义；需要接入实际评委 |
| `entity_constraint` | 检查项目数量、去重和属性关联，允许满足条件的替代组合 |
| `citation_support` | 检查引用内容是否支持论点、版本和来源是否适用；需要接入实际判断逻辑 |
| `trace_assertion` | 检查工具轨迹中是否有查证、状态或恢复行为；需要接入实际判断逻辑 |

`evaluate(case, run, evaluators)` 接收各评测器的回调函数；每个函数返回一项 `CheckResult`。`aggregate` 负责汇总已有评分，不能替代阅读答案和证据。运行记录必须对应相同的题目 ID、题目版本和快照 ID。

### 编写真实题目的约定

- 一道题一个 UTF-8 JSON 文件；当前加载器不接受 YAML 专用语法。JSONL 是多道 JSON 题目一行一条组成的合集。
- 固定问题的时间和软件版本。无 Release 不等于无 tag，访问失败不等于项目不存在，归档不等于无法查询。
- 比较题写明应用场景与必需维度；开放式答案允许等价表达。证据目录不必是唯一合法 URL 白名单，但其他引用也必须在允许的资料范围内且确实支持结论。
- 人工复核参考答案；如果使用模型评委，记录模型、提示词和采样配置，并抽查判分。
- 当前示例都属于开发集 `dev`，不是用于最终验收的隐藏测试集。以后划分开发集和测试集时，避免同一问题的改写出现在两边。
- 扩展到五类题后，报告成绩时按类别分别统计，再对类别成绩取平均；错误或无效样本单列。当前 MVP 报告仅覆盖 GitHub 类，耗时、调用数与 token 用量单列。实时联网 `live` 模式目前仅预留，尚未支持。
