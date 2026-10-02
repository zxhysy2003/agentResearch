# AgentResearch 真实资料审阅集 v1

**50 条任务，每类 10 条；全部依据实际抓取的一手来源。人工审阅状态：待审阅。**

这是一套真实来源的候选 benchmark，不是已经人工验收的标准答案。事实字段直接从保存的 JSON 响应提取；语义答案为对已抓取资料的中文归纳，逐项附来源定位，仍需你审核。没有使用虚构仓库、虚构版本或注入故障。

## 审阅入口

- 按下方目录打开五类审阅表，查看问题、标准事实、语义评分项及来源。
- `cases/<类别>/*.json`：兼容项目 BenchmarkCase 的独立样本；`dataset.jsonl` 为同一批数据的合集。
- `sources/<来源>/body`：抓取的原始响应；`text.txt`：便于阅读的派生文本；`metadata.json`：原始/最终 URL、HTTP 状态、抓取时刻、响应头、SHA-256。
- `manifest.json`：所有被样本引用的原文及哈希；`annotation_checks.json`：事实 JSON Pointer 和语义资料定位检查。

## 时间与真实性边界

- 被引用的来源共 59 份。采集区间：2026-09-29T14:35:30.359917+00:00 至 2026-09-29T14:39:16.671847+00:00。
- stars、Release、默认分支内容等答案只对保存的采集快照成立；不同端点为先后抓取，不是原子一致的数据库快照。
- latest Release 以 GitHub `/releases/latest` 响应为准；这不自动等同于 PyPI 最新版或最高语义版本。分页 Release 列表仅用于问明的首项、候选和空列表检查，不据此推断全量历史。
- 文档页的 latest/stable/default branch 可能变化，原始内容与哈希已冻结；不将默认分支文档假定为某个 release tag 的文档。
- 真实异常类覆盖归档、无 Release、有 tag、旧地址解析、组件/预发布混淆、许可证识别不确定和文档版本错配；未伪造 404、rate limit、timeout 或不存在的项目。
- 多跳题采用明确候选项目，要求联结不同资料；不是开放世界的完整项目名单。
- 过程评分需要未来实际 Agent 运行轨迹；此次仅收集任务和可核验答案，没有伪造轨迹、实测性能或评测成绩。
- 比较题是面向场景的参考要点，不是性能实测；功能未在某资料提及不等于不支持。

## 评分与验证

每条样本包含 task、ground_truth、evaluation_rule。事实匹配、语义要点、证据支撑和可观察查证分别评分；总分阈值 0.8 且所有 required 检查通过。分类权重沿用 benchmark v1。中文要点允许等价表述，不要求逐字复述。

本目录内运行 `PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python validate.py` 检查 5×10 数量、模型结构、来源引用、哈希、JSON 事实及文本定位。检查只能验证完整性与提取一致性，不能替代人对语义标注的审核。

`collect.py` 是采集脚本（需要联网，已有成功快照不会覆盖）；`build_dataset.py` 从原文构建样本与审阅页。重采集新数据应新建版本目录，避免覆盖本次审阅材料。

## 五类目录

- [GitHub 信息检索：10 条](github_lookup.md)
- [官方文档检索：10 条](official_docs.md)
- [多来源技术比较：10 条](comparison.md)
- [多跳 Research：10 条](multi_hop.md)
- [异常与边界：10 条](edge_case.md)
