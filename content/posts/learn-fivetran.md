---
title: 学会 Fivetran：从 ELT、MAR 到运维的完整入门课
date: 2026-05-13T18:35:52+08:00
draft: true
categories:
  - "数据库"
tags:
  - "fivetran"
  - "elt"
  - "dbt"
  - "tutorial"
keywords: fivetran,elt,mar,dbt,reverse etl,tutorial
---

如果你第一次接触 Fivetran，很容易把它理解成“一个把数据搬到数仓里的 SaaS 工具”。

这个理解不算错，但远远不够。

真正想把 Fivetran 学明白，你需要同时搞清楚它的三层角色：

- 它在现代数据栈里负责什么
- 它是如何同步、删行、保留历史和处理 schema 变化的
- 它在生产环境里为什么会变贵、变慢，或者变得难维护

这篇文章把这些问题串成一套完整入门课。目标不是带你记住控制台里有哪些按钮，而是帮你建立一个足够稳定的工程心智模型。

<!-- more -->

# 先建立一个正确的总模型

先把 Fivetran 放进这条链路里：

`Source -> Fivetran Connector -> Destination -> Transformations/dbt -> BI/Activation`

它本质上是一个托管式 `ELT` 平台，而不是传统意义上把大量业务规则塞进抽取流程里的 `ETL` 工具。

这意味着：

- 先把源数据稳定同步进 destination
- 再在目标端做 SQL 或 dbt 转换
- 最终把结果交给 BI、数据产品，或者回写到业务系统

如果只压缩成一句话，那就是：

`Fivetran 负责 data movement，dbt 负责 data modeling。`

# 第一课：先搞懂 Fivetran 在做什么

Fivetran 最核心的几个对象并不多：

- `Connector`：接入某个 source 的同步器
- `Destination`：数据最终落地的位置
- `Connection`：一条从 source 到 destination 的长期同步链路
- `Transformation`：数据入仓后的后置转换
- `Activation`：把数仓结果再同步回 CRM、广告、营销等业务系统，也就是 reverse ETL

这几样东西背后有一个非常重要的工程思想：原始数据先保留，再转换。

这和很多老式 ETL 工具的区别很大。它不是在源端前面拼命加工，而是优先保证数据能稳定、自动、持续地落进仓库，然后把建模交给更适合版本管理和测试的层，比如 dbt。

如果你刚开始学，只需要先抓住下面四个问题：

1. 它如何做首轮全量同步和后续增量同步
2. 源端 schema 变化后，它如何映射到 destination
3. 它把数据落成什么样
4. 它的核心计费单位为什么不是“同步次数”

# 第二课：第一次创建一条 connection，到底在配什么

一条 Fivetran connection 并不是“填几个参数连一下数据库”，而是在定义一条长期运行的数据同步合同。

通常你实际在配置的是：

- `Source`：从哪里取数
- `Destination`：落到哪里
- `Credentials / Access`：用什么权限访问 source 和 destination
- `Objects / Schema`：哪些表或对象要同步
- `Sync Behavior`：多久同步一次，是否允许重同步
- `Post-load Actions`：同步后是否触发 transformations

很多新手第一次使用时，只关注 `Save & test` 能不能通过，但这只是最浅的一层。真正更重要的是：

- source 账号是不是最小权限
- destination schema name 是否可长期维护
- 是否一开始只开了少量关键表做观察
- 后续 schema 变化是否可控

我很建议第一次实操时按下面顺序思考：

1. 先确定 destination
2. 再选择一个最简单的 source
3. 明确 destination schema name
4. 只开启少量对象做 initial sync
5. 在 destination 里检查落库结构和系统列

`destination schema name` 尤其不要乱起。因为它会变成后续下游建模、权限管理和文档说明里的长期接口。像 `raw_hubspot_dev`、`raw_postgres_prod` 这样的命名，通常会比 `test2`、`demo_new` 稳定得多。

# 第三课：增量同步、删除和历史版本，才是 Fivetran 的核心

真正理解 Fivetran，关键不在 UI，而在同步语义。

它的基本工作方式是：

- 首次运行时做 `initial sync`
- 之后进入 `incremental sync`
- 通过 cursor 和 checkpoint 记录同步进度
- 失败后从 checkpoint 恢复，而不是简单整批重来

