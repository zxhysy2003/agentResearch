# AgentResearch — 面向开发者的自主技术调研 Agent

## 1.GitHub 信息检索

主要测试：

```
GitHub Search
Repository 信息获取
Release 查询
Issue 查询
README 阅读
```

例如：

```
1. 查询 LangGraph 当前最新稳定版本

2. 查询 Qdrant 最新版本发布时间

3. 查询 browser-use 仓库最近一次 release

4. 找出某 GitHub 项目 stars 数

5. 找出某项目主要使用的编程语言

6. 查询某项目最近关闭的一个 bug issue

7. 查询某项目 README 中推荐的 Python 版本

8. 查询某项目支持哪些 LLM Provider

9. 找出某项目最近一次 breaking change

10. 查询某项目 License
```

## 2. 官方文档检索

例如：

```
LangGraph 如何实现 checkpoint？

FastAPI BackgroundTasks 的用途是什么？

Qdrant 支持哪些距离算法？

Redis Vector Search 支持什么索引？

LangChain structured output 怎么使用？

Pydantic BaseModel 如何限制字段范围？

Python asyncio.gather 遇到异常会发生什么？

PostgreSQL pgvector 支持哪些 distance？

Docker Compose depends_on 有什么作用？

FastAPI StreamingResponse 怎么使用？
```

这里的数据来源必须优先：

```
官方 Documentation
```

## 3.多来源技术比较

例如：

```
LangGraph vs CrewAI

Chroma vs Qdrant

Redis vs PostgreSQL 做 Agent Memory

SSE vs WebSocket 做 Agent Streaming

pgvector vs Qdrant

LangChain vs LlamaIndex

FastAPI vs Flask 做 Agent Backend

Celery vs asyncio

OpenAI Function Calling vs MCP

BM25 vs Vector Search
```

**要求 Agent 覆盖正确的事实维度。**

例如：

```
✓ 是否讨论 persistence
✓ 是否讨论 filtering
✓ 是否讨论 deployment
✓ 是否提供官方来源
```

## 4.多跳 Research

例如：

> 找出 3 个支持 MCP 的 Python Agent 框架，并比较它们最近一次 GitHub Release 的时间。

Agent必须：

```
搜索 Agent Framework
↓
找到项目
↓
确认支持 MCP
↓
进入 GitHub
↓
查询 Release
↓
汇总
```

## 5.异常 / 边界任务

例如：

```
查询一个不存在的 GitHub repo

查询一个已经 archived 的项目

找一个没有 Release 的 repo 最新版本

搜索一个 ambiguous 的项目名称

官方文档返回 404

Web Search 没搜到答案

GitHub API rate limit

两个来源结果冲突

搜索结果是旧版本

某工具 timeout
```

例如：

> 查询 `abc-agent-framework` 的最新版本。

实际上根本不存在。

正确行为应该是：

```
没有找到可靠信息
```

而不是：

```
abc-agent-framework 最新版本是 1.3.2
```