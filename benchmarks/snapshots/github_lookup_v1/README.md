# GitHub 信息检索 MVP 快照 v1

本目录包含配套 [10 道题](../../datasets/github_lookup_v1/README.md) 引用的 10 份真实原始资料。快照 ID 为 `github_lookup_v1`，未模拟任何故障。

- `manifest.json`：原始资料 ID、URL、本地路径、SHA-256 和采集时间的映射。
- `sources/<资料 ID>/body`：Agent 工具可以检索、读取的原始响应。
- `sources/<资料 ID>/text.txt`：同一资料的可读文本，供审阅；证据中的行号指向它。
- `sources/<资料 ID>/metadata.json`：原采集的响应信息，保留来源与时间。

资料复制自原审阅目录，未重新抓取、改写或更新到今天。题目与评分规则留在数据集目录，不在原始资料中。

快照加载器只加载清单列出的 `body` 文件；不要把整个仓库当作搜索语料。查不到时不应回退实时网络。`SnapshotStore` 本身不负责拦截其他工具的联网行为，正式执行仍需工具适配器实现隔离。