这意味着它正常情况下不是每次全量扫表，而是尽量只抓“新增或变化的数据”。

但更关键的是两种同步模式：

- `Soft delete mode`
- `History mode`

## Soft delete mode

在 soft delete mode 下，目标表中的已删除记录通常不会被物理删除，而是通过系统列标记其状态。

最常见的是：

- `_fivetran_synced`
- `_fivetran_deleted`
- `_fivetran_index`

其中 `_fivetran_deleted = true` 表示这行已经在源端删除，或者这是一条被标记失效的旧版本记录。

如果你想查“当前有效数据”，通常要显式过滤：

```sql
where _fivetran_deleted = false
```

## History mode

`History mode` 则更进一步，它实现的是 `SCD Type 2` 风格的历史保留。

也就是说：

- 一条记录发生变化时
- 旧值不会直接被覆盖
- 系统会保留旧版本，再插入一条新版本

这会引入另外几列：

- `_fivetran_active`
- `_fivetran_start`
- `_fivetran_end`

这三列决定了你如何做当前状态查询和时点查询。

查当前状态时，通常写：

```sql
where _fivetran_active = true
```

查某个时间点的状态时，通常写：

```sql
where _fivetran_start <= '2026-05-01'
  and _fivetran_end > '2026-05-01'
```

所以一定要分清：

- `soft delete` 更关注“当前哪些行还有效”
- `history mode` 更关注“每个版本在什么时间段有效”

这两者不是一回事。

# 第四课：Fivetran 落库后到底长什么样

很多人会在 destination 里直接看到一堆表，但不知道这些表背后的约束是什么。

Fivetran 落库后的几个原则非常重要：

- 它会用你配置的 destination schema name 创建 schema
- 这个 schema name 是长期接口，不应频繁改动
- 它自己维护 source 到 destination 的结构映射
- 它管理的是 raw/base layer，不是你的业务模型层

因此最重要的实践只有一条：

`不要在 Fivetran 管理的 base tables 上直接做业务建模或手工结构改造。`

更稳妥的分层是：

- Fivetran 负责 `raw` 或 `base`
- 你自己的 dbt / SQL 模型放到单独 schema

## 你常会看到的系统列

常见系统列包括：

- `_fivetran_synced`
- `_fivetran_deleted`
- `_fivetran_index`
- `_fivetran_id`

其中 `_fivetran_id` 往往意味着源表没有稳定主键，Fivetran 需要生成内部 surrogate key 来帮助去重和识别记录。

这是一条非常实用的判断经验：

如果你在某张表里看到了 `_fivetran_id`，就应该立刻提高警惕，重新评估：

- 这张表有没有稳定业务主键
- 下游 join 是否可靠
- 更新是否可能表现成删旧插新
- 是否需要在 transformation 层补自己的唯一键逻辑

## 命名规则也要尽早理解

Fivetran 支持 `Fivetran naming` 和 `Source naming` 两种思路。

通常来说：

- 想要标准化、少踩保留字和命名兼容性问题，优先选 `Fivetran naming`
- 想尽量保留 source 原始命名，再考虑 `Source naming`

但后者并不总是最佳默认值，尤其在你还没有稳定数据建模规范的时候。

# 第五课：MAR、同步频率和重同步，决定了它会不会又贵又慢

Fivetran 一个最容易被误解的点，是计费和成本。

很多人会本能地以为：

`同步越频繁，账单就一定越高`

这并不准确。

它的核心计费概念是 `MAR`，也就是 `Monthly Active Rows`。你可以先这样理解：

- 关注的是一个月内发生过同步变化的不同主键行数
- 不是简单按“调度跑了多少次”计费
- 同一行在同一个月里多次更新，通常不会重复计为多行

这就是为什么“同步次数”本身并不是最关键的成本变量。

真正更值得关注的是：

- 有没有大量高频变化的表
- 有没有 history mode 带来的版本膨胀
- 有没有无主键表导致的高 churn
- 有没有重复同步到多个 destination
- 有没有频繁的大范围 `re-sync`

## 为什么同步频率仍然重要

虽然频率不直接等于 MAR，但它仍然会影响：

