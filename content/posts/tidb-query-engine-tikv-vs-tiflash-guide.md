---
title: "TiDB 引擎选路排查指南：TiKV vs TiFlash 适用场景与性能调优"
date: 2026-08-24T11:00:00+08:00
categories:
  - "数据库"
tags:
  - "tidb"
  - "tikv"
  - "tiflash"
  - "performance"
keywords: "TiDB, TiKV, TiFlash, HTAP, 引擎选路, MPP, 慢查询优化, 数据库性能调优"
---

TiDB 的 HTAP（混合事务与分析处理）架构同时提供行存引擎 **TiKV** 与列存引擎 **TiFlash**。收到 SQL 后，优化器（CBO）会估算不同执行方案的代价，选择将计算下推到 TiKV 或 TiFlash。

排查时常会遇到两个问题：聚合查询为什么没有使用 TiFlash？建好 TiFlash 副本后，查询为什么反而更慢，甚至出现 OOM？答案通常不在“哪个引擎更快”，而在扫描规模、索引、投影列数和计算方式是否匹配。

本文从存储与计算模型、选路依据、常见误区和执行计划四个角度说明 TiKV 与 TiFlash 的取舍。

<!-- more -->

# 一、核心决策速查表

分析具体 SQL 前，可以先按下面几个维度判断引擎方向：

| 判定维度 | 走 TiKV（行存） | 走 TiFlash（列存 + MPP） |
| :--- | :--- | :--- |
| **典型业务场景** | OLTP 事务、精准点查、高频业务 API | OLAP 报表、BI 看板分析、海量数据重度聚合 |
| **扫描数据行数** | $< 10^4$ 行（通过索引快速收敛） | $> 10^5 \sim 10^9$ 行（大范围扫描或全表扫描） |
| **访问列占总列数比例** | $> 50\%$ 或 `SELECT *` 宽表读取 | $< 20\%$（尤其是单列/少列的聚合计算） |
| **索引可用性** | 存在高区分度的二级索引或覆盖索引 | 无可用索引、低选择性过滤或大跨度范围过滤 |
| **Join 计算形式** | 小表 Lookup Join / 驱动表索引关联 | 大表 Hash Join / 跨节点 MPP Shuffle Join |
| **并发与延迟目标** | 高 QPS（上万）、超低延迟（$< 10\text{ms}$） | 低 QPS（几十~几百）、高吞吐优先（亚秒~秒级） |

---

# 二、底层存储与算力模型差异

两者的区别不只在行存和列存，数据组织与计算方式也不同：

```
+-------------------------------------------------------------+
|                      TiDB Server (CBO)                      |
+------------------------------+------------------------------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
+-----------------------+             +-----------------------+
|      TiKV Cluster     |             |    TiFlash Cluster    |
+-----------------------+             +-----------------------+
|  • RocksDB LSM-Tree   |             |  • DeltaTree 列存     |
|  • 行式物理存储       |             |  • 按列压缩与独立切块 |
|  • Coprocessor 算子   |             |  • MPP 节点间 Shuffle |
|  • B-Tree 索引二分查找|             |  • SIMD 向量化加速    |
+-----------------------+             +-----------------------+
```

### 1. TiKV（行存 + 索引寻道）
- **存储模型**：基于 RocksDB 的 LSM-Tree 行式存储，单行数据的所有字段在物理上紧凑连续存储。
- **计算机制**：利用 Coprocessor 将 `Filter`、`TopN` 及简单聚合算子下推到单个 Region 执行。
- **适用点**：主键或二级索引点查、小范围 Seek 的开销较低。若使用**覆盖索引（Covering Index）**，还能避免回表。

### 2. TiFlash（列存 + MPP 分布式计算）
- **存储模型**：基于针对分析场景自研的 DeltaTree 列式存储引擎，每列数据单独存储并进行高比例压缩。
- **计算机制**：
  - **列投影过滤（Column Projection）**：只读取查询涉及的列，可减少 I/O。
  - **MPP 架构**：TiFlash 节点可通过 Partition/Broadcast Shuffle 完成分布式 Hash Join，避免把大量中间结果集中到单个 TiDB Server。
  - **向量化与 Rough Set**：通过 CPU SIMD 批量计算，并利用数据块的 Min-Max 粗糙集索引跳过无关数据段。

