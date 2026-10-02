# GitHub 信息检索（10 条）

[返回总览](README.md)

## github_lookup_01：FastAPI stars

**任务：** 采集时 fastapi/fastapi 的 GitHub stars 数是多少？说明统计时刻。

**快照时间边界：** 2026-09-29T14:35:35.237227Z

[完整 JSON](cases/github_lookup/github_lookup_01.json)

**Ground truth / 必需评分项：**

- `repo_fastapi.stargazers_count` = `102713`（证据：e_1）

**来源与定位：**

- `e_1` [repo_fastapi](https://api.github.com/repos/fastapi/fastapi) · [本地资料](sources/repo_fastapi/text.txt) · JSON Pointer: /stargazers_count

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_02：Qdrant 主语言

**任务：** GitHub 将 qdrant/qdrant 的主要编程语言识别为什么？

**快照时间边界：** 2026-09-29T14:35:34.926097Z

[完整 JSON](cases/github_lookup/github_lookup_02.json)

**Ground truth / 必需评分项：**

- `repo_qdrant.primary_language` = `"Rust"`（证据：e_1）

**来源与定位：**

- `e_1` [repo_qdrant](https://api.github.com/repos/qdrant/qdrant) · [本地资料](sources/repo_qdrant/text.txt) · JSON Pointer: /language

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_03：HTTPX 许可证标识

**任务：** GitHub API 为 encode/httpx 返回的 SPDX 许可证标识是什么？

**快照时间边界：** 2026-09-29T14:35:35.421495Z

[完整 JSON](cases/github_lookup/github_lookup_03.json)

**Ground truth / 必需评分项：**

- `repo_httpx.license_spdx` = `"BSD-3-Clause"`（证据：e_1）

**来源与定位：**

- `e_1` [repo_httpx](https://api.github.com/repos/encode/httpx) · [本地资料](sources/repo_httpx/text.txt) · JSON Pointer: /license/spdx_id

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_04：Browser Use 最新 Release

**任务：** 查询 browser-use/browser-use 的 GitHub latest Release 标签和发布时间。

**快照时间边界：** 2026-09-29T14:39:15.698010Z

[完整 JSON](cases/github_lookup/github_lookup_04.json)

**Ground truth / 必需评分项：**

- `latest_browser.github_latest_tag` = `"0.13.10"`（证据：e_1）
- `latest_browser.published_at` = `"2026-09-04T03:28:53Z"`（证据：e_2）

**来源与定位：**

- `e_1` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · JSON Pointer: /tag_name
- `e_2` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_05：Pydantic 最新 Release

**任务：** 查询 pydantic/pydantic 的 GitHub latest Release 标签和发布时间，不把 prerelease 当成稳定版。

**快照时间边界：** 2026-09-29T14:39:15.735090Z

[完整 JSON](cases/github_lookup/github_lookup_05.json)

**Ground truth / 必需评分项：**

- `latest_pydantic.github_latest_tag` = `"v2.13.5"`（证据：e_1）
- `latest_pydantic.published_at` = `"2026-08-28T14:06:45Z"`（证据：e_2）

**来源与定位：**

- `e_1` [latest_pydantic](https://api.github.com/repos/pydantic/pydantic/releases/latest) · [本地资料](sources/latest_pydantic/text.txt) · JSON Pointer: /tag_name
- `e_2` [latest_pydantic](https://api.github.com/repos/pydantic/pydantic/releases/latest) · [本地资料](sources/latest_pydantic/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_06：Qdrant Release 发布时间

**任务：** 查询 qdrant/qdrant 的 GitHub latest Release 标签及 UTC 发布时间。

**快照时间边界：** 2026-09-29T14:39:16.135835Z

[完整 JSON](cases/github_lookup/github_lookup_06.json)

**Ground truth / 必需评分项：**

- `latest_qdrant.github_latest_tag` = `"v1.19.1"`（证据：e_1）
- `latest_qdrant.published_at` = `"2026-09-04T07:59:14Z"`（证据：e_2）

**来源与定位：**

- `e_1` [latest_qdrant](https://api.github.com/repos/qdrant/qdrant/releases/latest) · [本地资料](sources/latest_qdrant/text.txt) · JSON Pointer: /tag_name
- `e_2` [latest_qdrant](https://api.github.com/repos/qdrant/qdrant/releases/latest) · [本地资料](sources/latest_qdrant/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_07：HTTPX 已关闭 bug

**任务：** 从采集的 encode/httpx 已关闭 bug 查询结果中，找出标题涉及 PoolTimeout 与 asyncio.gather 的 issue，报告编号、标题和关闭时间。

**快照时间边界：** 2026-09-29T14:35:37.798713Z

[完整 JSON](cases/github_lookup/github_lookup_07.json)

**Ground truth / 必需评分项：**

- `issues_httpx.number` = `1171`（证据：e_1）
- `issues_httpx.title` = `"PoolTimeout when num tasks in asyncio.gather() exceeds client max_connections"`（证据：e_2）
- `issues_httpx.closed_at` = `"2024-02-12T11:20:32Z"`（证据：e_3）

**来源与定位：**

- `e_1` [issues_httpx](https://api.github.com/repos/encode/httpx/issues?state=closed&labels=bug&sort=updated&direction=desc&per_page=10) · [本地资料](sources/issues_httpx/text.txt) · JSON Pointer: /0/number
- `e_2` [issues_httpx](https://api.github.com/repos/encode/httpx/issues?state=closed&labels=bug&sort=updated&direction=desc&per_page=10) · [本地资料](sources/issues_httpx/text.txt) · JSON Pointer: /0/title
- `e_3` [issues_httpx](https://api.github.com/repos/encode/httpx/issues?state=closed&labels=bug&sort=updated&direction=desc&per_page=10) · [本地资料](sources/issues_httpx/text.txt) · JSON Pointer: /0/closed_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_08：Browser Use Python 安装说明

**任务：** browser-use README 的 Python Library 安装段落声明的最低 Python 版本是什么？新建项目的 uv 示例又选择哪个版本？

**快照时间边界：** 2026-09-29T14:35:34.768675Z

[完整 JSON](cases/github_lookup/github_lookup_08.json)

**Ground truth / 必需评分项：**

- 最低版本为 Python 3.11；新建项目示例使用 Python 3.12。这是最低要求与示例选择的区别。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [browser_readme](https://raw.githubusercontent.com/browser-use/browser-use/main/README.md) · [本地资料](sources/browser_readme/text.txt) · text.txt:L99-L99; locate nearby section
- `e_2` [browser_readme](https://raw.githubusercontent.com/browser-use/browser-use/main/README.md) · [本地资料](sources/browser_readme/text.txt) · text.txt:L101-L101; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_09：LangGraph README 能力

**任务：** LangGraph README 是否说明 durable execution 和 human-in-the-loop？分别概括其用途。

**快照时间边界：** 2026-09-29T14:35:34.389368Z

[完整 JSON](cases/github_lookup/github_lookup_09.json)

**Ground truth / 必需评分项：**

- Durable execution 面向故障后恢复与长时间运行；human-in-the-loop 支持执行过程中检查和修改 Agent 状态。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [langgraph_readme](https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md) · [本地资料](sources/langgraph_readme/text.txt) · text.txt:L39-L39; locate nearby section
- `e_2` [langgraph_readme](https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md) · [本地资料](sources/langgraph_readme/text.txt) · text.txt:L40-L40; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## github_lookup_10：CrewAI 仓库身份

**任务：** CrewAI 官方仓库的完整名称、默认分支和 GitHub 许可证标识是什么？

**快照时间边界：** 2026-09-29T14:35:35.428989Z

[完整 JSON](cases/github_lookup/github_lookup_10.json)

**Ground truth / 必需评分项：**

- `repo_crewai.full_name` = `"crewAIInc/crewAI"`（证据：e_1）
- `repo_crewai.default_branch` = `"main"`（证据：e_2）
- `repo_crewai.license_spdx` = `"MIT"`（证据：e_3）

**来源与定位：**

- `e_1` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /full_name
- `e_2` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /default_branch
- `e_3` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /license/spdx_id

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