- source 压力
- destination 写入压力
- 故障重试噪音
- 整体链路延迟
- 运维复杂度

所以不要把频率一上来就调到最小，而应该按业务 SLA 来设。

## 为什么 re-sync 不该当作常规手段

`re-sync` 即使不一定总是造成付费 MAR 灾难，也常常会造成：

- 更长的同步时间
- 更大的 source 负担
- 更高的 destination 写入量
- 更难解释的数据波动

它更像一把修复工具，而不是日常刷新按钮。

## history mode 不是默认值

history mode 很有价值，但不应该默认开启。

更适合开启 history mode 的，通常是：

- 客户维度
- 账户状态
- 员工归属
- 商品属性

不适合轻易开启的，往往是：

- 高频变更事实表
- 只关心当前快照的 operational tables

判断标准很简单：

`你是否真的会问“某个时间点这条记录当时是什么值”。`

如果不会，通常就没必要为它承担更多历史版本成本。

# 第六课：Transformations、Quickstart Data Models 和 dbt

学到这里，很多人会开始问：那 Fivetran 到底能不能做 transformation？

答案是能做，但这不是它的第一职责。

更准确的分工是：

- Fivetran 负责把数据稳定同步到 destination
- transformation 负责把 raw/base 数据变成更适合分析的模型

官方路线主要有两类：

- `Quickstart data models`
- `Transformations for dbt Core`

## Quickstart data models

它更像预构建的数据模型，适合：

- 刚开始接某个 connector
- 想快速得到 analytics-ready 表
- 团队暂时没有成熟 dbt 工程

优点是快，缺点是灵活度有限。

## dbt Core 路线

如果你的团队已经把建模当成工程来维护，那更长期的主线通常还是 dbt：

- 代码在 Git 里管理
- 模型可以评审
- 测试可以版本化
- 文档和 lineage 更清晰
- 更适合跨 source 的复杂业务口径

一句话概括：

- Quickstart 更像托管预制模型
- dbt 更像可长期演进的工程化建模体系

所以最稳妥的理解一直是：

`Fivetran 解决 data movement，dbt 解决 data modeling。`

# 第七课：监控、告警、RBAC 和 API，决定你能不能真正运维它

如果说前面几课是在回答“它怎么工作”，那这一课回答的是“它出问题时你怎么办”。

你最需要熟悉的运维面主要有：

- `Status / Sync History`
- `Alerts`
- `Platform Connector`
- `RBAC`
- `REST API`

## Status 和 Sync History

排障时不要只看“最后一次成功没有”，而要看：

- 上次成功是什么时候
- 是 `Extract`、`Process` 还是 `Load` 变慢
- 最近有没有 schema change
- 最近有没有 warning 或 error
- 最近是否有人做过 pause、resume、resync 或配置变更

`Sync History` 的价值，在于它能让你看见趋势，而不是只看一个瞬间状态。

## Alerts

Alerts 不是装饰栏，而是运维待办。

正确习惯是：

- 先处理 error
- 再评估 warning
- 不要让 warning 长期堆着不管

因为很多真正的大故障，一开始都只是 warning。

## Platform Connector

这是非常值得重视的一项能力。它可以把 Fivetran 自己的元数据、使用量和操作日志同步到 destination，让你在仓库里自己做运维看板，而不是完全依赖控制台 UI。

如果你要把 Fivetran 运维做得更系统化，这往往是比“每天人盯 dashboard”更成熟的入口。

## RBAC 和 API

生产环境里不要默认给太多人高权限。

你至少应该明确：

- 谁能改 connection
- 谁能改 destination
- 谁能触发 re-sync
- 谁能管理 API keys

而在自动化层面，REST API 则适合做：

- 手动触发 sync
- 触发历史重同步
- 更新 connection 配置
- 把 Fivetran 接入更完整的数据平台编排流程

但也别忘了，API 帮你放大效率的同时，也会放大错误操作的影响范围。

# 第八课：如果你想在两周内真正熟悉 Fivetran，该怎么练

学会 Fivetran，不是继续堆更多概念，而是把前面的内容压缩成一套训练路径。

我更推荐下面这条两周路线。

## 第 1 周：建立稳定心智模型

