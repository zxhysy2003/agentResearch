# 多跳 Research（10 条）

[返回总览](README.md)

## multi_hop_01：Python Agent 项目版本比较

**任务：** 核验 browser-use/browser-use、crewAIInc/crewAI、pydantic/pydantic-ai 是否都被 GitHub 识别为 Python 且许可证为 MIT，再查询各自 latest Release 的发布时间并排序。

**快照时间边界：** 2026-09-29T14:39:16.671847Z

[完整 JSON](cases/multi_hop/multi_hop_01.json)

**Ground truth / 必需评分项：**

- `repo_browser.full_name` = `"browser-use/browser-use"`（证据：e_1）
- `repo_browser.primary_language` = `"Python"`（证据：e_2）
- `repo_browser.license_spdx` = `"MIT"`（证据：e_3）
- `latest_browser.github_latest_tag` = `"0.13.10"`（证据：e_4）
- `latest_browser.published_at` = `"2026-09-04T03:28:53Z"`（证据：e_5）
- `repo_crewai.full_name` = `"crewAIInc/crewAI"`（证据：e_6）
- `repo_crewai.primary_language` = `"Python"`（证据：e_7）
- `repo_crewai.license_spdx` = `"MIT"`（证据：e_8）
- `latest_crewai.github_latest_tag` = `"1.15.23"`（证据：e_9）
- `latest_crewai.published_at` = `"2026-09-28T21:14:32Z"`（证据：e_10）
- `repo_pydantic_ai.full_name` = `"pydantic/pydantic-ai"`（证据：e_11）
- `repo_pydantic_ai.primary_language` = `"Python"`（证据：e_12）
- `repo_pydantic_ai.license_spdx` = `"MIT"`（证据：e_13）
- `latest_pydantic_ai.github_latest_tag` = `"v2.51.0"`（证据：e_14）
- `latest_pydantic_ai.published_at` = `"2026-09-25T23:19:04Z"`（证据：e_15）
- 按所采集 latest Release 发布时间从新到旧为：crewAIInc/crewAI、pydantic/pydantic-ai、browser-use/browser-use。（证据：e_16, e_17, e_18）

**来源与定位：**

