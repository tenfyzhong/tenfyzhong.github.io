---
title: '实测五款 Go JSON 库：谁才是性能之王？'
date: 2026-01-03T17:24:31+08:00
draft: false
categories:
  - "编程语言"
tags:
  - "golang"
  - "json"
  - "benchmark"
  - "performance"
keywords:
  - Go JSON 性能对比
  - golang json benchmark
  - easyjson
  - go-json
  - json-iterator
---

最近在做一个高并发的 API 服务，JSON 序列化成了性能瓶颈。标准库虽然稳定可靠，但在压测时 CPU 占用居高不下。于是我决定做一次彻底的 JSON 库性能对比，看看市面上这些号称"高性能"的库到底有多少真本事。

<!-- more -->

## 参赛选手

这次对比选了 4 个主流的 JSON 库，外加标准库作为基准：

| 库 | 特点 |
|---|---|
| `encoding/json` | 标准库，稳定可靠，开箱即用 |
| [goccy/go-json](https://github.com/goccy/go-json) | 号称零反射的高性能方案 |
| [json-iterator/go](https://github.com/json-iterator/go) | 滴滴开源，API 兼容标准库 |
| [mailru/easyjson](https://github.com/mailru/easyjson) | 代码生成方案，需要额外构建步骤 |

另外还测试了 [tidwall/pretty](https://github.com/tidwall/pretty) 这个专门做 JSON 格式化的库。

## 测试环境

- Go 1.25.5
- macOS / Apple Silicon (M 系列芯片)
- 8 核 CPU

测试代码在这里：[tenfyzhong/json-benchmark](https://github.com/tenfyzhong/json-benchmark)

## 编码性能：谁序列化最快？

先看编码（Marshal）性能。我准备了两组测试数据：

- **小型结构体**：大约 10 个字段，模拟常见的 API 响应
- **大型结构体**：50+ 个字段，包含嵌套结构，模拟复杂业务对象

### 小型结构体编码

| 排名 | 库 | 耗时 (ns/op) | 内存分配 | 加速比 |
|:---:|---|---:|---:|---:|
| 🥇 | easyjson | 342.60 | 912 B | **3.46x** |
| 🥈 | json-iterator | 383.20 | 1032 B | **3.10x** |
| 🥉 | go-json | 883.10 | 1024 B | **1.34x** |
| 4 | encoding/json | 1187.00 | 1024 B | 1.00x |

### 大型结构体编码

| 排名 | 库 | 耗时 (ns/op) | 内存分配 | 加速比 |
|:---:|---|---:|---:|---:|
| 🥇 | easyjson | 3186 | 3070 B | **3.88x** |
| 🥈 | json-iterator | 3378 | 5277 B | **3.66x** |
| 🥉 | go-json | 7489 | 5270 B | **1.65x** |
| 4 | encoding/json | 12351 | 5273 B | 1.00x |

**结论**：easyjson 和 json-iterator 在编码场景打得难解难分，都能达到标准库 3 倍以上的性能。go-json 表现中规中矩。

## 解码性能：反序列化谁更强？

解码（Unmarshal）通常比编码更复杂，因为涉及到 JSON 解析和类型转换。

### 小型结构体解码

| 排名 | 库 | 耗时 (ns/op) | 内存分配 | 加速比 |
|:---:|---|---:|---:|---:|
| 🥇 | easyjson | 452.20 | 168 B | **3.80x** |
| 🥈 | go-json | 694.60 | 744 B | **2.47x** |
| 🥉 | json-iterator | 1059.00 | 640 B | **1.62x** |
| 4 | encoding/json | 1718.00 | 472 B | 1.00x |

### 大型结构体解码

| 排名 | 库 | 耗时 (ns/op) | 内存分配 | 加速比 |
|:---:|---|---:|---:|---:|
| 🥇 | easyjson | 5362 | 2944 B | **3.07x** |
| 🥈 | go-json | 7071 | 8130 B | **2.32x** |
| 🥉 | json-iterator | 9511 | 7162 B | **1.73x** |
| 4 | encoding/json | 16435 | 3712 B | 1.00x |

**有意思的发现**：在解码场景，go-json 反超了 json-iterator！这说明不同库的优化策略确实不同：json-iterator 更擅长编码，go-json 更擅长解码。

## JSON 格式化：别小看这个场景

如果你的服务需要做 JSON 美化输出（比如调试接口、日志记录），tidwall/pretty 这个专门库值得一看：

### Pretty Print（格式化）

| 场景 | pretty.Pretty | json.Indent | 加速比 |
|---|---:|---:|---:|
| 小型 JSON | 317.1 ns | 894.7 ns | **2.82x** |
| 大型 JSON | 3389 ns | 9883 ns | **2.92x** |

### Compact（压缩）

| 场景 | pretty.Ugly | json.Compact | 加速比 |
|---|---:|---:|---:|
| 小型 JSON | 219.2 ns | 1004 ns | **4.58x** |
| 大型 JSON | 2673 ns | 12475 ns | **4.67x** |

**接近 5 倍的性能提升**，这在需要频繁处理 JSON 格式化的场景非常可观。

## 怎么选？

根据测试结果，我总结了一份选型指南：

### 追求极致性能：选 easyjson

easyjson 在所有场景都是冠军，但代价是需要代码生成：

```bash
# 安装
go install github.com/mailru/easyjson/...@latest

# 生成代码
easyjson -all your_types.go
```

适合场景：

- 高频调用的核心 API
- 对性能有明确要求的服务
- 结构体定义相对稳定

### 想要性能提升又不想改构建流程：选 json-iterator 或 go-json

这两个库都是"即插即用"的，API 兼容标准库：

```go
// json-iterator
import jsoniter "github.com/json-iterator/go"
var json = jsoniter.ConfigCompatibleWithStandardLibrary
json.Marshal(v)

// go-json
import gojson "github.com/goccy/go-json"
gojson.Marshal(v)
```

选择建议：

- 编码多于解码 → json-iterator
- 解码多于编码 → go-json
- 不确定 → 都试试，实测为准

### 只是想让 JSON 输出好看点：选 pretty

```go
import "github.com/tidwall/pretty"

formatted := pretty.Pretty(jsonBytes)
compacted := pretty.Ugly(jsonBytes)
```

## 最后

标准库慢是慢了点，但它的稳定性和兼容性是最好的。如果性能不是瓶颈，用标准库完全没问题。

性能优化这事儿，还是那句老话：**先 profile，再优化**。别为了那点理论上的性能提升把代码搞得一团糟。

完整的测试代码和数据在这里：[tenfyzhong/json-benchmark](https://github.com/tenfyzhong/json-benchmark)
