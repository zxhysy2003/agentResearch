"""Build review candidates exclusively from downloaded evidence; never fetches the web."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'src'))
from benchmark.models import BenchmarkCase

SNAPSHOT = 'agentresearch-real-review-v1'
CATEGORIES = ['github_lookup', 'official_docs', 'comparison', 'multi_hop', 'edge_case']
LABELS = ['GitHub 信息检索', '官方文档检索', '多来源技术比较', '多跳 Research', '异常与边界']
CASES = []
PROOFS = []

def read(key):
    return (ROOT / 'sources' / key / 'text.txt').read_text()

def data(key):
    return json.loads((ROOT / 'sources' / key / 'body').read_text())

def meta(key):
    return json.loads((ROOT / 'sources' / key / 'metadata.json').read_text())

def pointer(key, path):
    value = data(key)
    for part in path.strip('/').split('/') if path else []:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

class Case:
    def __init__(self, category, title, prompt):
        n = sum(c['category'] == category for c in CASES) + 1
        self.id = f'{category}_{n:02d}'
        self.category, self.title, self.prompt = category, title, prompt
        self.facts, self.rubrics, self.evidence, self.checks, self.proofs = [], [], [], [], []

    def evidence_for(self, key, locator):
        m = meta(key)
        assert m['status'] == 200, (key, m['status'])
        eid = f'e_{len(self.evidence)+1}'
        self.evidence.append(dict(id=eid,source_type='github_api' if 'api.github.com' in m['requested_url'] else ('repository' if 'raw.githubusercontent.com' in m['requested_url'] else 'official_docs'),url=m['requested_url'],artifact_id=key,locator=locator,captured_at=m['retrieved_at']))
        return eid

    def fact(self, key, path, predicate, subject=None):
        value = pointer(key, path)
        assert value is not None, (key, path)
        kind = 'boolean' if type(value) is bool else 'number' if type(value) in (int,float) else 'set' if isinstance(value,list) else 'datetime' if predicate.endswith('_at') else 'string'
        fid = f'f_{len(self.facts)+1}'
        eid = self.evidence_for(key, 'JSON Pointer: ' + (path or '/ (root)'))
        self.facts.append(dict(id=fid,subject=subject or key,predicate=predicate,expected=dict(type=kind,value=value),evidence_ids=[eid]))
        self.checks.append(dict(id=f'c_{fid}',dimension='correctness',evaluator='fact_match',target=[fid],weight=1,required=True))
        self.proofs.append(dict(kind='json_pointer',source=key,pointer=path,value=value))
        return value

    def claim(self, statement, *supports):
        eids=[]
        for key, anchor in supports:
            text=read(key)
            match=re.search(r'\s+'.join(re.escape(part) for part in anchor.split()), text, re.IGNORECASE)
            assert match is not None, (self.id, key, anchor)
            idx=match.start()
            anchor=match.group()
            line=text[:idx].count('\n')+1
            end=line+anchor.count('\n')
            eids.append(self.evidence_for(key,f'text.txt:L{line}-L{end}; locate nearby section'))
            self.proofs.append(dict(kind='text_anchor',source=key,anchor=anchor,line=line))
        rid=f'r_{len(self.rubrics)+1}'
        self.rubrics.append(dict(id=rid,criterion=statement,evidence_ids=eids,anchors={'0':'未回答或与原始证据矛盾。','0.5':'部分正确，但遗漏该评分项中的条件或限制。','1':'完整且正确地表述该评分项，保留适用范围与限制。'}))
        self.checks.append(dict(id=f'c_{rid}',dimension='correctness',evaluator='rubric_judge',target=[rid],weight=1,required=True))

    def release(self,key):
        self.fact('latest_'+key,'/tag_name','github_latest_tag')
        self.fact('latest_'+key,'/published_at','published_at')

    def save(self):
        targets=[f['id'] for f in self.facts]+[r['id'] for r in self.rubrics]
        self.checks.extend([
            dict(id='c_citations',dimension='evidence',evaluator='citation_support',target=targets,weight=1,required=True),
            dict(id='c_trace',dimension='process',evaluator='trace_assertion',target=targets,assertion='supporting_source_observed',weight=1,required=True),
        ])
        weights=dict(correctness=.7,evidence=.2,process=.1)
        if self.category in ('comparison','multi_hop'): weights=dict(correctness=.6,evidence=.25,process=.15)
        if self.category=='edge_case': weights=dict(correctness=.5,evidence=.2,process=.3)
        obj=dict(schema_version='1.0',id=self.id,revision=1,category=self.category,difficulty='hard' if self.category in ('comparison','multi_hop','edge_case') else 'medium',tags=['real_sources','review_candidate'],split='dev',task=dict(prompt=self.prompt,as_of=max(e['captured_at'] for e in self.evidence),context={'time_scope':'仅依据此任务的采集快照回答；当前、最新及统计值均指各来源记录的采集时刻，不代表未来实时状态。'},requirements=['引用可核验的一手来源。','区分材料直接记载、推断和不确定性；不编造。']),environment=dict(mode='snapshot',snapshot_id=SNAPSHOT,allowed_tools=['web_search','fetch_page','github_read'],limits=dict(max_tool_calls=30,timeout_seconds=180),fault_scenario_id=None),ground_truth=dict(expected_outcome='answered',facts=self.facts,evidence=self.evidence,rubrics=self.rubrics,entity_requirements=None),evaluation_rule=dict(checks=self.checks,dimension_weights=weights,pass_threshold=.8))
        obj=BenchmarkCase.model_validate(obj).model_dump(mode='json')
        path=ROOT/'cases'/self.category/f'{self.id}.json';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
        CASES.append(obj)
        PROOFS.append(dict(case_id=self.id,title=self.title,review_status='pending_human_review',checks=self.proofs))

# 1. GitHub information retrieval: heterogeneous questions, not ten copies of one prompt.
c=Case('github_lookup','FastAPI stars','采集时 fastapi/fastapi 的 GitHub stars 数是多少？说明统计时刻。');c.fact('repo_fastapi','/stargazers_count','stargazers_count');c.save()
c=Case('github_lookup','Qdrant 主语言','GitHub 将 qdrant/qdrant 的主要编程语言识别为什么？');c.fact('repo_qdrant','/language','primary_language');c.save()
c=Case('github_lookup','HTTPX 许可证标识','GitHub API 为 encode/httpx 返回的 SPDX 许可证标识是什么？');c.fact('repo_httpx','/license/spdx_id','license_spdx');c.save()
c=Case('github_lookup','Browser Use 最新 Release','查询 browser-use/browser-use 的 GitHub latest Release 标签和发布时间。');c.release('browser');c.save()
c=Case('github_lookup','Pydantic 最新 Release','查询 pydantic/pydantic 的 GitHub latest Release 标签和发布时间，不把 prerelease 当成稳定版。');c.release('pydantic');c.save()
c=Case('github_lookup','Qdrant Release 发布时间','查询 qdrant/qdrant 的 GitHub latest Release 标签及 UTC 发布时间。');c.release('qdrant');c.save()
c=Case('github_lookup','HTTPX 已关闭 bug','从采集的 encode/httpx 已关闭 bug 查询结果中，找出标题涉及 PoolTimeout 与 asyncio.gather 的 issue，报告编号、标题和关闭时间。')
issue_index=next(i for i,d in enumerate(data('issues_httpx')) if d.get('number')==1171 and 'pull_request' not in d)
for field in ['number','title','closed_at']: c.fact('issues_httpx',f'/{issue_index}/{field}',field)
c.save()
c=Case('github_lookup','Browser Use Python 安装说明','browser-use README 的 Python Library 安装段落声明的最低 Python 版本是什么？新建项目的 uv 示例又选择哪个版本？')
c.claim('最低版本为 Python 3.11；新建项目示例使用 Python 3.12。这是最低要求与示例选择的区别。',('browser_readme','Python >= 3.11'),('browser_readme','uv init --python 3.12'));c.save()
c=Case('github_lookup','LangGraph README 能力','LangGraph README 是否说明 durable execution 和 human-in-the-loop？分别概括其用途。')
c.claim('Durable execution 面向故障后恢复与长时间运行；human-in-the-loop 支持执行过程中检查和修改 Agent 状态。',('langgraph_readme','Durable execution'),('langgraph_readme','Human-in-the-loop'));c.save()
c=Case('github_lookup','CrewAI 仓库身份','CrewAI 官方仓库的完整名称、默认分支和 GitHub 许可证标识是什么？')
for field in ['full_name','default_branch']:c.fact('repo_crewai','/'+field,field)
c.fact('repo_crewai','/license/spdx_id','license_spdx');c.save()

# 2. Official documentation.
c=Case('official_docs','asyncio.gather 异常','Python 3.12 的 asyncio.gather 默认遇到子任务异常时会怎样？return_exceptions=True 有何变化？')
c.claim('默认立即向等待 gather 的任务传播首个异常；其他 awaitable 不会因此自动取消，而会继续运行。',('python_asyncio','Other awaitables'))
c.claim('return_exceptions=True 时，异常与成功结果一起进入结果列表。',('python_asyncio','exceptions are treated the same as successful'))
c.save()
c=Case('official_docs','FastAPI BackgroundTasks','FastAPI BackgroundTasks 在什么时候执行？任务函数能否使用 async def？何时应考虑 Celery？')
c.claim('任务在返回响应之后运行，任务函数支持普通 def 和 async def。',('fastapi_background','after returning a response'),('fastapi_background','async def or normal'))
c.claim('小型、需共享进程对象的后台工作可使用 BackgroundTasks；跨进程或跨服务器的重型计算可考虑 Celery 等队列工具。',('fastapi_background','multiple processes'),('fastapi_background','small background tasks'));c.save()
c=Case('official_docs','Qdrant 距离度量','Qdrant collection 文档列出哪些常用稠密向量距离度量？Cosine 上传时有什么处理？')
c.claim('度量包括 Dot、Cosine、Euclid、Manhattan；Cosine 通过归一化向量的点积实现，上传时自动归一化。',('qdrant_collections','Manhattan distance'),('qdrant_collections','automatically normalized'));c.save()
c=Case('official_docs','Pydantic 正整数列表','如何使用 Pydantic 的 Annotated 与 Field，使列表的每个整数元素都大于 0？')
c.claim('使用 list[Annotated[int, Field(gt=0)]]，约束施加于元素；[1,3] 有效，包含负数或 0 的元素不满足 gt=0。',('pydantic_fields','int_list: list[Annotated[int, Field(gt=0)]]'));c.save()
c=Case('official_docs','Compose 就绪条件','Docker Compose depends_on 是否默认等待数据库就绪？如何等待健康检查或一次性任务完成？')
c.claim('默认只保证依赖容器已运行，不保证服务就绪；service_healthy 配合 healthcheck 等待健康，service_completed_successfully 等待成功完成。',('docker_depends','only until'),('docker_depends','service_completed_successfully'));c.save()
c=Case('official_docs','pgvector 距离算子','列出 pgvector 的 L2、内积、余弦、L1、Hamming、Jaccard 距离算子，并说明内积算子的符号。')
c.claim('依次是 <->、<#>、<=>、<+>、<~>、<%>；<#> 返回负内积以适配 ASC 索引扫描；Hamming 与 Jaccard 针对二进制向量。',('pgvector_readme','Supported distance functions'),('pgvector_readme','negative inner product'));c.save()
c=Case('official_docs','HTTPX 异步客户端生命周期','在异步请求循环中如何复用和关闭 HTTPX AsyncClient？为什么不推荐在热循环里反复创建客户端？')
c.claim('使用有作用域或共享的 AsyncClient 复用连接池，避免热循环中多次实例化；用 async with 或 await client.aclose() 关闭。',('httpx_async','hot loop'),('httpx_async','await client.aclose()'));c.save()
c=Case('official_docs','Redis 持久化','解释 Redis RDB 与 AOF 的基本机制、能否同时启用，以及默认 every-second fsync 策略的数据丢失窗口。')
c.claim('RDB 是按时间点保存的数据集快照；AOF 记录写操作并可重放；两者可同时启用。',('redis_persistence','point-in-time snapshots'),('redis_persistence','RDB + AOF'))
c.claim('文档对默认每秒 fsync 的说明是可能丢失约一秒写入，不能声称绝对零丢失。',('redis_persistence','one second worth of writes'));c.save()
c=Case('official_docs','PostgreSQL 索引类型','PostgreSQL 17 的默认索引是什么？GIN 与 BRIN 分别适用于什么数据特点？')
c.claim('CREATE INDEX 默认 B-tree；GIN 是倒排索引，适合包含多个组件值的数据；BRIN 保存物理块范围摘要，适合值与物理存储顺序相关的数据。',('postgres_indexes','By default'),('postgres_indexes','inverted'),('postgres_indexes','well-correlated'));c.save()
c=Case('official_docs','SQLite WAL 限制','SQLite WAL 的读写并发优势是什么？是否适合多个主机通过网络文件系统共享同一数据库？')
c.claim('WAL 允许读写并行，读者不阻塞写者、写者不阻塞读者；但仍只有一个写者。',('sqlite_wal','readers do not block writers'),('sqlite_wal','only be one writer'))
c.claim('使用数据库的进程必须在同一主机；WAL 不适用于这种跨主机网络文件系统共享。',('sqlite_wal','same host computer'));c.save()

# 3. Each comparison uses at least two independently fetched primary-source documents.
c=Case('comparison','Requests vs HTTPX 异步请求','为异步 Agent 批量调用 HTTP API，比较 Requests 与 HTTPX 的非阻塞支持、连接复用和流式读取。给出有条件的选择。')
c.claim('Requests 默认 transport 不提供非阻塞 I/O，stream=True 也不使读取变成非阻塞；HTTPX 提供 AsyncClient 与异步流式迭代。',('requests_advanced','does not provide any kind of non-blocking IO'),('httpx_async','AsyncClient.stream(method, url, ...)'))
c.claim('Requests Session 可复用连接；HTTPX 应复用 AsyncClient 并管理关闭。纯 async 调用场景可优先 HTTPX；不要据此断言 Requests 在所有场景都不适用。',('requests_advanced','within a session'),('httpx_async','hot loop'));c.save()
c=Case('comparison','BackgroundTasks vs Celery','比较 FastAPI BackgroundTasks 与 Celery，场景分别是轻量通知与跨服务器后台任务；说明部署和消息确认的限制。')
c.claim('BackgroundTasks 适合轻量、同应用对象访问；Celery 需要消息队列等配置并支持跨进程或服务器工作。',('fastapi_background','Celery'),('celery_tasks','worker'))
c.claim('不能将 Celery 描述为天然 exactly-once；文档强调幂等任务，acks_late 与重试有不同语义。',('celery_tasks','idempotent'),('fastapi_background','message/job queue'));c.save()
c=Case('comparison','FastAPI vs Flask 后台工作','比较 FastAPI BackgroundTasks 与默认 WSGI 部署的 Flask async view：响应之后的工作应如何安排？')
c.claim('FastAPI 有响应后执行的 BackgroundTasks；Flask 默认 async view 完成后，其事件循环中的未完成任务会取消，不应直接用 create_task 充当持久后台队列。',('fastapi_background','after returning a response'),('flask_async','will be cancelled'))
c.claim('限定 Flask 的默认 WSGI 场景；文档另有 ASGI 加 WsgiToAsgi 的例外，不能声称 Flask 永远无法运行长期异步任务。',('flask_async','WsgiToAsgi'),('fastapi_background','Celery'));c.save()
c=Case('comparison','Qdrant vs pgvector 向量检索','比较 Qdrant 和 pgvector 的距离度量、部署形态与过滤表达；不要给出无实测支持的性能排名。')
c.claim('Qdrant 文档列出 Dot/Cosine/Euclid/Manhattan；pgvector 还列出针对二进制向量的 Hamming/Jaccard，须区分向量类型。',('qdrant_collections','Manhattan'),('pgvector_readme','Jaccard'))
c.claim('pgvector 是 Postgres 扩展并使用 SQL WHERE；Qdrant 以 collection/payload 条件表达过滤。',('pgvector_readme','CREATE EXTENSION'),('pgvector_readme','WHERE'),('qdrant_filtering','you can impose conditions on both the'));c.save()
c=Case('comparison','Docker volume vs bind mount','为容器数据库持久化和开发源码共享分别比较 Docker volume 与 bind mount 的管理方式、可移植性及主机写入影响。')
c.claim('volume 由 Docker 管理，适合容器产生的数据持久化；bind mount 直接映射主机路径，依赖主机目录布局。',('docker_volumes','managed by Docker'),('docker_bind','directory on the host'))
c.claim('bind mount 默认可写主机文件，可用 readonly/ro 限制；不能把删除容器等同于自动删除持久 volume。',('docker_bind','write access'),('docker_volumes','remove the container'));c.save()
c=Case('comparison','asyncio.gather vs futures.as_completed','比较 Python 3.12 asyncio.gather 与 concurrent.futures.as_completed 的输入模型、结果顺序及异常获取方式。')
c.claim('gather 并发等待 awaitables，成功结果按输入顺序排列；as_completed 迭代完成的 Future，应逐个调用 result() 取值或接收异常。',('python_asyncio','order of awaitables'),('python_futures','Returns an iterator over the'))
c.claim('asyncio 协程并发与 Executor 的线程/进程执行不是同一种执行模型；不把 gather 说成自动创建线程池。',('python_asyncio','automatically scheduled as a Task'),('python_futures','pool of threads'));c.save()
c=Case('comparison','LangGraph vs CrewAI 编排','根据两项目官方 README，比较 LangGraph 与 CrewAI 的编排抽象、状态恢复和协作方式，为需人工介入的状态流程说明选择依据。')
c.claim('LangGraph 明确强调 stateful workflow、durable execution 和 human-in-the-loop；CrewAI 用 Crews 表达角色协作，用 Flows 表达事件驱动控制。',('langgraph_readme','Human-in-the-loop'),('crewai_readme','CrewAI Flows'))
c.claim('建议应与控制、状态及协作需求关联；不能因某 README 未展开某功能就断言另一项目不支持该功能。',('langgraph_readme','stateful'),('crewai_readme','event-driven'));c.save()
c=Case('comparison','Pydantic 默认转换 vs strict','对接收外部 JSON 的 Agent 配置，比较 Pydantic 默认模式、调用级 strict=True 和字段级 strict 的作用范围。')
c.claim('默认可以把字符串 123 转为整数；严格模式会拒绝示例中的字符串整数；strict 可在校验调用或字段配置启用。',('pydantic_strict',"'123'"),('pydantic_fields','strict=True'))
c.claim('strict 并非所有类型和输入通道完全一致；JSON 输入对某些日期时间类型更宽松，需按类型与输入方式解释。',('pydantic_strict','looser rules may apply'),('pydantic_fields','name: str = Field(strict=True)'));c.save()
c=Case('comparison','SQLite WAL vs Redis 持久化','比较 SQLite WAL 与 Redis RDB/AOF，用于单机 Agent 状态保存时分别说明并发、持久化机制及故障限制。')
c.claim('SQLite WAL 在单机共享内存约束下支持读写并行但只允许一个写者；Redis RDB 是快照，AOF 是写操作日志，不能把二者机制混为一谈。',('sqlite_wal','only be one writer'),('redis_persistence','point-in-time snapshots'))
c.claim('应说明 SQLite WAL 不支持跨主机网络文件系统方案，以及 Redis every-second fsync 的约一秒丢失窗口；不作没有数据支撑的吞吐比较。',('sqlite_wal','same host computer'),('redis_persistence','one second worth'));c.save()
c=Case('comparison','HTTP 流式响应 vs WebSocket','在 FastAPI 中比较 StreamingResponse 和 WebSocket：持续输出 Agent token 与同一连接上的双向交互分别如何实现？')
c.claim('StreamingResponse 消费普通或异步生成器并流式返回 HTTP 响应体；WebSocket 示例在连接内接收文本并发送文本，适合双向交互。',('fastapi_streaming','normal generator/iterator'),('fastapi_websockets','receive_text'))
c.claim('WebSocket 示例先接受连接，再循环接收和发送文本；StreamingResponse 则通过迭代生成器发送响应体，二者的接口使用方式不同。',('fastapi_streaming','streams the response body'),('fastapi_websockets','accept'));c.save()

# 4. Multi-hop tasks require joining identities, documentation, and metadata.
c=Case('multi_hop','Python Agent 项目版本比较','核验 browser-use/browser-use、crewAIInc/crewAI、pydantic/pydantic-ai 是否都被 GitHub 识别为 Python 且许可证为 MIT，再查询各自 latest Release 的发布时间并排序。')
for key in ['browser','crewai','pydantic_ai']:
 c.fact('repo_'+key,'/full_name','full_name');c.fact('repo_'+key,'/language','primary_language');c.fact('repo_'+key,'/license/spdx_id','license_spdx');c.release(key)
order=sorted(['browser','crewai','pydantic_ai'],key=lambda key:data('latest_'+key)['published_at'],reverse=True)
c.claim('按所采集 latest Release 发布时间从新到旧为：'+'、'.join(data('repo_'+k)['full_name'] for k in order)+'。',*[(('latest_'+k),data('latest_'+k)['published_at']) for k in order]);c.save()
c=Case('multi_hop','向量项目实现与能力关联','将 Qdrant 和 pgvector 的官方仓库、主要语言与距离能力对应起来，确认哪个是 PostgreSQL 扩展，避免把元数据配到另一个项目。')
for key in ['qdrant','pgvector']:
 c.fact('repo_'+key,'/full_name','full_name');c.fact('repo_'+key,'/language','primary_language')
c.claim('Qdrant 对应 Rust 和 collection 度量配置；pgvector 对应 C 和 PostgreSQL 扩展，支持 SQL 距离算子。',('qdrant_collections','Cosine'),('pgvector_readme','CREATE EXTENSION'));c.save()
c=Case('multi_hop','从归档项目追踪替代库','检查 encode/requests-async 是否归档，阅读它推荐的替代客户端，再查询替代库的官方仓库许可证与 latest Release。')
c.fact('repo_requests_async','/archived','archived');c.claim('README 推荐 httpx.AsyncClient()，替代项目是 encode/httpx。',('requests_async_readme','httpx.AsyncClient()'))
c.fact('repo_httpx','/full_name','full_name');c.fact('repo_httpx','/license/spdx_id','license_spdx');c.release('httpx');c.save()
c=Case('multi_hop','Browser Use Python 版本交叉核验','交叉核验 browser-use 默认分支 README 的最低 Python、uv 示例版本和 pyproject.toml 的 requires-python，然后报告 GitHub latest Release；不要假设默认分支文件就是该 tag 的文件。')
c.claim('README 最低 Python 3.11，uv 示例选 3.12；当前默认分支 pyproject 声明 >=3.11,<4.0，示例版本并非最低版本。',('browser_readme','Python >= 3.11'),('browser_readme','uv init --python 3.12'),('browser_pyproject','requires-python = ">=3.11,<4.0"'))
c.release('browser');c.save()
c=Case('multi_hop','LangGraph 持久化与仓库确认','从 LangGraph 官方持久化文档区分 checkpointer 和 store 的用途，再确认官方 GitHub 仓库身份与许可证。')
c.claim('checkpointer 用于线程内短期记忆，store 用于跨会话长期记忆；线程恢复需要稳定 thread_id。',('langgraph_persistence','short-term memory'),('langgraph_persistence','Pass a thread_id'))
c.fact('repo_langgraph','/full_name','full_name');c.fact('repo_langgraph','/license/spdx_id','license_spdx');c.save()
c=Case('multi_hop','CrewAI MCP 支持与版本','用 CrewAI 官方文档确认 MCP 工具集成及列出的 transport，再定位 GitHub 仓库，报告语言和 latest Release 时间。')
c.claim('CrewAI 官方 MCP 文档列出 Stdio、SSE 和 Streamable HTTP transport，将 MCP server 的工具接入 Agent。',('crewai_mcp','Stdio Transport (Local Servers)'),('crewai_mcp','Utilize flexible Streamable HTTP'))
c.fact('repo_crewai','/language','primary_language');c.release('crewai');c.save()
c=Case('multi_hop','Pydantic AI MCP 支持与版本','通过 Pydantic AI 官方 MCP 文档和 README 核验 MCP 能力，再确认仓库语言、许可证和 latest Release。')
c.claim('官方 MCP 文档与 README 的 MCP capability 示例都支持它具备 MCP 集成这一结论；不要仅依据仓库名称推断。',('pydantic_ai_mcp','can connect to MCP servers and use their tools'),('pydantic_ai_readme',"capabilities=[MCP("))
c.fact('repo_pydantic_ai','/language','primary_language');c.fact('repo_pydantic_ai','/license/spdx_id','license_spdx');c.release('pydantic_ai');c.save()
c=Case('multi_hop','Celery 稳定版与消息语义','查看 Celery Release 列表与 latest 端点，排除预发布候选，再根据官方任务文档解释 acks_late 是否保证 exactly-once。')
c.fact('releases_celery','/0/tag_name','first_listed_tag');c.fact('releases_celery','/0/prerelease','first_listed_prerelease');c.release('celery')
c.claim('acks_late 在任务返回后确认，但不是 exactly-once 保证；任务应幂等，子进程某些终止情形仍会确认消息。',('celery_tasks','idempotent'),('celery_tasks','even when'))
c.save()
c=Case('multi_hop','pgvector 发布渠道与兼容性','查询 pgvector 是否有 GitHub Release，再查 tags 的首个返回项，并从官方 README 确认支持的 PostgreSQL 最低版本；区分 tag 与 Release。')
c.fact('releases_pgvector','','github_releases');c.fact('pgvector_tags','/0/name','first_returned_tag')
c.claim('采集的 README 声明支持 Postgres 13+；空 Release 列表不意味着没有软件版本。',('pgvector_readme','supports Postgres 13+'),('pgvector_tags',data('pgvector_tags')[0]['name']));c.save()
c=Case('multi_hop','FastAPI 仓库迁移后查版本','从旧地址 tiangolo/fastapi 定位当前规范仓库，再查询该仓库 latest Release，并用官方文档说明 BackgroundTasks 可接受哪些函数形式。')
c.fact('repo_old_fastapi','/full_name','canonical_repository');c.release('fastapi')
c.claim('BackgroundTasks 接受普通 def 与 async def 函数，FastAPI 会处理相应调用。',('fastapi_background','async def or normal'));c.save()

# 5. Real observed boundary situations, never simulated network failures.
c=Case('edge_case','归档不等于不存在','encode/requests-async 已归档是否意味着项目不存在？报告实际状态及 README 的替代建议。')
c.fact('repo_requests_async','/archived','archived');c.fact('repo_requests_async','/full_name','full_name')
c.claim('归档仓库仍可读取；README 推荐 httpx.AsyncClient()，不能编造该项目仍在活跃维护。',('requests_async_readme','httpx.AsyncClient()'));c.save()
c=Case('edge_case','Auto-GPT-Plugins 归档状态','核验 Significant-Gravitas/Auto-GPT-Plugins 的归档状态、默认分支与语言；不能把旧插件仓库的状态推断为整个 AutoGPT 项目的状态。')
for field in ['archived','default_branch','language']:c.fact('repo_autogpt_plugins','/'+field,field)
c.claim('结论仅适用于 Auto-GPT-Plugins 这个仓库；不得扩展为整个 AutoGPT 项目已停止。',('repo_autogpt_plugins','Significant-Gravitas/Auto-GPT-Plugins'));c.save()
c=Case('edge_case','pgvector 没有 Release 但有 tag','pgvector/pgvector 的 GitHub Releases 列表为空时，能否得出没有版本的结论？用 tags 核验。')
c.fact('releases_pgvector','','github_releases');c.fact('pgvector_tags','/0/name','first_returned_tag')
c.claim('不能从空 GitHub Releases 列表推出没有版本；tags 返回了版本标签。不要把 tag 的时间或名称冒充 Release published_at。',('pgvector_tags',data('pgvector_tags')[0]['name']));c.save()
c=Case('edge_case','awesome-python 没有 Release','查询 vinta/awesome-python 最新 GitHub Release；若采集的列表为空，应如何作答？')
c.fact('releases_awesome_python','','github_releases')
c.claim('应明确该采集结果中无 GitHub Release，无法给出其 Release 版本和发布时间；不能编造 v1.0 或声称仓库不存在。',('repo_awesome_python','vinta/awesome-python'));c.save()
c=Case('edge_case','FastAPI 旧 owner','访问 tiangolo/fastapi 返回了不同 full_name，应怎样识别项目？')
c.fact('repo_old_fastapi','/full_name','canonical_repository')
c.claim('旧地址请求成功且解析到 fastapi/fastapi；应说明规范地址变化，不判为项目不存在。',('repo_old_fastapi','fastapi/fastapi'));c.save()
c=Case('edge_case','LangChain 旧 owner','用户提供 hwchase17/langchain，查询返回的规范仓库是什么？是否应直接报告找不到项目？')
c.fact('repo_old_langchain','/full_name','canonical_repository')
c.claim('应识别为 langchain-ai/langchain，旧 owner 路径的成功解析不等于不存在。',('repo_old_langchain','langchain-ai/langchain'));c.save()
c=Case('edge_case','LangGraph 组件与 prerelease 标志','LangGraph 采集的 Release 列表首项能否直接当成 Python langgraph 核心包最新稳定版本？检查标签名及 prerelease 字段。')
c.fact('releases_langgraph','/0/tag_name','first_listed_tag');c.fact('releases_langgraph','/0/prerelease','github_prerelease_flag')
c.claim('首项 cli==0.4.32.dev0 指向 CLI 且标签包含 dev0；即使 GitHub prerelease 字段为 false，也不能把它当作核心 langgraph 包稳定版。',('releases_langgraph','cli==0.4.32.dev0'));c.save()
c=Case('edge_case','Celery 预发布混入列表','Celery Release 列表首项与 latest 端点不一致时，查询稳定版应该报告什么并解释差别？')
c.fact('releases_celery','/0/tag_name','first_listed_tag');c.fact('releases_celery','/0/prerelease','first_listed_prerelease');c.release('celery')
c.claim('列表首项 v5.7.0a1 为预发布，而 latest 端点返回 v5.6.3；不应只取列表第一项。',('releases_celery','v5.7.0a1'),('latest_celery','v5.6.3'));c.save()
c=Case('edge_case','NOASSERTION 不等于无许可证','GitHub 对 pgvector 返回 license.spdx_id=NOASSERTION，是否可以断言项目没有许可证？核对实际 LICENSE 文件。')
c.fact('repo_pgvector','/license/spdx_id','github_license_spdx')
c.claim('NOASSERTION 表示该 API 字段未给出确定 SPDX 标识，不等于没有许可证；实际 LICENSE 存在并包含使用、复制、修改和分发的许可文字。不要擅自将 API 值改成 MIT。',('pgvector_license','Permission to use, copy, modify, and distribute'));c.save()
c=Case('edge_case','Python 3.12 误用 3.13 API','开发者使用 Python 3.12，却找到 asyncio.Queue.shutdown 文档。对比 3.12 和 3.13 文档，判断能否直接采用。')
c.claim('Queue.shutdown 在 3.13 文档标记为 3.13 新增，3.12 的 Queue API 页面没有该方法；不能将新版 API 直接声称为 3.12 可用。',('python_queue_313','Added in version 3.13'),('python_queue','Queue'))
assert 'shutdown' not in read('python_queue').lower()
c.save()

assert Counter(c['category'] for c in CASES)==Counter({k:10 for k in CATEGORIES})
used={e['artifact_id'] for c in CASES for e in c['ground_truth']['evidence']}
artifacts=[]
for key in sorted(used):
 m=meta(key); body=ROOT/'sources'/key/'body'
 assert hashlib.sha256(body.read_bytes()).hexdigest()==m['sha256']
 artifacts.append(dict(id=key,url=m['requested_url'],path=f'sources/{key}/body',sha256=m['sha256'],captured_at=m['retrieved_at']))
(ROOT/'manifest.json').write_text(json.dumps(dict(id=SNAPSHOT,synthetic=False,artifacts=artifacts,faults=[]),indent=2)+'\n')
(ROOT/'annotation_checks.json').write_text(json.dumps(PROOFS,ensure_ascii=False,indent=2)+'\n')
(ROOT/'dataset.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in CASES))

lines=['# AgentResearch 真实资料审阅集 v1','', '**50 条任务，每类 10 条；全部依据实际抓取的一手来源。人工审阅状态：待审阅。**','',
'这是一套真实来源的候选 benchmark，不是已经人工验收的标准答案。事实字段直接从保存的 JSON 响应提取；语义答案为对已抓取资料的中文归纳，逐项附来源定位，仍需你审核。没有使用虚构仓库、虚构版本或注入故障。','',
'## 审阅入口','',
'- 按下方目录打开五类审阅表，查看问题、标准事实、语义评分项及来源。','- `cases/<类别>/*.json`：兼容项目 BenchmarkCase 的独立样本；`dataset.jsonl` 为同一批数据的合集。','- `sources/<来源>/body`：抓取的原始响应；`text.txt`：便于阅读的派生文本；`metadata.json`：原始/最终 URL、HTTP 状态、抓取时刻、响应头、SHA-256。','- `manifest.json`：所有被样本引用的原文及哈希；`annotation_checks.json`：事实 JSON Pointer 和语义资料定位检查。','',
'## 时间与真实性边界','',
f'- 被引用的来源共 {len(used)} 份。采集区间：{min(meta(k)["retrieved_at"] for k in used)} 至 {max(meta(k)["retrieved_at"] for k in used)}。','- stars、Release、默认分支内容等答案只对保存的采集快照成立；不同端点为先后抓取，不是原子一致的数据库快照。','- latest Release 以 GitHub `/releases/latest` 响应为准；这不自动等同于 PyPI 最新版或最高语义版本。分页 Release 列表仅用于问明的首项、候选和空列表检查，不据此推断全量历史。','- 文档页的 latest/stable/default branch 可能变化，原始内容与哈希已冻结；不将默认分支文档假定为某个 release tag 的文档。','- 真实异常类覆盖归档、无 Release、有 tag、旧地址解析、组件/预发布混淆、许可证识别不确定和文档版本错配；未伪造 404、rate limit、timeout 或不存在的项目。','- 多跳题采用明确候选项目，要求联结不同资料；不是开放世界的完整项目名单。','- 过程评分需要未来实际 Agent 运行轨迹；此次仅收集任务和可核验答案，没有伪造轨迹、实测性能或评测成绩。','- 比较题是面向场景的参考要点，不是性能实测；功能未在某资料提及不等于不支持。','',
'## 评分与验证','',
'每条样本包含 task、ground_truth、evaluation_rule。事实匹配、语义要点、证据支撑和可观察查证分别评分；总分阈值 0.8 且所有 required 检查通过。分类权重沿用 benchmark v1。中文要点允许等价表述，不要求逐字复述。','',
'本目录内运行 `PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python validate.py` 检查 5×10 数量、模型结构、来源引用、哈希、JSON 事实及文本定位。检查只能验证完整性与提取一致性，不能替代人对语义标注的审核。','',
'`collect.py` 是采集脚本（需要联网，已有成功快照不会覆盖）；`build_dataset.py` 从原文构建样本与审阅页。重采集新数据应新建版本目录，避免覆盖本次审阅材料。','',
'## 五类目录','']
for category,label in zip(CATEGORIES,LABELS):
 lines.append(f'- [{label}：10 条]({category}.md)')
 group=[c for c in CASES if c['category']==category]
 review=[f'# {label}（10 条）','', '[返回总览](README.md)','']
 for c in group:
  title=next(p['title'] for p in PROOFS if p['case_id']==c['id'])
  review += [f'## {c["id"]}：{title}','',f'**任务：** {c["task"]["prompt"]}','',f'**快照时间边界：** {c["task"]["as_of"]}','',f'[完整 JSON](cases/{category}/{c["id"]}.json)','', '**Ground truth / 必需评分项：**','']
  for fact in c['ground_truth']['facts']:
   review.append(f'- `{fact["subject"]}.{fact["predicate"]}` = `{json.dumps(fact["expected"]["value"],ensure_ascii=False)}`（证据：{", ".join(fact["evidence_ids"])}）')
  for r in c['ground_truth']['rubrics']:
   review.append(f'- {r["criterion"]}（证据：{", ".join(r["evidence_ids"])}）')
  review += ['', '**来源与定位：**','']
  for e in c['ground_truth']['evidence']:
   review.append(f'- `{e["id"]}` [{e["artifact_id"]}]({e["url"]}) · [本地资料](sources/{e["artifact_id"]}/text.txt) · {e["locator"]}')
  review += ['', '**审阅：** [ ] 事实正确　[ ] 来源支撑充分　[ ] 问题清晰　[ ] 评分合理','']
 (ROOT/f'{category}.md').write_text('\n'.join(review)+'\n')
(ROOT/'README.md').write_text('\n'.join(lines)+'\n')
print(f'Built {len(CASES)} cases, {len(used)} cited sources')