- `e_1` [repo_browser](https://api.github.com/repos/browser-use/browser-use) · [本地资料](sources/repo_browser/text.txt) · JSON Pointer: /full_name
- `e_2` [repo_browser](https://api.github.com/repos/browser-use/browser-use) · [本地资料](sources/repo_browser/text.txt) · JSON Pointer: /language
- `e_3` [repo_browser](https://api.github.com/repos/browser-use/browser-use) · [本地资料](sources/repo_browser/text.txt) · JSON Pointer: /license/spdx_id
- `e_4` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · JSON Pointer: /tag_name
- `e_5` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · JSON Pointer: /published_at
- `e_6` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /full_name
- `e_7` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /language
- `e_8` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /license/spdx_id
- `e_9` [latest_crewai](https://api.github.com/repos/crewAIInc/crewAI/releases/latest) · [本地资料](sources/latest_crewai/text.txt) · JSON Pointer: /tag_name
- `e_10` [latest_crewai](https://api.github.com/repos/crewAIInc/crewAI/releases/latest) · [本地资料](sources/latest_crewai/text.txt) · JSON Pointer: /published_at
- `e_11` [repo_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai) · [本地资料](sources/repo_pydantic_ai/text.txt) · JSON Pointer: /full_name
- `e_12` [repo_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai) · [本地资料](sources/repo_pydantic_ai/text.txt) · JSON Pointer: /language
- `e_13` [repo_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai) · [本地资料](sources/repo_pydantic_ai/text.txt) · JSON Pointer: /license/spdx_id
- `e_14` [latest_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai/releases/latest) · [本地资料](sources/latest_pydantic_ai/text.txt) · JSON Pointer: /tag_name
- `e_15` [latest_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai/releases/latest) · [本地资料](sources/latest_pydantic_ai/text.txt) · JSON Pointer: /published_at
- `e_16` [latest_crewai](https://api.github.com/repos/crewAIInc/crewAI/releases/latest) · [本地资料](sources/latest_crewai/text.txt) · text.txt:L1-L1; locate nearby section
- `e_17` [latest_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai/releases/latest) · [本地资料](sources/latest_pydantic_ai/text.txt) · text.txt:L1-L1; locate nearby section
- `e_18` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_02：向量项目实现与能力关联

**任务：** 将 Qdrant 和 pgvector 的官方仓库、主要语言与距离能力对应起来，确认哪个是 PostgreSQL 扩展，避免把元数据配到另一个项目。

**快照时间边界：** 2026-09-29T14:35:35.410943Z

[完整 JSON](cases/multi_hop/multi_hop_02.json)

**Ground truth / 必需评分项：**

- `repo_qdrant.full_name` = `"qdrant/qdrant"`（证据：e_1）
- `repo_qdrant.primary_language` = `"Rust"`（证据：e_2）
- `repo_pgvector.full_name` = `"pgvector/pgvector"`（证据：e_3）
- `repo_pgvector.primary_language` = `"C"`（证据：e_4）
- Qdrant 对应 Rust 和 collection 度量配置；pgvector 对应 C 和 PostgreSQL 扩展，支持 SQL 距离算子。（证据：e_5, e_6）

**来源与定位：**

- `e_1` [repo_qdrant](https://api.github.com/repos/qdrant/qdrant) · [本地资料](sources/repo_qdrant/text.txt) · JSON Pointer: /full_name
- `e_2` [repo_qdrant](https://api.github.com/repos/qdrant/qdrant) · [本地资料](sources/repo_qdrant/text.txt) · JSON Pointer: /language
- `e_3` [repo_pgvector](https://api.github.com/repos/pgvector/pgvector) · [本地资料](sources/repo_pgvector/text.txt) · JSON Pointer: /full_name
- `e_4` [repo_pgvector](https://api.github.com/repos/pgvector/pgvector) · [本地资料](sources/repo_pgvector/text.txt) · JSON Pointer: /language
- `e_5` [qdrant_collections](https://qdrant.tech/documentation/concepts/collections/) · [本地资料](sources/qdrant_collections/text.txt) · text.txt:L240-L240; locate nearby section
- `e_6` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L58-L58; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_03：从归档项目追踪替代库

**任务：** 检查 encode/requests-async 是否归档，阅读它推荐的替代客户端，再查询替代库的官方仓库许可证与 latest Release。

**快照时间边界：** 2026-09-29T14:39:16.189405Z

[完整 JSON](cases/multi_hop/multi_hop_03.json)

**Ground truth / 必需评分项：**

- `repo_requests_async.archived` = `true`（证据：e_1）
- `repo_httpx.full_name` = `"encode/httpx"`（证据：e_3）
- `repo_httpx.license_spdx` = `"BSD-3-Clause"`（证据：e_4）
- `latest_httpx.github_latest_tag` = `"0.28.1"`（证据：e_5）
- `latest_httpx.published_at` = `"2024-12-06T15:36:24Z"`（证据：e_6）
- README 推荐 httpx.AsyncClient()，替代项目是 encode/httpx。（证据：e_2）

**来源与定位：**

- `e_1` [repo_requests_async](https://api.github.com/repos/encode/requests-async) · [本地资料](sources/repo_requests_async/text.txt) · JSON Pointer: /archived
- `e_2` [requests_async_readme](https://raw.githubusercontent.com/encode/requests-async/master/README.md) · [本地资料](sources/requests_async_readme/text.txt) · text.txt:L3-L3; locate nearby section
- `e_3` [repo_httpx](https://api.github.com/repos/encode/httpx) · [本地资料](sources/repo_httpx/text.txt) · JSON Pointer: /full_name
- `e_4` [repo_httpx](https://api.github.com/repos/encode/httpx) · [本地资料](sources/repo_httpx/text.txt) · JSON Pointer: /license/spdx_id
- `e_5` [latest_httpx](https://api.github.com/repos/encode/httpx/releases/latest) · [本地资料](sources/latest_httpx/text.txt) · JSON Pointer: /tag_name
- `e_6` [latest_httpx](https://api.github.com/repos/encode/httpx/releases/latest) · [本地资料](sources/latest_httpx/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_04：Browser Use Python 版本交叉核验

**任务：** 交叉核验 browser-use 默认分支 README 的最低 Python、uv 示例版本和 pyproject.toml 的 requires-python，然后报告 GitHub latest Release；不要假设默认分支文件就是该 tag 的文件。

**快照时间边界：** 2026-09-29T14:39:15.698010Z

[完整 JSON](cases/multi_hop/multi_hop_04.json)

**Ground truth / 必需评分项：**

- `latest_browser.github_latest_tag` = `"0.13.10"`（证据：e_4）
- `latest_browser.published_at` = `"2026-09-04T03:28:53Z"`（证据：e_5）
- README 最低 Python 3.11，uv 示例选 3.12；当前默认分支 pyproject 声明 >=3.11,<4.0，示例版本并非最低版本。（证据：e_1, e_2, e_3）

**来源与定位：**

- `e_1` [browser_readme](https://raw.githubusercontent.com/browser-use/browser-use/main/README.md) · [本地资料](sources/browser_readme/text.txt) · text.txt:L99-L99; locate nearby section
- `e_2` [browser_readme](https://raw.githubusercontent.com/browser-use/browser-use/main/README.md) · [本地资料](sources/browser_readme/text.txt) · text.txt:L101-L101; locate nearby section
- `e_3` [browser_pyproject](https://raw.githubusercontent.com/browser-use/browser-use/main/pyproject.toml) · [本地资料](sources/browser_pyproject/text.txt) · text.txt:L7-L7; locate nearby section
- `e_4` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · JSON Pointer: /tag_name
- `e_5` [latest_browser](https://api.github.com/repos/browser-use/browser-use/releases/latest) · [本地资料](sources/latest_browser/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_05：LangGraph 持久化与仓库确认

**任务：** 从 LangGraph 官方持久化文档区分 checkpointer 和 store 的用途，再确认官方 GitHub 仓库身份与许可证。

**快照时间边界：** 2026-09-29T14:39:15.674898Z

[完整 JSON](cases/multi_hop/multi_hop_05.json)

**Ground truth / 必需评分项：**

- `repo_langgraph.full_name` = `"langchain-ai/langgraph"`（证据：e_3）
- `repo_langgraph.license_spdx` = `"MIT"`（证据：e_4）
- checkpointer 用于线程内短期记忆，store 用于跨会话长期记忆；线程恢复需要稳定 thread_id。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [langgraph_persistence](https://docs.langchain.com/oss/python/langgraph/persistence) · [本地资料](sources/langgraph_persistence/text.txt) · text.txt:L84-L84; locate nearby section
- `e_2` [langgraph_persistence](https://docs.langchain.com/oss/python/langgraph/persistence) · [本地资料](sources/langgraph_persistence/text.txt) · text.txt:L187-L188; locate nearby section
- `e_3` [repo_langgraph](https://api.github.com/repos/langchain-ai/langgraph) · [本地资料](sources/repo_langgraph/text.txt) · JSON Pointer: /full_name
- `e_4` [repo_langgraph](https://api.github.com/repos/langchain-ai/langgraph) · [本地资料](sources/repo_langgraph/text.txt) · JSON Pointer: /license/spdx_id

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_06：CrewAI MCP 支持与版本

**任务：** 用 CrewAI 官方文档确认 MCP 工具集成及列出的 transport，再定位 GitHub 仓库，报告语言和 latest Release 时间。

**快照时间边界：** 2026-09-29T14:39:15.793222Z

[完整 JSON](cases/multi_hop/multi_hop_06.json)

**Ground truth / 必需评分项：**

- `repo_crewai.primary_language` = `"Python"`（证据：e_3）
- `latest_crewai.github_latest_tag` = `"1.15.23"`（证据：e_4）
- `latest_crewai.published_at` = `"2026-09-28T21:14:32Z"`（证据：e_5）
- CrewAI 官方 MCP 文档列出 Stdio、SSE 和 Streamable HTTP transport，将 MCP server 的工具接入 Agent。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [crewai_mcp](https://docs.crewai.com/en/mcp/overview) · [本地资料](sources/crewai_mcp/text.txt) · text.txt:L550-L550; locate nearby section
- `e_2` [crewai_mcp](https://docs.crewai.com/en/mcp/overview) · [本地资料](sources/crewai_mcp/text.txt) · text.txt:L1501-L1501; locate nearby section
- `e_3` [repo_crewai](https://api.github.com/repos/crewAIInc/crewAI) · [本地资料](sources/repo_crewai/text.txt) · JSON Pointer: /language
- `e_4` [latest_crewai](https://api.github.com/repos/crewAIInc/crewAI/releases/latest) · [本地资料](sources/latest_crewai/text.txt) · JSON Pointer: /tag_name
- `e_5` [latest_crewai](https://api.github.com/repos/crewAIInc/crewAI/releases/latest) · [本地资料](sources/latest_crewai/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_07：Pydantic AI MCP 支持与版本

**任务：** 通过 Pydantic AI 官方 MCP 文档和 README 核验 MCP 能力，再确认仓库语言、许可证和 latest Release。

**快照时间边界：** 2026-09-29T14:39:16.671847Z

[完整 JSON](cases/multi_hop/multi_hop_07.json)

**Ground truth / 必需评分项：**

- `repo_pydantic_ai.primary_language` = `"Python"`（证据：e_3）
- `repo_pydantic_ai.license_spdx` = `"MIT"`（证据：e_4）
- `latest_pydantic_ai.github_latest_tag` = `"v2.51.0"`（证据：e_5）
- `latest_pydantic_ai.published_at` = `"2026-09-25T23:19:04Z"`（证据：e_6）
- 官方 MCP 文档与 README 的 MCP capability 示例都支持它具备 MCP 集成这一结论；不要仅依据仓库名称推断。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [pydantic_ai_mcp](https://ai.pydantic.dev/mcp/overview/) · [本地资料](sources/pydantic_ai_mcp/text.txt) · text.txt:L392-L392; locate nearby section
- `e_2` [pydantic_ai_readme](https://raw.githubusercontent.com/pydantic/pydantic-ai/main/README.md) · [本地资料](sources/pydantic_ai_readme/text.txt) · text.txt:L173-L173; locate nearby section
- `e_3` [repo_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai) · [本地资料](sources/repo_pydantic_ai/text.txt) · JSON Pointer: /language
- `e_4` [repo_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai) · [本地资料](sources/repo_pydantic_ai/text.txt) · JSON Pointer: /license/spdx_id
- `e_5` [latest_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai/releases/latest) · [本地资料](sources/latest_pydantic_ai/text.txt) · JSON Pointer: /tag_name
- `e_6` [latest_pydantic_ai](https://api.github.com/repos/pydantic/pydantic-ai/releases/latest) · [本地资料](sources/latest_pydantic_ai/text.txt) · JSON Pointer: /published_at

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_08：Celery 稳定版与消息语义

**任务：** 查看 Celery Release 列表与 latest 端点，排除预发布候选，再根据官方任务文档解释 acks_late 是否保证 exactly-once。

**快照时间边界：** 2026-09-29T14:39:16.567688Z

[完整 JSON](cases/multi_hop/multi_hop_08.json)

**Ground truth / 必需评分项：**

- `releases_celery.first_listed_tag` = `"v5.7.0a1"`（证据：e_1）
- `releases_celery.first_listed_prerelease` = `true`（证据：e_2）
- `latest_celery.github_latest_tag` = `"v5.6.3"`（证据：e_3）
- `latest_celery.published_at` = `"2026-03-26T12:21:23Z"`（证据：e_4）
- acks_late 在任务返回后确认，但不是 exactly-once 保证；任务应幂等，子进程某些终止情形仍会确认消息。（证据：e_5, e_6）

**来源与定位：**

- `e_1` [releases_celery](https://api.github.com/repos/celery/celery/releases?per_page=10) · [本地资料](sources/releases_celery/text.txt) · JSON Pointer: /0/tag_name
- `e_2` [releases_celery](https://api.github.com/repos/celery/celery/releases?per_page=10) · [本地资料](sources/releases_celery/text.txt) · JSON Pointer: /0/prerelease
- `e_3` [latest_celery](https://api.github.com/repos/celery/celery/releases/latest) · [本地资料](sources/latest_celery/text.txt) · JSON Pointer: /tag_name
- `e_4` [latest_celery](https://api.github.com/repos/celery/celery/releases/latest) · [本地资料](sources/latest_celery/text.txt) · JSON Pointer: /published_at
- `e_5` [celery_tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html) · [本地资料](sources/celery_tasks/text.txt) · text.txt:L34-L34; locate nearby section
- `e_6` [celery_tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html) · [本地资料](sources/celery_tasks/text.txt) · text.txt:L54-L54; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_09：pgvector 发布渠道与兼容性

**任务：** 查询 pgvector 是否有 GitHub Release，再查 tags 的首个返回项，并从官方 README 确认支持的 PostgreSQL 最低版本；区分 tag 与 Release。

**快照时间边界：** 2026-09-29T14:39:15.289837Z

[完整 JSON](cases/multi_hop/multi_hop_09.json)

**Ground truth / 必需评分项：**

- `releases_pgvector.github_releases` = `[]`（证据：e_1）
- `pgvector_tags.first_returned_tag` = `"v0.8.6"`（证据：e_2）
- 采集的 README 声明支持 Postgres 13+；空 Release 列表不意味着没有软件版本。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [releases_pgvector](https://api.github.com/repos/pgvector/pgvector/releases?per_page=10) · [本地资料](sources/releases_pgvector/text.txt) · JSON Pointer: / (root)
- `e_2` [pgvector_tags](https://api.github.com/repos/pgvector/pgvector/tags?per_page=10) · [本地资料](sources/pgvector_tags/text.txt) · JSON Pointer: /0/name
- `e_3` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L22-L22; locate nearby section
- `e_4` [pgvector_tags](https://api.github.com/repos/pgvector/pgvector/tags?per_page=10) · [本地资料](sources/pgvector_tags/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## multi_hop_10：FastAPI 仓库迁移后查版本

**任务：** 从旧地址 tiangolo/fastapi 定位当前规范仓库，再查询该仓库 latest Release，并用官方文档说明 BackgroundTasks 可接受哪些函数形式。

**快照时间边界：** 2026-09-29T14:39:16.232056Z

[完整 JSON](cases/multi_hop/multi_hop_10.json)

**Ground truth / 必需评分项：**

- `repo_old_fastapi.canonical_repository` = `"fastapi/fastapi"`（证据：e_1）
- `latest_fastapi.github_latest_tag` = `"0.141.1"`（证据：e_2）
- `latest_fastapi.published_at` = `"2026-07-29T17:17:26Z"`（证据：e_3）
- BackgroundTasks 接受普通 def 与 async def 函数，FastAPI 会处理相应调用。（证据：e_4）

**来源与定位：**

- `e_1` [repo_old_fastapi](https://api.github.com/repos/tiangolo/fastapi) · [本地资料](sources/repo_old_fastapi/text.txt) · JSON Pointer: /full_name
- `e_2` [latest_fastapi](https://api.github.com/repos/fastapi/fastapi/releases/latest) · [本地资料](sources/latest_fastapi/text.txt) · JSON Pointer: /tag_name
- `e_3` [latest_fastapi](https://api.github.com/repos/fastapi/fastapi/releases/latest) · [本地资料](sources/latest_fastapi/text.txt) · JSON Pointer: /published_at
- `e_4` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L348-L349; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

