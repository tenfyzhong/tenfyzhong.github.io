---
title: "ModelTap 实战指南：透明监控 AI 编程 Agent Token 消耗与成本，结合 Grafana Alloy 与 Grafana Cloud 搭建可观测大盘"
date: 2026-08-22T11:09:16+08:00
categories:
  - "人工智能"
  - "工具"
tags:
  - "modeltap"
  - "grafana-cloud"
  - "grafana-alloy"
  - "opentelemetry"
  - "ai-proxy"
  - "cursor"
  - "claude-code"
  - "oh-my-pi"
keywords: "ModelTap, Grafana Alloy, Grafana Cloud, AI Proxy, Token 监控, 大模型成本, Cursor, Claude Code, oh-my-pi, OpenTelemetry, OTLP"
---

在日常使用各种 AI Coding Agent（如 Claude Code、Cursor、Codex、oh-my-pi、Gemini CLI、OpenCode 等）进行软件开发时，多轮对话、上下文回溯、代码库搜索与子任务规划往往会在不知不觉中消耗惊人数量的 Token。

但在这个过程中，很多开发者都会遇到类似的困扰：

1. **消耗不透明**：刚才跑完的一个复杂重构任务到底消耗了多少 Prompt Token 和 Completion Token？Prompt 缓存（Cache Read / Cache Write）到底命中了多少？
2. **成本难以核算**：今天调用不同厂商的大模型（OpenAI、Anthropic、Gemini、DeepSeek 等）一共花了多少钱？DeepSeek 这类区分高峰期与低谷期分时计价的模型，实际费用如何精准折算？
3. **缺乏统一大盘**：不同工具、不同 SDK 各自为政，没有一个统一、集中且低开销的可观测看板来跟踪日常调用趋势、模型分布与代理延迟。

