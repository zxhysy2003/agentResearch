# 异常与边界（10 条）

[返回总览](README.md)

## edge_case_01：归档不等于不存在

**任务：** encode/requests-async 已归档是否意味着项目不存在？报告实际状态及 README 的替代建议。

**快照时间边界：** 2026-09-29T14:35:35.878929Z

[完整 JSON](cases/edge_case/edge_case_01.json)

**Ground truth / 必需评分项：**

- `repo_requests_async.archived` = `true`（证据：e_1）
- `repo_requests_async.full_name` = `"encode/requests-async"`（证据：e_2）
- 归档仓库仍可读取；README 推荐 httpx.AsyncClient()，不能编造该项目仍在活跃维护。（证据：e_3）

**来源与定位：**

- `e_1` [repo_requests_async](https://api.github.com/repos/encode/requests-async) · [本地资料](sources/repo_requests_async/text.txt) · JSON Pointer: /archived
- `e_2` [repo_requests_async](https://api.github.com/repos/encode/requests-async) · [本地资料](sources/repo_requests_async/text.txt) · JSON Pointer: /full_name
- `e_3` [requests_async_readme](https://raw.githubusercontent.com/encode/requests-async/master/README.md) · [本地资料](sources/requests_async_readme/text.txt) · text.txt:L3-L3; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_02：Auto-GPT-Plugins 归档状态

**任务：** 核验 Significant-Gravitas/Auto-GPT-Plugins 的归档状态、默认分支与语言；不能把旧插件仓库的状态推断为整个 AutoGPT 项目的状态。

**快照时间边界：** 2026-09-29T14:35:35.880432Z

[完整 JSON](cases/edge_case/edge_case_02.json)

**Ground truth / 必需评分项：**

- `repo_autogpt_plugins.archived` = `true`（证据：e_1）
- `repo_autogpt_plugins.default_branch` = `"master"`（证据：e_2）
- `repo_autogpt_plugins.language` = `"Python"`（证据：e_3）
- 结论仅适用于 Auto-GPT-Plugins 这个仓库；不得扩展为整个 AutoGPT 项目已停止。（证据：e_4）

**来源与定位：**

- `e_1` [repo_autogpt_plugins](https://api.github.com/repos/Significant-Gravitas/Auto-GPT-Plugins) · [本地资料](sources/repo_autogpt_plugins/text.txt) · JSON Pointer: /archived
- `e_2` [repo_autogpt_plugins](https://api.github.com/repos/Significant-Gravitas/Auto-GPT-Plugins) · [本地资料](sources/repo_autogpt_plugins/text.txt) · JSON Pointer: /default_branch
- `e_3` [repo_autogpt_plugins](https://api.github.com/repos/Significant-Gravitas/Auto-GPT-Plugins) · [本地资料](sources/repo_autogpt_plugins/text.txt) · JSON Pointer: /language
- `e_4` [repo_autogpt_plugins](https://api.github.com/repos/Significant-Gravitas/Auto-GPT-Plugins) · [本地资料](sources/repo_autogpt_plugins/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_03：pgvector 没有 Release 但有 tag

**任务：** pgvector/pgvector 的 GitHub Releases 列表为空时，能否得出没有版本的结论？用 tags 核验。

**快照时间边界：** 2026-09-29T14:39:15.289837Z

[完整 JSON](cases/edge_case/edge_case_03.json)

**Ground truth / 必需评分项：**

- `releases_pgvector.github_releases` = `[]`（证据：e_1）
- `pgvector_tags.first_returned_tag` = `"v0.8.6"`（证据：e_2）
- 不能从空 GitHub Releases 列表推出没有版本；tags 返回了版本标签。不要把 tag 的时间或名称冒充 Release published_at。（证据：e_3）

**来源与定位：**

- `e_1` [releases_pgvector](https://api.github.com/repos/pgvector/pgvector/releases?per_page=10) · [本地资料](sources/releases_pgvector/text.txt) · JSON Pointer: / (root)
- `e_2` [pgvector_tags](https://api.github.com/repos/pgvector/pgvector/tags?per_page=10) · [本地资料](sources/pgvector_tags/text.txt) · JSON Pointer: /0/name
- `e_3` [pgvector_tags](https://api.github.com/repos/pgvector/pgvector/tags?per_page=10) · [本地资料](sources/pgvector_tags/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_04：awesome-python 没有 Release

**任务：** 查询 vinta/awesome-python 最新 GitHub Release；若采集的列表为空，应如何作答？

**快照时间边界：** 2026-09-29T14:35:37.460606Z

[完整 JSON](cases/edge_case/edge_case_04.json)

**Ground truth / 必需评分项：**

- `releases_awesome_python.github_releases` = `[]`（证据：e_1）
- 应明确该采集结果中无 GitHub Release，无法给出其 Release 版本和发布时间；不能编造 v1.0 或声称仓库不存在。（证据：e_2）

**来源与定位：**

- `e_1` [releases_awesome_python](https://api.github.com/repos/vinta/awesome-python/releases?per_page=10) · [本地资料](sources/releases_awesome_python/text.txt) · JSON Pointer: / (root)
- `e_2` [repo_awesome_python](https://api.github.com/repos/vinta/awesome-python) · [本地资料](sources/repo_awesome_python/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_05：FastAPI 旧 owner

**任务：** 访问 tiangolo/fastapi 返回了不同 full_name，应怎样识别项目？

**快照时间边界：** 2026-09-29T14:35:36.255739Z

[完整 JSON](cases/edge_case/edge_case_05.json)

**Ground truth / 必需评分项：**

- `repo_old_fastapi.canonical_repository` = `"fastapi/fastapi"`（证据：e_1）
- 旧地址请求成功且解析到 fastapi/fastapi；应说明规范地址变化，不判为项目不存在。（证据：e_2）

**来源与定位：**

- `e_1` [repo_old_fastapi](https://api.github.com/repos/tiangolo/fastapi) · [本地资料](sources/repo_old_fastapi/text.txt) · JSON Pointer: /full_name
- `e_2` [repo_old_fastapi](https://api.github.com/repos/tiangolo/fastapi) · [本地资料](sources/repo_old_fastapi/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_06：LangChain 旧 owner

**任务：** 用户提供 hwchase17/langchain，查询返回的规范仓库是什么？是否应直接报告找不到项目？

**快照时间边界：** 2026-09-29T14:35:36.284111Z

[完整 JSON](cases/edge_case/edge_case_06.json)

**Ground truth / 必需评分项：**

- `repo_old_langchain.canonical_repository` = `"langchain-ai/langchain"`（证据：e_1）
- 应识别为 langchain-ai/langchain，旧 owner 路径的成功解析不等于不存在。（证据：e_2）

**来源与定位：**

- `e_1` [repo_old_langchain](https://api.github.com/repos/hwchase17/langchain) · [本地资料](sources/repo_old_langchain/text.txt) · JSON Pointer: /full_name
- `e_2` [repo_old_langchain](https://api.github.com/repos/hwchase17/langchain) · [本地资料](sources/repo_old_langchain/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_07：LangGraph 组件与 prerelease 标志

**任务：** LangGraph 采集的 Release 列表首项能否直接当成 Python langgraph 核心包最新稳定版本？检查标签名及 prerelease 字段。

**快照时间边界：** 2026-09-29T14:35:36.376406Z

[完整 JSON](cases/edge_case/edge_case_07.json)

**Ground truth / 必需评分项：**

- `releases_langgraph.first_listed_tag` = `"cli==0.4.32.dev0"`（证据：e_1）
- `releases_langgraph.github_prerelease_flag` = `false`（证据：e_2）
- 首项 cli==0.4.32.dev0 指向 CLI 且标签包含 dev0；即使 GitHub prerelease 字段为 false，也不能把它当作核心 langgraph 包稳定版。（证据：e_3）

**来源与定位：**

- `e_1` [releases_langgraph](https://api.github.com/repos/langchain-ai/langgraph/releases?per_page=10) · [本地资料](sources/releases_langgraph/text.txt) · JSON Pointer: /0/tag_name
- `e_2` [releases_langgraph](https://api.github.com/repos/langchain-ai/langgraph/releases?per_page=10) · [本地资料](sources/releases_langgraph/text.txt) · JSON Pointer: /0/prerelease
- `e_3` [releases_langgraph](https://api.github.com/repos/langchain-ai/langgraph/releases?per_page=10) · [本地资料](sources/releases_langgraph/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_08：Celery 预发布混入列表

**任务：** Celery Release 列表首项与 latest 端点不一致时，查询稳定版应该报告什么并解释差别？

**快照时间边界：** 2026-09-29T14:39:16.567688Z

[完整 JSON](cases/edge_case/edge_case_08.json)

**Ground truth / 必需评分项：**

- `releases_celery.first_listed_tag` = `"v5.7.0a1"`（证据：e_1）
- `releases_celery.first_listed_prerelease` = `true`（证据：e_2）
- `latest_celery.github_latest_tag` = `"v5.6.3"`（证据：e_3）
- `latest_celery.published_at` = `"2026-03-26T12:21:23Z"`（证据：e_4）
- 列表首项 v5.7.0a1 为预发布，而 latest 端点返回 v5.6.3；不应只取列表第一项。（证据：e_5, e_6）

**来源与定位：**

- `e_1` [releases_celery](https://api.github.com/repos/celery/celery/releases?per_page=10) · [本地资料](sources/releases_celery/text.txt) · JSON Pointer: /0/tag_name
- `e_2` [releases_celery](https://api.github.com/repos/celery/celery/releases?per_page=10) · [本地资料](sources/releases_celery/text.txt) · JSON Pointer: /0/prerelease
- `e_3` [latest_celery](https://api.github.com/repos/celery/celery/releases/latest) · [本地资料](sources/latest_celery/text.txt) · JSON Pointer: /tag_name
- `e_4` [latest_celery](https://api.github.com/repos/celery/celery/releases/latest) · [本地资料](sources/latest_celery/text.txt) · JSON Pointer: /published_at
- `e_5` [releases_celery](https://api.github.com/repos/celery/celery/releases?per_page=10) · [本地资料](sources/releases_celery/text.txt) · text.txt:L1-L1; locate nearby section
- `e_6` [latest_celery](https://api.github.com/repos/celery/celery/releases/latest) · [本地资料](sources/latest_celery/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_09：NOASSERTION 不等于无许可证

**任务：** GitHub 对 pgvector 返回 license.spdx_id=NOASSERTION，是否可以断言项目没有许可证？核对实际 LICENSE 文件。

**快照时间边界：** 2026-09-29T14:39:15.288870Z

[完整 JSON](cases/edge_case/edge_case_09.json)

**Ground truth / 必需评分项：**

- `repo_pgvector.github_license_spdx` = `"NOASSERTION"`（证据：e_1）
- NOASSERTION 表示该 API 字段未给出确定 SPDX 标识，不等于没有许可证；实际 LICENSE 存在并包含使用、复制、修改和分发的许可文字。不要擅自将 API 值改成 MIT。（证据：e_2）

**来源与定位：**

- `e_1` [repo_pgvector](https://api.github.com/repos/pgvector/pgvector) · [本地资料](sources/repo_pgvector/text.txt) · JSON Pointer: /license/spdx_id
- `e_2` [pgvector_license](https://raw.githubusercontent.com/pgvector/pgvector/master/LICENSE) · [本地资料](sources/pgvector_license/text.txt) · text.txt:L5-L5; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## edge_case_10：Python 3.12 误用 3.13 API

**任务：** 开发者使用 Python 3.12，却找到 asyncio.Queue.shutdown 文档。对比 3.12 和 3.13 文档，判断能否直接采用。

**快照时间边界：** 2026-09-29T14:39:15.288137Z

[完整 JSON](cases/edge_case/edge_case_10.json)

**Ground truth / 必需评分项：**

- Queue.shutdown 在 3.13 文档标记为 3.13 新增，3.12 的 Queue API 页面没有该方法；不能将新版 API 直接声称为 3.12 可用。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [python_queue_313](https://docs.python.org/3.13/library/asyncio-queue.html) · [本地资料](sources/python_queue_313/text.txt) · text.txt:L255-L255; locate nearby section
- `e_2` [python_queue](https://docs.python.org/3.12/library/asyncio-queue.html) · [本地资料](sources/python_queue/text.txt) · text.txt:L1-L1; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

