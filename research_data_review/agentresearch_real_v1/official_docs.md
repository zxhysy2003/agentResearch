# 官方文档检索（10 条）

[返回总览](README.md)

## official_docs_01：asyncio.gather 异常

**任务：** Python 3.12 的 asyncio.gather 默认遇到子任务异常时会怎样？return_exceptions=True 有何变化？

**快照时间边界：** 2026-09-29T14:35:30.359917Z

[完整 JSON](cases/official_docs/official_docs_01.json)

**Ground truth / 必需评分项：**

- 默认立即向等待 gather 的任务传播首个异常；其他 awaitable 不会因此自动取消，而会继续运行。（证据：e_1）
- return_exceptions=True 时，异常与成功结果一起进入结果列表。（证据：e_2）

**来源与定位：**

- `e_1` [python_asyncio](https://docs.python.org/3.12/library/asyncio-task.html) · [本地资料](sources/python_asyncio/text.txt) · text.txt:L1141-L1141; locate nearby section
- `e_2` [python_asyncio](https://docs.python.org/3.12/library/asyncio-task.html) · [本地资料](sources/python_asyncio/text.txt) · text.txt:L1150-L1151; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_02：FastAPI BackgroundTasks

**任务：** FastAPI BackgroundTasks 在什么时候执行？任务函数能否使用 async def？何时应考虑 Celery？

**快照时间边界：** 2026-09-29T14:35:30.361903Z

[完整 JSON](cases/official_docs/official_docs_02.json)

**Ground truth / 必需评分项：**

- 任务在返回响应之后运行，任务函数支持普通 def 和 async def。（证据：e_1, e_2）
- 小型、需共享进程对象的后台工作可使用 BackgroundTasks；跨进程或跨服务器的重型计算可考虑 Celery 等队列工具。（证据：e_3, e_4）

**来源与定位：**

- `e_1` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L231-L232; locate nearby section
- `e_2` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L348-L349; locate nearby section
- `e_3` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L889-L889; locate nearby section
- `e_4` [fastapi_background](https://fastapi.tiangolo.com/tutorial/background-tasks/) · [本地资料](sources/fastapi_background/text.txt) · text.txt:L892-L892; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_03：Qdrant 距离度量

**任务：** Qdrant collection 文档列出哪些常用稠密向量距离度量？Cosine 上传时有什么处理？

**快照时间边界：** 2026-09-29T14:35:31.503138Z

[完整 JSON](cases/official_docs/official_docs_03.json)

**Ground truth / 必需评分项：**

- 度量包括 Dot、Cosine、Euclid、Manhattan；Cosine 通过归一化向量的点积实现，上传时自动归一化。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [qdrant_collections](https://qdrant.tech/documentation/concepts/collections/) · [本地资料](sources/qdrant_collections/text.txt) · text.txt:L248-L248; locate nearby section
- `e_2` [qdrant_collections](https://qdrant.tech/documentation/concepts/collections/) · [本地资料](sources/qdrant_collections/text.txt) · text.txt:L252-L252; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_04：Pydantic 正整数列表

**任务：** 如何使用 Pydantic 的 Annotated 与 Field，使列表的每个整数元素都大于 0？

**快照时间边界：** 2026-09-29T14:35:31.263022Z

[完整 JSON](cases/official_docs/official_docs_04.json)

**Ground truth / 必需评分项：**

- 使用 list[Annotated[int, Field(gt=0)]]，约束施加于元素；[1,3] 有效，包含负数或 0 的元素不满足 gt=0。（证据：e_1）

**来源与定位：**

- `e_1` [pydantic_fields](https://docs.pydantic.dev/latest/concepts/fields/) · [本地资料](sources/pydantic_fields/text.txt) · text.txt:L291-L291; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_05：Compose 就绪条件

**任务：** Docker Compose depends_on 是否默认等待数据库就绪？如何等待健康检查或一次性任务完成？

**快照时间边界：** 2026-09-29T14:35:31.383306Z

[完整 JSON](cases/official_docs/official_docs_05.json)

**Ground truth / 必需评分项：**

- 默认只保证依赖容器已运行，不保证服务就绪；service_healthy 配合 healthcheck 等待健康，service_completed_successfully 等待成功完成。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [docker_depends](https://docs.docker.com/compose/how-tos/startup-order/) · [本地资料](sources/docker_depends/text.txt) · text.txt:L999-L999; locate nearby section
- `e_2` [docker_depends](https://docs.docker.com/compose/how-tos/startup-order/) · [本地资料](sources/docker_depends/text.txt) · text.txt:L1008-L1008; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_06：pgvector 距离算子

**任务：** 列出 pgvector 的 L2、内积、余弦、L1、Hamming、Jaccard 距离算子，并说明内积算子的符号。

**快照时间边界：** 2026-09-29T14:35:32.158204Z

[完整 JSON](cases/official_docs/official_docs_06.json)

**Ground truth / 必需评分项：**

- 依次是 <->、<#>、<=>、<+>、<~>、<%>；<#> 返回负内积以适配 ASC 索引扫描；Hamming 与 Jaccard 针对二进制向量。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L138-L138; locate nearby section
- `e_2` [pgvector_readme](https://raw.githubusercontent.com/pgvector/pgvector/master/README.md) · [本地资料](sources/pgvector_readme/text.txt) · text.txt:L81-L81; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_07：HTTPX 异步客户端生命周期

**任务：** 在异步请求循环中如何复用和关闭 HTTPX AsyncClient？为什么不推荐在热循环里反复创建客户端？

**快照时间边界：** 2026-09-29T14:35:32.857896Z

[完整 JSON](cases/official_docs/official_docs_07.json)

**Ground truth / 必需评分项：**

- 使用有作用域或共享的 AsyncClient 复用连接池，避免热循环中多次实例化；用 async with 或 await client.aclose() 关闭。（证据：e_1, e_2）

**来源与定位：**

- `e_1` [httpx_async](https://www.python-httpx.org/async/) · [本地资料](sources/httpx_async/text.txt) · text.txt:L146-L146; locate nearby section
- `e_2` [httpx_async](https://www.python-httpx.org/async/) · [本地资料](sources/httpx_async/text.txt) · text.txt:L148-L148; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_08：Redis 持久化

**任务：** 解释 Redis RDB 与 AOF 的基本机制、能否同时启用，以及默认 every-second fsync 策略的数据丢失窗口。

**快照时间边界：** 2026-09-29T14:35:32.226015Z

[完整 JSON](cases/official_docs/official_docs_08.json)

**Ground truth / 必需评分项：**

- RDB 是按时间点保存的数据集快照；AOF 记录写操作并可重放；两者可同时启用。（证据：e_1, e_2）
- 文档对默认每秒 fsync 的说明是可能丢失约一秒写入，不能声称绝对零丢失。（证据：e_3）

**来源与定位：**

- `e_1` [redis_persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) · [本地资料](sources/redis_persistence/text.txt) · text.txt:L161-L161; locate nearby section
- `e_2` [redis_persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) · [本地资料](sources/redis_persistence/text.txt) · text.txt:L166-L166; locate nearby section
- `e_3` [redis_persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) · [本地资料](sources/redis_persistence/text.txt) · text.txt:L186-L186; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_09：PostgreSQL 索引类型

**任务：** PostgreSQL 17 的默认索引是什么？GIN 与 BRIN 分别适用于什么数据特点？

**快照时间边界：** 2026-09-29T14:35:32.658607Z

[完整 JSON](cases/official_docs/official_docs_09.json)

**Ground truth / 必需评分项：**

- CREATE INDEX 默认 B-tree；GIN 是倒排索引，适合包含多个组件值的数据；BRIN 保存物理块范围摘要，适合值与物理存储顺序相关的数据。（证据：e_1, e_2, e_3）

**来源与定位：**

- `e_1` [postgres_indexes](https://www.postgresql.org/docs/17/indexes-types.html) · [本地资料](sources/postgres_indexes/text.txt) · text.txt:L90-L90; locate nearby section
- `e_2` [postgres_indexes](https://www.postgresql.org/docs/17/indexes-types.html) · [本地资料](sources/postgres_indexes/text.txt) · text.txt:L198-L198; locate nearby section
- `e_3` [postgres_indexes](https://www.postgresql.org/docs/17/indexes-types.html) · [本地资料](sources/postgres_indexes/text.txt) · text.txt:L216-L216; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

## official_docs_10：SQLite WAL 限制

**任务：** SQLite WAL 的读写并发优势是什么？是否适合多个主机通过网络文件系统共享同一数据库？

**快照时间边界：** 2026-09-29T14:35:32.823567Z

[完整 JSON](cases/official_docs/official_docs_10.json)

**Ground truth / 必需评分项：**

- WAL 允许读写并行，读者不阻塞写者、写者不阻塞读者；但仍只有一个写者。（证据：e_1, e_2）
- 使用数据库的进程必须在同一主机；WAL 不适用于这种跨主机网络文件系统共享。（证据：e_3）

**来源与定位：**

- `e_1` [sqlite_wal](https://www.sqlite.org/wal.html) · [本地资料](sources/sqlite_wal/text.txt) · text.txt:L55-L55; locate nearby section
- `e_2` [sqlite_wal](https://www.sqlite.org/wal.html) · [本地资料](sources/sqlite_wal/text.txt) · text.txt:L206-L206; locate nearby section
- `e_3` [sqlite_wal](https://www.sqlite.org/wal.html) · [本地资料](sources/sqlite_wal/text.txt) · text.txt:L62-L62; locate nearby section

**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理