为了解决这些问题，[ModelTap](https://github.com/tenfyzhong/modeltap) 应运而生。它是一个采用 Rust 开发的高性能显式 HTTP/HTTPS 代理与 AI 用量监控工具。通过无侵入的 TLS MITM 嗅探与流式旁路解析，ModelTap 能自动识别主流大模型协议并计算实时成本，再通过标准 OpenTelemetry（OTLP/HTTP）将指标推送给 Grafana Alloy 并汇聚到 Grafana Cloud 中，从而构建起一套完整的 AI 模型用量与成本可观测大盘。

本文将从零开始，详细介绍 ModelTap 的工作原理、安装部署、CA 根证书配置、Grafana Alloy 管道搭建以及 Grafana Cloud 大盘的导入与实战使用。

<!-- more -->

# ModelTap 的核心特性与工作架构

ModelTap 的设计原则是**透明、零缓冲、低开销与高精度**。它在保证客户端流式体验不受影响的前提下，完成所有指标的采集与计算。

## 核心特性

- **零缓冲流式转发 (Zero-Buffering Streaming)**：支持 HTTP/1.1 与 HTTP/2。对于 SSE（Server-Sent Events）流式响应与长连接 WebSocket（如 Codex 使用的 `chatgpt.com` 端点），ModelTap 采用流式直通转发，不等待完整响应包体；针对 WebSocket 握手开启的 `permessage-deflate` 压缩，仅在旁路解压并提取 `response.completed` 事件中的 Token 数据，原数据流原样无损传递。
- **自动协议识别 (Automatic Protocol Detection)**：内部自动识别 OpenAI Chat/Responses/Embeddings、Anthropic Messages、Google Gemini metadata、DeepSeek（同时兼容 OpenAI 与 Anthropic 格式）以及 Cursor Connect/Protobuf 协议，无需手动为每个站点配置冗余的协议类型。
- **Agent CLI 智能识别**：自动根据请求头嗅探客户端来源，打上 `claude_code`、`codex`、`gemini_cli`、`oh_my_pi`、`opencode` 或 `unknown` 的 `agent_cli` 标签。
- **灵活的计费引擎 (Pricing Engine)**：支持基于百万 Token 的精确定价规则，覆盖 Input、Output、Cache Read 与 Cache Write。支持时区感知的峰谷阶梯时段（`peak_windows`），完美适配 DeepSeek 等国内模型的北京时间分时计费规则。
- **级联出口代理 (Egress Cascading)**：支持上游级联代理（HTTP、HTTPS、SOCKS5、Privoxy、GOST 等），并允许针对特定站点进行路由覆盖（例如 DeepSeek 走直连 `direct`，其他流量走 Privoxy）。
- **标准 OpenTelemetry 导出**：提供 `ai_proxy_requests`、`ai_proxy_tokens`、`ai_proxy_cost` 以及多维度的微秒级代理延迟直方图，通过 OTLP/HTTP 异步批量导出。

## 整体架构与数据流

整个系统的调用流与度量数据流如下图所示：

```text
AI 客户端 / CLI (Claude Code / Cursor / oh-my-pi / SDK)
  │  配置 HTTP_PROXY, HTTPS_PROXY, PI_PROXY = http://127.0.0.1:2080
  ▼
ModelTap 显式代理 (Rust)
  ├─ 目标 Host 不在 sites 白名单 ──► 透明隧道转发 ──► 上游 API
  └─ 目标 Host 匹配 sites 配置
       │
       ├─ TLS MITM 解密 (本地根证书) & 流式转发 ────────► 上游 API (或 Egress 级联代理)
       ├─ 旁路流式解析器 (SSE / WebSocket / Cursor Connect)
       │    └─ 提取 model 与 token 用量 (input / output / cache_read / cache_write)
       └─ UsageObserver
            ├─ PriceBook: 匹配 site + model + 当前时段费率 ──► 计算精确花费
            ├─ 结构化用量日志输出
            └─ OpenTelemetry 内存计数器 / 延迟直方图
                 │
                 │  OTLP/HTTP (POST /v1/metrics)
                 ▼
Grafana Alloy (本地 OTLP 接收器: 127.0.0.1:4318)
  │  otelcol.receiver.otlp ──► otelcol.exporter.prometheus
  │  prometheus.remote_write (带 Basic Auth 鉴权)
  ▼
Grafana Cloud (Prometheus 托管存储)
  │
  ▼
Grafana Dashboard (可视化大盘：请求数、Token 消耗、费用、延迟)
```

---

# 第一步：安装与配置 ModelTap

## 1. 安装 ModelTap

你可以通过以下几种方式获取并安装 ModelTap：

### 方式 A：通过 Homebrew 安装（macOS / Linux）

如果你在 macOS 或 Linux 上使用 Homebrew，可以直接通过官方 Tap 安装：

```bash
brew install tenfyzhong/tap/modeltap
```

### 方式 B：从 GitHub Release 下载预编译二进制文件

访问 [ModelTap Releases](https://github.com/tenfyzhong/modeltap/releases) 页面，下载对应平台的归档包并解压到 `PATH` 路径下：

- `modeltap-<version>-aarch64-apple-darwin.tar.gz`（macOS Apple Silicon）
- `modeltap-<version>-x86_64-unknown-linux-gnu.tar.gz`（Linux x86_64）
- `modeltap-<version>-aarch64-unknown-linux-gnu.tar.gz`（Linux ARM64）

### 方式 C：从源码编译

机器上安装有 Rust 工具链时，可直接编译：

```bash
git clone https://github.com/tenfyzhong/modeltap.git
cd modeltap
make build
# 编译产物位于 target/debug/modeltap 或 target/release/modeltap
```

### 方式 D：通过 Docker / Docker Compose 运行

仓库中提供了现成的 `Dockerfile` 与 `docker-compose.yml`，可以直接容器化部署：

```bash
docker compose up --build -d
```

## 2. 生成本地 Root CA 根证书

ModelTap 只会对你在配置文件 `sites` 列表中显式指定的域名进行 TLS MITM 解密，其余域名保持纯透明隧道转发。为了让客户端信任 ModelTap 动态签发的证书，首先需要生成一对专用的本地根证书与私钥：

```bash
mkdir -p certs
modeltap ca-init \
  --cert certs/modeltap-ca-cert.pem \
  --key certs/modeltap-ca-key.pem
```

> **安全提示**：生成的私钥 `modeltap-ca-key.pem` 属于高敏感机密，绝对不要共享、上传或提交到代码仓库中；客户端只需安装和信任公钥证书 `modeltap-ca-cert.pem`。

## 3. 在客户端中信任根证书

### macOS 系统信任

在 macOS 上，双击 `certs/modeltap-ca-cert.pem` 打开“钥匙串访问”（Keychain Access），将其导入到 **系统**（System）钥匙串中，并双击证书设置其信任策略为 **始终信任**（Always Trust）。

### Node.js 客户端环境（重点）

许多现代 AI 工具（如 `oh-my-pi`、`Claude Code` 等）运行在 Node.js 环境下。Node.js 默认内置了自己的 CA 证书列表，不一定会直接读取系统的信任根证书。

因此，在启动这些客户端之前，需要通过环境变量 `NODE_EXTRA_CA_CERTS` 指定 ModelTap 的 CA 证书绝对路径：

```bash
export NODE_EXTRA_CA_CERTS="$(pwd)/certs/modeltap-ca-cert.pem"
export HTTP_PROXY=http://127.0.0.1:2080
export HTTPS_PROXY=http://127.0.0.1:2080
```

### 快速验证 MITM 转发链路

使用 `curl` 命令发送一条测试请求：

```bash
curl --proxy http://127.0.0.1:2080 \
  --cacert certs/modeltap-ca-cert.pem \
  https://api.openai.com/v1/models
```

如果返回 OpenAI 的 `401 Unauthorized`（因为没有带实际的 API Key），即证明代理、TLS MITM 解密与上游转发链路完全正常！

## 4. 编写配置文件 `config.yaml`

复制仓库中的 `config.sample.yaml` 并根据自身环境调整：

```bash
cp config.sample.yaml config.yaml
```

一份典型的生产/开发配置示例如下：

```yaml
proxy:
  listen: 127.0.0.1:2080

logging:
  level: info
  # 如需持久化日志，可取消注释并指定路径
  # file: ./logs/modeltap.log

tls:
  ca_cert_file: ./certs/modeltap-ca-cert.pem
  ca_key_file: ./certs/modeltap-ca-key.pem

telemetry:
  otlp:
    endpoint: http://127.0.0.1:4318
    service_name: modeltap-prod

egress:
  default: privoxy
  proxies:
    - id: privoxy
      url: http://127.0.0.1:8118

sites:
  - id: openai
    hosts:
      - chatgpt.com
      - openai.com
  - id: anthropic
    hosts:
      - anthropic.com
  - id: gemini
    hosts:
      - googleapis.com
  - id: deepseek
    hosts:
      - api.deepseek.com
    egress: direct # DeepSeek 直连，不走 Privoxy
  - id: grok
    hosts:
      - api.x.ai
  - id: cursor
    hosts:
      - cursor.sh
      - cursor.com
      - api2.cursor.sh

pricing:
  timezone: Asia/Shanghai
  peak_windows:
    - start: "09:00"
      end: "12:00"
    - start: "14:00"
      end: "18:00"
  rules:
    # OpenAI 模型单价示例 (USD / 1M Tokens)
    - site: openai
      model: "gpt-5.6-sol*"
      currency: USD
      rates:
        input: 5.0
        output: 30.0
        cache_read: 0.5

    # Anthropic Claude 模型单价示例
    - site: anthropic
      model: "claude-sonnet-4-6*"
      currency: USD
      rates:
        input: 3.0
        output: 15.0
        cache_read: 0.3
        cache_write: 3.75

    # Google Gemini 模型单价示例
    - site: gemini
      model: "gemini-3.7-flash*"
      currency: USD
      rates:
        input: 0.75
        output: 3.75
        cache_read: 0.075

    # DeepSeek 区分峰谷时段定价示例
    - site: deepseek
      model: "deepseek-v4-flash*"
      currency: USD
      peak:
        input: 0.4452
        output: 1.3356
        cache_read: 0.0148
      off_peak:
        input: 0.2226
        output: 0.6678
        cache_read: 0.0074
```

### 配置检查与启动

ModelTap 提供了非常实用的语法与规则静态校验命令，无需启动端口即可检验配置合法性：

```bash
# 验证配置文件正确性
modeltap validate --config config.yaml

# 启动 ModelTap 代理
modeltap run --config config.yaml
```

---

# 第二步：安装与配置 Grafana Alloy

[Grafana Alloy](https://grafana.com/docs/alloy/latest/) 是 Grafana 官方推出的 OpenTelemetry 采集与管道处理代理。我们将用 Alloy 接收 ModelTap 发出的 OTLP/HTTP 指标，并通过 `remote_write` 将指标无缝推送到 Grafana Cloud 托管的 Prometheus 中。

## 1. 安装 Grafana Alloy

### macOS (Homebrew)

```bash
brew install grafana/grafana/alloy
brew services start grafana/grafana/alloy
```

### Linux (Debian / Ubuntu)

```bash
sudo apt-get install -y gpg wget
sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/grafana.asc https://apt.grafana.com/gpg-full.key
sudo chmod 644 /etc/apt/keyrings/grafana.asc
echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" \
  | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y alloy
sudo systemctl enable --now alloy
```

## 2. 获取 Grafana Cloud Prometheus 凭据

1. 登录 [Grafana Cloud Portal](https://grafana.com/)，找到你创建的 Stack。
2. 在 **Prometheus** 卡片上点击 **Details**：
   - 记录 **Remote Write Endpoint**（格式形如 `https://prometheus-prod-XX-prod-XX.grafana.net/api/prom/push`）。
   - 记录 **Instance ID / Username**（这是一串数字，例如 `1234567`，注意不是你的 Grafana 登录邮箱）。
3. 前往 **Access Policies** 页面，创建一个只包含 `metrics:write` 最小权限的策略（Policy），并为其生成一个 Token，将其作为密码保存。

## 3. 安全配置环境变量

为了避免将敏感 Token 硬编码在配置文件中，建议使用环境变量注入：

### macOS 环境

编辑 `$(brew --prefix)/etc/alloy/config.env` 文件（Homebrew 启动的 Alloy 服务会自动载入该文件）：

```bash
export AGENT_USAGE_PROMETHEUS_URL="https://prometheus-prod-XX.grafana.net/api/prom/push"
export AGENT_USAGE_PROMETHEUS_USERNAME="YOUR_NUMERIC_INSTANCE_ID"
export AGENT_USAGE_PROMETHEUS_PASSWORD="YOUR_GRAFANA_ACCESS_TOKEN"
```

### Linux 环境

编辑 `/etc/default/alloy`：

```bash
AGENT_USAGE_PROMETHEUS_URL="https://prometheus-prod-XX.grafana.net/api/prom/push"
AGENT_USAGE_PROMETHEUS_USERNAME="YOUR_NUMERIC_INSTANCE_ID"
AGENT_USAGE_PROMETHEUS_PASSWORD="YOUR_GRAFANA_ACCESS_TOKEN"
```

## 4. 编写 Alloy 管道配置 (`config.alloy`)

修改 Alloy 的配置文件（macOS 位于 `$(brew --prefix)/etc/alloy/config.alloy`，Linux 位于 `/etc/alloy/config.alloy`）：

```alloy
logging {
  level  = "info"
  format = "logfmt"
}

// 1. 启动 OTLP/HTTP 接收器，监听本地 4318 端口
otelcol.receiver.otlp "agent_usage" {
  http {
    endpoint = "127.0.0.1:4318"
  }
  output {
    metrics = [otelcol.exporter.prometheus.agent_usage.input]
  }
}

// 2. 将 OTLP 指标格式转换为 Prometheus 指标格式
otelcol.exporter.prometheus "agent_usage" {
  add_metric_suffixes = false
  forward_to          = [prometheus.remote_write.default.receiver]
}

// 3. 通过 remote_write 推送至 Grafana Cloud Prometheus
prometheus.remote_write "default" {
  endpoint {
    url = sys.env("AGENT_USAGE_PROMETHEUS_URL")

    basic_auth {
      username = sys.env("AGENT_USAGE_PROMETHEUS_USERNAME")
      password = sys.env("AGENT_USAGE_PROMETHEUS_PASSWORD")
    }
  }
}
```

## 5. 校验并重启 Alloy 服务

配置完成后，使用 Alloy CLI 校验配置文件，并重启服务：

```bash
# macOS
alloy validate "$(brew --prefix)/etc/alloy/config.alloy"
brew services restart grafana/grafana/alloy
tail -f "$(brew --prefix)/var/log/alloy.err.log"

# Linux
sudo alloy validate /etc/alloy/config.alloy
sudo systemctl restart alloy
sudo journalctl -u alloy -f
```

打开浏览器访问 `http://127.0.0.1:12345`，可以进入 Alloy 的 Web 状态页面，确认 `otelcol.receiver.otlp.agent_usage` 和 `prometheus.remote_write.default` 各组件均处于运行健康的绿色状态。

---

# 第三步：Grafana Cloud 大盘导入与监控实战

## 1. 验证指标上报

启动 ModelTap 并向代理发送几条请求后，打开 Grafana Cloud 的 **Explore** 页面，切换到对应的 Prometheus 数据源，查询以下指标：

- `ai_proxy_requests`：累计请求总数
- `ai_proxy_tokens`：累计消耗的 Token 计数器
- `ai_proxy_cost`：累计消耗的成本（USD）

如果能正常查到数据序列，说明从 ModelTap 到 Grafana Cloud 的全链路已经完全连通！

## 2. 导入官方预置 Dashboard

ModelTap 仓库在 `grafana/modeltap-dashboard.json` 中内置了经过精心调优的可视化大盘，包含请求聚合、Token 细分、费用核算与延迟分析等全套视图。

导入步骤非常简单：

1. 在 Grafana Cloud 左侧导航栏点击 **Dashboards** -> **New** -> **Import**。
2. 上传 ModelTap 仓库中的 `grafana/modeltap-dashboard.json` 文件（或者复制 JSON 内容粘贴到文本框）。
3. 在底部的 **Prometheus** 下拉框中，选择你刚刚推送指标的 Grafana Cloud Prometheus 数据源。
4. 点击 **Import** 即可完成创建。

## 3. 大盘看板深度解读

导入后，你将获得一个全功能的多维度大盘：

1. **顶部核心概览指标卡 (Stat Cards)**：
   - **Cumulative requests**：累计请求次数。
   - **Total tokens in selected range**：当前选定时间范围内的总 Token 消耗增量。
   - **Cost in selected range (USD)**：当前时间范围内的总花费金额。
2. **多维分布与消耗趋势 (Timeseries Charts)**：
   - **Cumulative requests by model**：按模型细分的请求增长曲线。
   - **Cumulative tokens by agent_cli, site, model, and type**：细分到具体的 Agent 工具（如 `oh_my_pi` vs `claude_code`）、站点服务商、模型名称以及 Token 类型（`input`、`output`、`cache_read`、`cache_write`）。
   - **Cumulative cost by agent_cli, site, model, and type**：各模型各维度的费用累计走势。
3. **模型费用明细表 (Cost Table)**：
   - **Cost by model in selected range (USD)**：以表格形式展示选定区间内消耗最高的前几名模型及其具体成本。
4. **级联筛选变量 (Cascading Template Variables)**：
   - 顶部提供 `Agent CLI -> Site -> Model` 级联选择器。选择特定的 Agent 后，站点和模型下拉列表会自动进行联动过滤，方便快速排查单个工具或单个模型的调用情况。
5. **性能与代理开销看板 (Latency & Overhead)**：
   - **Upstream first response latency**：监控从 ModelTap 接收请求到上游 API 返回首包 Header 的耗时。
   - **ai_proxy_local_processing_duration_microseconds**：监控 ModelTap 本地解析分块（Chunk）与记录遥测指标的微秒级开销（通常 p95 耗时仅在微秒级别），证明代理不会对流式交互带来任何可感知的延迟。

---

# 第四步：各 AI 客户端与 Agent CLI 的配置实战

配置完代理与监控后，只需要将客户端流量导向 ModelTap 即可。

## 1. 通用环境变量配置

在终端环境中，直接导出标准代理变量：

```bash
export NODE_EXTRA_CA_CERTS="/path/to/certs/modeltap-ca-cert.pem"
export HTTP_PROXY="http://127.0.0.1:2080"
export HTTPS_PROXY="http://127.0.0.1:2080"
```

## 2. oh-my-pi 接入

[oh-my-pi](https://github.com/canis-aur/oh-my-pi) 支持统一的代理变量 `PI_PROXY`。设置后，所有 AI Provider 都会通过 ModelTap：

```bash
export NODE_EXTRA_CA_CERTS="/path/to/certs/modeltap-ca-cert.pem"
export PI_PROXY="http://127.0.0.1:2080"

# 如果使用 Fish Shell
# set -x NODE_EXTRA_CA_CERTS /path/to/certs/modeltap-ca-cert.pem
# set -x PI_PROXY http://127.0.0.1:2080

omp
```

> **提示**：oh-my-pi 针对 Cursor Agent 采用了专用的 HTTP/2 传输通道。通过设置 `PI_PROXY`（或专用的 `PI_PROXY_CURSOR=http://127.0.0.1:2080`），可以确保 Cursor 后端模型（包括 Grok 等）也能准确被 ModelTap 捕获并记录用量。

## 3. Claude Code / Codex / Gemini CLI 接入

对于其他主流 CLI 工具，只需在同一 Shell 会话下设置好上述代理变量和 `NODE_EXTRA_CA_CERTS`，直接启动 CLI 工具即可自动享受用量与成本的透明监控。

---

# 安全建议与生产实践

1. **保护好 CA 根证书私钥**：`modeltap-ca-key.pem` 拥有动态签发解密流量证书的能力，务必限制该文件的系统读取权限（例如 `chmod 600`），切勿将其存放在共享目录或代码仓库中。
2. **避免运行公网开放代理**：默认配置下 `proxy.listen` 为 `127.0.0.1:2080`。如果需要监听非本地地址（如 `0.0.0.0:2080`），请务必在主机防火墙或 VPC 网络层限制来源 IP，防止被扫描器利用。
3. **敏感信息保护**：ModelTap 的指标设计遵循严格的数据保护原则，所有 Metric Label 均不包含 API Key、Prompt 文本、User ID 等隐私数据。在开启 `logging.level: debug` 时，请仅在受信任的本地调试环境中使用。

---

# 总结

通过 **ModelTap + Grafana Alloy + Grafana Cloud** 的组合，我们以极低的性能开销和完全透明的方式，搭建起了一套专属于开发者的 AI 模型可观测体系：

- **ModelTap**：专注于高效、零缓冲地抓取和解析流量，精准核算 Token 与成本；
- **Grafana Alloy**：充当可靠的本地 OpenTelemetry 收集与转发管道；
- **Grafana Cloud**：提供稳定免运维的时序存储与丰富的多维可视化看板。

无论你是重度使用 AI 辅助编程的开发者，还是希望对团队大模型 API 消耗进行精细化成本管控的工程师，ModelTap 都是一个轻量、优雅且功能强大的选择。

- **GitHub 仓库**：[https://github.com/tenfyzhong/modeltap](https://github.com/tenfyzhong/modeltap)
- **在线文档与 Alloy 指南**：[ModelTap Documentation](https://github.com/tenfyzhong/modeltap/tree/main/docs)

欢迎体验并给项目点个 Star！如果在配置过程中有任何问题，也欢迎在仓库中提交 Issue 或 PR 参与建设。