第一周先不追求“会操作全部页面”，只追求讲明白它的工作机制。

建议顺序：

1. 读 Quickstart 和 Core Concepts
2. 读 Sync Overview 和 Sync Modes
3. 读 System Columns 和 Naming
4. 读 Pricing 和 MAR 说明
5. 读 Transformations 和 dbt
6. 读 Status、Alerts、RBAC、REST API
7. 自己不看文档，复述一遍完整架构

如果你到这一步能不用文档就回答下面这些问题，第一周就算过关：

- initial sync 和 incremental sync 的区别是什么
- soft delete 和 history mode 有什么不同
- 为什么 `_fivetran_synced` 不能当业务更新时间
- 为什么 Fivetran 更像 ELT 而不是 ETL
- 为什么同步频率快不等于使用方式合理

## 第 2 周：做最小实验

第二周开始做练习，哪怕你没有生产环境，也可以先做“纸上实战”。

### 实验 1：设计一条最小 connection

自己写出：

- source 是什么
- destination 是什么
- schema name 怎么命名
- 为什么只同步这些表
- sync frequency 为什么设成这个值

### 实验 2：模拟数据变化

假设：

- 源表新增一列
- 源表删除一行
- 源表更新一行属性

分别推演：

- destination 会发生什么
- soft delete 模式下怎么查当前数据
- history mode 下怎么查某个时间点的状态

### 实验 3：做成本判断

挑一张你熟悉的业务表，回答：

- 它为什么可能产生高 MAR
- 是否适合 history mode
- 是否有稳定主键
- 是否存在重复同步到多个 destination 的风险

### 实验 4：做排障演练

假设某条 connection 最近 24 小时明显变慢，你应该先看什么？

一个合理的顺序通常是：

1. 看 Status 和 Sync History
2. 看最近的 Alerts 和 Events
3. 看最近有没有 schema change 或人工配置变更
4. 再决定是否需要更重的修复动作

# 一个我很推荐的能力标准

真正算熟悉 Fivetran，不是会背多少名词，而是面对一条新的同步需求时，你能独立做出这些判断：

- 这个 source 值不值得接
- destination 和 schema 应该怎么命名
- 哪些表先同步，哪些表先别同步
- 是否真的需要 history mode
- 哪些地方有 MAR 风险
- 哪些系统列会影响 SQL 语义
- 出问题时应该先看 UI、metadata 还是 API

如果这些问题你都能独立回答，你就已经不只是“用过 Fivetran”，而是能开始把它当成数据平台的一部分来使用了。

# 小结

Fivetran 真正值得学的地方，从来不只是“能把数据搬过来”。

更重要的是，你能不能看懂它的同步语义、结构映射、历史保留、成本机制和运维边界。

对工程师来说，最有价值的学习闭环通常是：

`从概念理解 -> 到最小实操 -> 再到生产判断`

只要你按这个顺序走，Fivetran 就不会再只是一个控制台里的黑盒，而会变成一套你能解释、能优化、能排障的数据基础设施。

# 参考资料

- [Fivetran Quickstart](https://fivetran.com/docs/getting-started/quickstart)
- [Fivetran Core Concepts](https://fivetran.com/docs/core-concepts)
- [Fivetran Sync Overview](https://fivetran.com/docs/core-concepts/syncoverview)
- [Fivetran Sync Modes](https://fivetran.com/docs/core-concepts/sync-modes)
- [Fivetran History Mode](https://fivetran.com/docs/core-concepts/sync-modes/history-mode)
- [Fivetran System Columns and Tables](https://fivetran.com/docs/core-concepts/system-columns-and-tables)
- [Fivetran Pricing](https://fivetran.com/docs/getting-started/pricing)
- [Fivetran Transformations](https://fivetran.com/docs/transformations)
- [Fivetran dbt Transformations](https://fivetran.com/docs/transformations/dbt)
- [Fivetran Alerts](https://fivetran.com/docs/using-fivetran/fivetran-dashboard/alerts)
- [Fivetran Role-Based Access Control](https://fivetran.com/docs/using-fivetran/fivetran-dashboard/account-settings/role-based-access-control)
- [Fivetran REST API](https://fivetran.com/docs/rest-api)