---

# 三、场景判定与特征分析

## 1. 优先走 TiKV 的典型场景

1. **主键、唯一键或高区分度索引点查**
   * **特征**：`WHERE id = 1001` 或 `WHERE uid = 456 AND status = 1`。
* **原因**：索引可以迅速收敛扫描范围；TiFlash 没有面向点查的行级二级索引，通常不适合这类访问。
2. **高频数据写入、更新与删除**
   * **特征**：业务事务中的 `INSERT`、`UPDATE ... WHERE id = ...`。
   * **原因**：TiFlash 是只读的 Raft Learner 副本，事务写入与行锁由 TiKV 的 Raft Leader 协调处理。
3. **宽表全字段投影（`SELECT *`）**
   * **特征**：表包含数十上百列，且业务需要返回该行的所有字段。
* **原因**：列存读取全部列需要重组行，I/O 与内存组装开销会明显上升，未必比行存合适。
4. **覆盖索引查询（Covering Index Scan）**
   * **特征**：SQL 所需的所有列（包括 Filter 和 Select）均包含在联合索引中。
* **原因**：TiKV 可直接扫描索引中已有的数据，避免回表（IndexLookUp）。

---

## 2. 优先走 TiFlash 的典型场景

1. **大宽表统计少量列（Agg & Group By）**
   * **特征**：`SELECT dept_id, SUM(amount), AVG(duration) FROM sales GROUP BY dept_id`。
* **原因**：列存只需扫描计算涉及的列；在宽表上，这通常比读取整行更省 I/O。
2. **缺乏高选择性索引的大范围扫描**
   * **特征**：`WHERE create_time BETWEEN '2025-01-01' AND '2025-12-31'`（涉及数千万行甚至数亿行）。
* **原因**：TiKV 的索引回表可能产生大量随机 I/O，全表扫描的数据量也很大；TiFlash 更擅长列式大范围扫描，并可借助 Min-Max 过滤跳过部分数据块。
3. **海量数据跨表关联（MPP Join）**
   * **特征**：千万级订单事实表与百万级商户/商品维度表关联。
* **原因**：TiFlash MPP 可在存储节点间并行完成 Hash Join，减少大量中间结果回传到 TiDB Server 带来的网络和内存压力。
4. **低 QPS 的重度分析与报表接口**
   * **特征**：后台运营看板、财务月结统计，对 QPS 要求不高，但要求单次查询在亚秒或数秒内完成。

---

# 四、常见排查误区与避坑案例

### 踩坑 1：聚合慢查询就直接用 Hint 强制走 TiFlash
* **典型误区**：只要 SQL 中有 `COUNT(*)`、`SUM()` 且耗时长，就认定应该走 TiFlash。
* **真实案例**：某现货订单表根据单一用户 ID 统计近 30 天未完成订单：
  ```sql
  SELECT COUNT(*) FROM orders WHERE uid = 880192 AND ctime > 1700000000 AND status IN (1, 2);
  ```
  原有索引为 `(uid, status, ctime)`，由于范围条件 `ctime` 在最后，导致前缀 Seek 无法截断，TiKV 扫描了该 UID 下 100 多万条历史索引，耗时 600ms。
  强制走 TiFlash 后，由于 TiFlash 没有 `uid` 二级索引，查询会退化为大范围扫描，甚至触发冷数据远程读取，耗时增加到数秒。
* **正确解法**：单 UID、单租户的聚合点查仍属 OLTP。将 **TiKV 联合索引列顺序** 调整为 `(uid, ctime, status)`，可让前缀条件尽早收敛扫描范围，扫描行数降到百行以内，耗时降至 2ms。

