# GitHub 信息检索 MVP 数据集 v1

这是一套供 MVP 使用的 **10 道 GitHub 信息检索题**，已依据用户在会话中的明确确认记录为人工审阅通过。它使用 2026-09-29 采集的真实资料，属于开发集 `dev`。

## 先看这三个位置

| 位置 | 放什么 | 谁来使用 |
| --- | --- | --- |
| [cases/](cases/) | 每题的 task、ground_truth、evaluation_rule 及运行环境 | 评测程序；不能整份交给 Agent |
| [快照目录](../../snapshots/github_lookup_v1/) | 做题可检索的原始资料 | 通过工具提供给 Agent |
| [review.json](review.json) | 用户审阅确认、来源路径、版本和文件指纹 | 审阅者与维护者 |

`validation.json` 是数据完整性检查结果，不是 Agent 的成绩。原始 50 条审阅数据与教学示例仍保留，本数据集不包含其余四类题目。

## 十道题

| ID / 题目文件 | 问题 | 正确性评分方式 |
| --- | --- | --- |
| [github_lookup_01](cases/github_lookup_01.json) | 采集时 fastapi/fastapi 的 GitHub stars 数是多少？说明统计时刻。 | 事实匹配（facts） |
| [github_lookup_02](cases/github_lookup_02.json) | GitHub 将 qdrant/qdrant 的主要编程语言识别为什么？ | 事实匹配（facts） |
| [github_lookup_03](cases/github_lookup_03.json) | GitHub API 为 encode/httpx 返回的 SPDX 许可证标识是什么？ | 事实匹配（facts） |
| [github_lookup_04](cases/github_lookup_04.json) | 查询 browser-use/browser-use 的 GitHub latest Release 标签和发布时间。 | 事实匹配（facts） |
| [github_lookup_05](cases/github_lookup_05.json) | 查询 pydantic/pydantic 的 GitHub latest Release 标签和发布时间，不把 prerelease 当成稳定版。 | 事实匹配（facts） |
| [github_lookup_06](cases/github_lookup_06.json) | 查询 qdrant/qdrant 的 GitHub latest Release 标签及 UTC 发布时间。 | 事实匹配（facts） |
| [github_lookup_07](cases/github_lookup_07.json) | 从采集的 encode/httpx 已关闭 bug 查询结果中，找出标题涉及 PoolTimeout 与 asyncio.gather 的 issue，报告编号、标题和关闭时间。 | 事实匹配（facts） |
| [github_lookup_08](cases/github_lookup_08.json) | browser-use README 的 Python Library 安装段落声明的最低 Python 版本是什么？新建项目的 uv 示例又选择哪个版本？ | 语义要点评分（rubrics） |
| [github_lookup_09](cases/github_lookup_09.json) | LangGraph README 是否说明 durable execution 和 human-in-the-loop？分别概括其用途。 | 语义要点评分（rubrics） |
| [github_lookup_10](cases/github_lookup_10.json) | CrewAI 官方仓库的完整名称、默认分支和 GitHub 许可证标识是什么？ | 事实匹配（facts） |

## 题目与快照怎样关联？

例如，第 1 题询问 FastAPI 在采集时的 stars 数：

```text
cases/github_lookup_01.json
  environment.snapshot_id = github_lookup_v1
  ground_truth.evidence 中的 artifact_id = repo_fastapi
                   ↓
../../snapshots/github_lookup_v1/manifest.json
  资料 repo_fastapi 的 path = sources/repo_fastapi/body
                   ↓
../../snapshots/github_lookup_v1/sources/repo_fastapi/body
  原始 GitHub API 响应
```

每份资料还附有 `text.txt`（方便阅读）和 `metadata.json`（请求 URL、最终 URL、采集时间等）。这些文件按原字节复制，原始响应的 SHA-256 与审阅集一致。

## 本次整理改了什么？

- 提取 10 条题目，以及它们引用的 10 份去重资料；没有重新联网采集。
- 题目 ID 保持不变；revision 从 1 升为 2，表示重新打包后的版本。
- snapshot_id 改为 `github_lookup_v1`，标签记录为 `human_reviewed` 和 `mvp`。
- 问题、参考答案、证据时间和评分规则均保持原样；审阅确认是用户提供的，不是程序冒充人工审核。

## 在仓库根目录检查数据

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m benchmark validate \
  benchmarks/datasets/github_lookup_v1/cases/*.json \
  --manifest benchmarks/snapshots/github_lookup_v1/manifest.json
```

预期输出 10 行 `Valid: github_lookup_XX`。这只说明数据格式和资料引用校验通过，不会启动 Agent，也不会自动给回答判分。

## MVP 的运行边界

- 仅从本目录 `cases/` 读取题目，不递归加载全部 `benchmarks/`，避免混入教学题。
- 快照工具应只检索本快照清单中的原始资料；所有题目使用同一个资料集合，不按题目 ID 直接派发答案资料。
- 只向 Agent 提供 `case.agent_input()`；不要暴露题目完整 JSON、审阅页、评分规则或 `review.json`。
- URL 读取应映射到清单中的本地资料；未命中返回未找到，禁止回退真实网络。搜索能力和网络隔离仍需运行适配器接入。
- 这套快照只含相关资料，是限定资料范围的评测，不能代表整个互联网搜索难度。stars 和 latest Release 均按原采集时刻回答。
- 第 8、9 题使用 rubrics；初期可人工判分。引用和过程检查也需要评测适配器或人工给分。
- 保留已有规则的局限，例如第 1 题未单设统计时间检查；本次人工审阅确认不等于所有评分细节都已完善。
- 下一步才是接入 Agent 执行、轨迹保存和评分；本次整理没有生成运行记录或能力成绩。
