---
title: "给 Agent 搭一个自己掌控的知识库"
date: 2026-08-31T15:40:04+08:00
draft: true
categories:
  - "人工智能"
tags:
  - "ai-agent"
  - "obsidian"
  - "cloudflare-vectorize"
  - "mcp"
keywords: "AI Agent,知识库,Obsidian,Cloudflare Vectorize,MCP,GitHub Actions"
---

我一直想给 Agent 搭一个知识库。断断续续琢磨了很久，最近终于做出了一个能用的版本。

这套方案并不复杂：用 Obsidian 管理原始笔记，通过 GitHub Actions 增量建立索引，把向量存进 Cloudflare Vectorize，再由 Cloudflare Worker 以 MCP 服务的形式提供给 Agent。

<!-- more -->

# 知识首先要掌握在自己手里

知识库最重要的不是“库”，而是里面的知识。工作中的专业知识、项目进度和经验判断，只有长期积累下来，才能真正为 Agent 所用。

我对知识管理还有一个基本要求：数据必须由自己完全掌控。这里的“掌控”，是指能够拿到完整的原始文件，也能够自由地迁移、备份和处理它们。一些云笔记很方便，但数据导出往往受平台限制，很难满足这个要求。

因此，我选择了 Obsidian。它的笔记就是本地磁盘上的 Markdown 文件，不依赖专有格式；无论是版本管理、批量处理，还是以后迁移到别的工具，都比较容易。

# 用 PARA 组织笔记

有了工具，还需要一套稳定的组织方法，否则笔记只会越积越多。我采用的是 PARA：Projects、Areas、Resources 和 Archives，分别用来存放项目、领域、资源和归档内容。

PARA 不要求先设计一套复杂的分类体系，而是从内容当前的用途出发，把它放到合适的位置。对我来说，这种方式既方便日常整理，也便于后续把笔记交给程序处理。

# 把笔记接入 Agent

我的知识库链路如下：

```text
Obsidian 笔记
    -> GitHub Actions 增量同步
    -> Cloudflare Worker 调用 Workers AI 生成 embedding
    -> Vectorize 存储和检索向量
    -> MCP 服务向 Agent 提供搜索能力
```

索引部分由 GitHub Actions 定时运行。它读取需要同步的内容，完成切分和变更检测，再把新增或修改的文本发送给 Worker。这样每次只处理发生变化的内容，不必重复索引整个知识库。

Worker 负责调用 Workers AI 生成 embedding，并把向量写入 Vectorize；同步状态则保存在 KV 中。查询时，Agent 通过 MCP 调用语义搜索，不需要知道底层使用了哪一种向量数据库或 embedding 模型。

这套拆分还有一个好处：原始笔记仍然是我手里的 Markdown 文件，Vectorize 只是可以随时重建的检索层。即使以后更换存储或模型，也不会影响原始数据。

对个人知识库的规模而言，Cloudflare Workers、Vectorize 和 GitHub Actions 的免费额度已经能覆盖我目前的日常使用。

# 相关代码

- [cf-knowbase-indexer](https://github.com/tenfyzhong/cf-knowbase-indexer)：增量读取、切分并同步知识库内容。
- [cf-knowbase-api](https://github.com/tenfyzhong/cf-knowbase-api)：生成 embedding、管理向量，并向 Agent 提供 MCP 搜索服务。
