# 多来源技术比较（10 条）

[返回总览](README.md)

## comparison_01：Requests vs HTTPX 异步请求

**任务：** 为异步 Agent 批量调用 HTTP API，比较 Requests 与 HTTPX 的非阻塞支持、连接复用和流式读取。给出有条件的选择。

**快照时间边界：** 2026-09-29T14:35:32.987545Z

[完整 JSON](cases/comparison/comparison_01.json)

**Ground truth / 必需评分项：**

- Requests 默认 transport 不提供非阻塞 I/O，stream=True 也不使读取变成非阻塞；HTTPX 提供 AsyncClient 与异步流式迭代。（证据：e_1, e_2）
- Requests Session 可复用连接；HTTPX 应复用 AsyncClient 并管理关闭。纯 async 调用场景可优先 HTTPX；不要据此断言 Requests 在所有场景都不适用。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [requests_advanced](https://requests.readthedocs.io/en/latest/user/advanced/) · [本地资料](sources/requests_advanced/text.txt) · text.txt:L2250-L2251; locate nearby section
- `e_2` [httpx_async](https://www.python-httpx.org/async/) · [本地资料](sources/httpx_async/text.txt) · text.txt:L164-L164; locate nearby section
- `e_3` [requests_advanced](https://requests.readthedocs.io/en/latest/user/advanced/) · [本地资料](sources/requests_advanced/text.txt) · text.txt:L170-L170; locate nearby section
- `e_4` [httpx_async](https://www.python-httpx.org/async/) · [本地资料](sources/httpx_async/text.txt) · text.txt:L146-L146; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_02：BackgroundTasks vs Celery

**任务：** 比较 FastAPI BackgroundTasks 与 Celery，场景分别是轻量通知与跨服务器后台任务；说明部署和消息确认的限制。

**快照时间边界：** 2026-09-29T14:35:33.814837Z

[完整 JSON](cases/comparison/comparison_02.json)

**Ground truth / 必需评分项：**

- BackgroundTasks 适合轻量、同应用对象访问；Celery 需要消息队列等配置并支持跨进程或服务器工作。（证据：e_1, e_2）
- 不能将 Celery 描述为天然 exactly-once；文档强调幂等任务，acks_late 与重试有不同语义。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L887-L887; locate nearby section
- `e_2` [celery_tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html) · [本地资料](sources/celery_tasks/text.txt) · text.txt:L24-L24; locate nearby section
- `e_3` [celery_tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html) · [本地资料](sources/celery_tasks/text.txt) · text.txt:L34-L34; locate nearby section
- `e_4` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L889-L889; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_03：FastAPI vs Flask 后台工作

**任务：** 比较 FastAPI BackgroundTasks 与默认 WSGI 部署的 Flask async view：响应之后的工作应如何安排？

**快照时间边界：** 2026-09-29T14:35:33.567348Z

[完整 JSON](cases/comparison/comparison_03.json)

**Ground truth / 必需评分项：**

- FastAPI 有响应后执行的 BackgroundTasks；Flask 默认 async view 完成后，其事件循环中的未完成任务会取消，不应直接用 create_task 充当持久后台队列。（证据：e_1, e_2）
- 限定 Flask 的默认 WSGI 场景；文档另有 ASGI 加 WsgiToAsgi 的例外，不能声称 Flask 永远无法运行长期异步任务。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L231-L232; locate nearby section
- `e_2` [flask_async](https://flask.palletsprojects.com/en/stable/async-await/) · [本地资料](sources/flask_async/text.txt) · text.txt:L90-L90; locate nearby section
- `e_3` [flask_async](https://flask.palletsprojects.com/en/stable/async-await/) · [本地资料](sources/flask_async/text.txt) · text.txt:L97-L97; locate nearby section
- `e_4` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L887-L887; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_04：Qdrant vs pgvector 向量检索

**任务：** 比较 Qdrant 和 pgvector 的距离度量、部署形态与过滤表达；不要给出无实测支持的性能排名。

**快照时间边界：** 2026-09-29T14:35:32.158204Z

[完整 JSON](cases/comparison/comparison_04.json)

**Ground truth / 必需评分项：**

- Qdrant 文档列出 Dot/Cosine/Euclid/Manhattan；pgvector 还列出针对二进制向量的 Hamming/Jaccard，须区分向量类型。（证据：e_1, e_2）
- pgvector 是 Postgres 扩展并使用 SQL WHERE；Qdrant 以 collection/payload 条件表达过滤。（证据：e_3, e_4, e_5）

**来源与定位：**

- `e_1` [qdrant_collections](https://qdrant.tech/documentation/concepts/collections/) · [本地资料](sources/qdrant_collections/text.txt) · text.txt:L248-L248; locate nearby section
- `e_2` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L9-L9; locate nearby section
- `e_3` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L58-L58; locate nearby section
- `e_4` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L55-L55; locate nearby section
- `e_5` [qdrant_filtering](https://qdrant.tech/documentation/concepts/filtering/) · [本地资料](sources/qdrant_filtering/text.txt) · text.txt:L231-L231; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_05：Docker volume vs bind mount

**任务：** 为容器数据库持久化和开发源码共享分别比较 Docker volume 与 bind mount 的管理方式、可移植性及主机写入影响。

**快照时间边界：** 2026-09-29T14:35:31.440616Z

[完整 JSON](cases/comparison/comparison_05.json)

**Ground truth / 必需评分项：**

- volume 由 Docker 管理，适合容器产生的数据持久化；bind mount 直接映射主机路径，依赖主机目录布局。（证据：e_1, e_2）
- bind mount 默认可写主机文件，可用 readonly/ro 限制；不能把删除容器等同于自动删除持久 volume。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [docker_volumes](https://docs.docker.com/engine/storage/volumes/) · [本地资料](sources/docker_volumes/text.txt) · text.txt:L1009-L1010; locate nearby section
- `e_2` [docker_bind](https://docs.docker.com/engine/storage/bind-mounts/) · [本地资料](sources/docker_bind/text.txt) · text.txt:L994-L994; locate nearby section
- `e_3` [docker_bind](https://docs.docker.com/engine/storage/bind-mounts/) · [本地资料](sources/docker_bind/text.txt) · text.txt:L1027-L1027; locate nearby section
- `e_4` [docker_volumes](https://docs.docker.com/engine/storage/volumes/) · [本地资料](sources/docker_volumes/text.txt) · text.txt:L1094-L1094; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_06：asyncio.gather vs futures.as_completed

**任务：** 比较 Python 3.12 asyncio.gather 与 concurrent.futures.as_completed 的输入模型、结果顺序及异常获取方式。

**快照时间边界：** 2026-09-29T14:35:30.360506Z

[完整 JSON](cases/comparison/comparison_06.json)

**Ground truth / 必需评分项：**

- gather 并发等待 awaitables，成功结果按输入顺序排列；as_completed 迭代完成的 Future，应逐个调用 result() 取值或接收异常。（证据：e_1, e_2）
- asyncio 协程并发与 Executor 的线程/进程执行不是同一种执行模型；不把 gather 说成自动创建线程池。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [python_asyncio](https://docs.python.org/3.12/library/asyncio-task.html) · [本地资料](sources/python_asyncio/text.txt) · text.txt:L1130-L1130; locate nearby section
- `e_2` [python_futures](https://docs.python.org/3.12/library/concurrent.futures.html) · [本地资料](sources/python_futures/text.txt) · text.txt:L1319-L1319; locate nearby section
- `e_3` [python_asyncio](https://docs.python.org/3.12/library/asyncio-task.html) · [本地资料](sources/python_asyncio/text.txt) · text.txt:L1126-L1127; locate nearby section
- `e_4` [python_futures](https://docs.python.org/3.12/library/concurrent.futures.html) · [本地资料](sources/python_futures/text.txt) · text.txt:L344-L345; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_07：LangGraph vs CrewAI 编排

**任务：** 根据两项目官方 README，比较 LangGraph 与 CrewAI 的编排抽象、状态恢复和协作方式，为需人工介入的状态流程说明选择依据。

**快照时间边界：** 2026-09-29T14:35:34.768256Z

[完整 JSON](cases/comparison/comparison_07.json)

**Ground truth / 必需评分项：**

- LangGraph 明确强调 stateful workflow、durable execution 和 human-in-the-loop；CrewAI 用 Crews 表达角色协作，用 Flows 表达事件驱动控制。（证据：e_1, e_2）
- 建议应与控制、状态及协作需求关联；不能因某 README 未展开某功能就断言另一项目不支持该功能。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [langgraph_readme](https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md) · [本地资料](sources/langgraph_readme/text.txt) · text.txt:L40-L40; locate nearby section
- `e_2` [crewai_readme](https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md) · [本地资料](sources/crewai_readme/text.txt) · text.txt:L62-L62; locate nearby section
- `e_3` [langgraph_readme](https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md) · [本地资料](sources/langgraph_readme/text.txt) · text.txt:L12-L12; locate nearby section
- `e_4` [crewai_readme](https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md) · [本地资料](sources/crewai_readme/text.txt) · text.txt:L59-L59; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_08：Pydantic 默认转换 vs strict

**任务：** 对接收外部 JSON 的 Agent 配置，比较 Pydantic 默认模式、调用级 strict=True 和字段级 strict 的作用范围。

**快照时间边界：** 2026-09-29T14:35:31.347816Z

[完整 JSON](cases/comparison/comparison_08.json)

**Ground truth / 必需评分项：**

- 默认可以把字符串 123 转为整数；严格模式会拒绝示例中的字符串整数；strict 可在校验调用或字段配置启用。（证据：e_1, e_2）
- strict 并非所有类型和输入通道完全一致；JSON 输入对某些日期时间类型更宽松，需按类型与输入方式解释。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [pydantic_strict](https://docs.pydantic.dev/latest/concepts/strict_mode/) · [本地资料](sources/pydantic_strict/text.txt) · text.txt:L172-L172; locate nearby section
- `e_2` [pydantic_fields](https://docs.pydantic.dev/latest/concepts/fields/) · [本地资料](sources/pydantic_fields/text.txt) · text.txt:L244-L244; locate nearby section
- `e_3` [pydantic_strict](https://docs.pydantic.dev/latest/concepts/strict_mode/) · [本地资料](sources/pydantic_strict/text.txt) · text.txt:L185-L185; locate nearby section
- `e_4` [pydantic_fields](https://docs.pydantic.dev/latest/concepts/fields/) · [本地资料](sources/pydantic_fields/text.txt) · text.txt:L733-L733; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_09：SQLite WAL vs Redis 持久化

**任务：** 比较 SQLite WAL 与 Redis RDB/AOF，用于单机 Agent 状态保存时分别说明并发、持久化机制及故障限制。

**快照时间边界：** 2026-09-29T14:35:32.823567Z

[完整 JSON](cases/comparison/comparison_09.json)

**Ground truth / 必需评分项：**

- SQLite WAL 在单机共享内存约束下支持读写并行但只允许一个写者；Redis RDB 是快照，AOF 是写操作日志，不能把二者机制混为一谈。（证据：e_1, e_2）
- 应说明 SQLite WAL 不支持跨主机网络文件系统方案，以及 Redis every-second fsync 的约一秒丢失窗口；不作没有数据支撑的吞吐比较。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [sqlite_wal](https://www.sqlite.org/wal.html) · [本地资料](sources/sqlite_wal/text.txt) · text.txt:L206-L206; locate nearby section
- `e_2` [redis_persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) · [本地资料](sources/redis_persistence/text.txt) · text.txt:L161-L161; locate nearby section
- `e_3` [sqlite_wal](https://www.sqlite.org/wal.html) · [本地资料](sources/sqlite_wal/text.txt) · text.txt:L62-L62; locate nearby section
- `e_4` [redis_persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) · [本地资料](sources/redis_persistence/text.txt) · text.txt:L186-L186; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## comparison_10：HTTP 流式响应 vs WebSocket

**任务：** 在 FastAPI 中比较 StreamingResponse 和 WebSocket：持续输出 Agent token 与同一连接上的双向交互分别如何实现？

**快照时间边界：** 2026-09-29T14:35:30.361537Z

[完整 JSON](cases/comparison/comparison_10.json)

**Ground truth / 必需评分项：**

- StreamingResponse 消费普通或异步生成器并流式返回 HTTP 响应体；WebSocket 示例在连接内接收文本并发送文本，适合双向交互。（证据：e_1, e_2）
- WebSocket 示例先接受连接，再循环接收和发送文本；StreamingResponse 则通过迭代生成器发送响应体，二者的接口使用方式不同。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [fastapi_streaming](https://fastapi.tiangolo.com/advanced/custom-response/) · [本地资料](sources/fastapi_streaming/text.txt) · text.txt:L944-L944; locate nearby section
- `e_2` [fastapi_websockets](https://fastapi.tiangolo.com/advanced/websockets/) · [本地资料](sources/fastapi_websockets/text.txt) · text.txt:L362-L362; locate nearby section
- `e_3` [fastapi_streaming](https://fastapi.tiangolo.com/advanced/custom-response/) · [本地资料](sources/fastapi_streaming/text.txt) · text.txt:L946-L946; locate nearby section
- `e_4` [fastapi_websockets](https://fastapi.tiangolo.com/advanced/websockets/) · [本地资料](sources/fastapi_websockets/text.txt) · text.txt:L352-L352; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