### 踩坑 2：在 TiFlash 上执行 `SELECT *` 导致 OOM
* **典型误区**：只要机器资源足够，TiFlash 就总会比 TiKV 快。
* **后果**：对 60+ 列的大宽表执行 `SELECT *` 并走 TiFlash，需要逐列解压再组装为行，内存占用和 CPU 序列化开销都很大，可能导致 TiFlash 节点或 TiDB Server OOM。
* **做法**：分析查询应遵守 **按需投影（Column Pruning）** 原则，只取需要的列，避免无目的地使用 `SELECT *`。

### 踩坑 3：统计信息过期导致优化器选路失真
* **现象**：业务逻辑没有变化，原本经 TiKV 毫秒级返回的 SQL 突然变慢并转为 TiFlash 全表扫描；也可能是本应使用 TiFlash 的大分析被分配给 TiKV。
* **排查方法**：
  ```sql
  -- 检查表的统计信息健康度
  SHOW STATS_HEALTHY WHERE Table_name = 'orders';

  -- 查看 EXPLAIN 中的预估行数（estRows）与实际扫描行数（actRows）是否偏差过大
  EXPLAIN ANALYZE SELECT ...;
  ```
* **解决办法**：重新收集统计信息并设置合理的自动收集调度：
  ```sql
  ANALYZE TABLE orders;
  ```

---

# 五、执行计划识别与人工控制

### 1. 执行计划（EXPLAIN）关键特征

查看 `EXPLAIN` 时，重点看 **Task** 列和算子名称：

- **走 TiKV 的标志**：
  - Task 列出现 `cop[tikv]` 或 `root`。
  - 算子包含 `Point_Get`、`IndexLookUp`、`IndexRangeScan`、`IndexReader` 等。
- **走 TiFlash 的标志**：
  - Task 列出现 `cop[tiflash]` 或 **`mpp[tiflash]`**。
  - 算子包含 `TableFullScan`（列存块读取）、`ExchangeSender` / `ExchangeReceiver`（MPP 节点间数据分发）。

### 2. 人工控制与 Hint 语法

若统计信息不准或复杂表达式让优化器选路不理想，可用 Hint 指定存储引擎；使用前仍应通过 `EXPLAIN ANALYZE` 验证实际收益：

* **强制指定走 TiFlash**：
  ```sql
  SELECT /*+ READ_FROM_STORAGE(TIFLASH[t1, t2]) */
         dept_id, SUM(amount)
  FROM sales t1
  JOIN department t2 ON t1.dept_id = t2.id
  GROUP BY dept_id;
  ```

* **强制指定走 TiKV**：
  ```sql
  SELECT /*+ READ_FROM_STORAGE(TIKV[orders]) */ *
  FROM orders
  WHERE order_sn = 'SN20260824001';
  ```

* **MPP 模式开关控制**：
  ```sql
  -- 会话级开启 MPP（默认开启）
  SET @@tidb_allow_mpp = ON;

  -- 临时关闭 MPP（降级为单节点 Coprocessor 收集后回传 TiDB 计算）
  SET @@tidb_allow_mpp = OFF;
  ```

---

# 六、选路决策流程图

```
                +------------------------------+
                |     SQL 调优 / 引擎选路决策   |
                +--------------+---------------+
                               |
                               v
                /------------------------------\
               /    单次预估扫描行数规模？      \
              +--------------------------------+
               |                              |
               | < 10^4 行                    | > 10^5 行
               v                              v
    /----------------------\        /----------------------\
   /  是否有高区分度索引？   \      /   查询涉及列占比？     \
  +--------------------------+    +--------------------------+
   |                        |      |                        |
   | 是                     | 否   | 少量列 / 聚合计算      | 大量列 / SELECT *
   v                        v      v                        v
+------------------+   +-------+ +------------------+   +------------------+
|    走 TiKV       |   | 尝试建| |   走 TiFlash     |   | 评估裁剪投影列   |
| 依靠索引极速返回 |   | 覆盖索| | 利用列存+MPP加速 |   | 或改走行存分页   |
+------------------+   +-------+ +------------------+   +------------------+
```

遇到慢查询时，先看扫描规模、索引结构、投影列数和执行计划，再决定是否调整索引、统计信息或引擎。Hint 适合用于验证和处理少数明确的例外，不应替代这些基础排查。
