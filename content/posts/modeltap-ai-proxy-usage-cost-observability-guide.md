---
title: "用 ModelTap 监控 AI 编程工具的 Token 用量与成本"
date: 2026-08-22T11:09:16+08:00
categories:
  - "人工智能"
tags:
  - "modeltap"
  - "grafana-cloud"
  - "grafana-alloy"
  - "opentelemetry"
keywords: "ModelTap, Grafana Alloy, Grafana Cloud, AI Proxy, Token 监控, 大模型成本, Cursor, Claude Code, oh-my-pi, OpenTelemetry, OTLP"
---

使用 Claude Code、Cursor、Codex、oh-my-pi、Gemini CLI 或 OpenCode 写代码时，一次任务往往会包含多轮对话、代码库搜索和上下文回溯。Token 用量很容易超过预期。

我主要想弄清楚三件事：

1. 一次任务分别用了多少输入、输出和缓存 Token？
2. 不同厂商和模型的费用累计是多少？对 DeepSeek 这类分时计价模型，费用如何计算？
3. 能否把不同 CLI 和 SDK 的用量放到同一个看板里，同时看到代理延迟？

这篇文章用 [ModelTap](https://github.com/tenfyzhong/modeltap) 处理这些问题。它是用 Rust 写的显式 HTTP/HTTPS 代理，能从常见模型 API 的响应中提取用量信息，并按配置的价格规则计算成本。指标通过 OpenTelemetry（OTLP/HTTP）发送给 Grafana Alloy，再写入 Grafana Cloud。

下面依次说明代理的工作方式、根证书配置、Alloy 管道，以及 Grafana Cloud 看板的导入。

<!-- more -->

# ModelTap 的工作方式

ModelTap 将流量转发与用量解析分开处理：客户端的数据流继续转发，解析器从旁路读取需要的信息并记录指标。

## 主要特性

- **流式转发**：支持 HTTP/1.1、HTTP/2、SSE 和 WebSocket。响应不会等到完整包体到齐再转发。对启用了 `permessage-deflate` 的 WebSocket，ModelTap 在旁路解压后读取 `response.completed` 事件中的 Token 数据。
- **协议识别**：可识别 OpenAI Chat、Responses 和 Embeddings，Anthropic Messages、Google Gemini metadata、DeepSeek 的 OpenAI/Anthropic 格式，以及 Cursor Connect/Protobuf。
- **CLI 来源标签**：按请求头标记 `claude_code`、`codex`、`gemini_cli`、`oh_my_pi`、`opencode` 或 `unknown`。
- **计费规则**：按每百万 Token 配置 input、output、cache read 和 cache write 的价格；`peak_windows` 可用于按时区设置峰谷价格。
- **上游代理**：可配置 HTTP、HTTPS、SOCKS5、Privoxy 或 GOST 等出口代理，并按站点覆盖路由。
- **OpenTelemetry 指标**：通过 OTLP/HTTP 导出 `ai_proxy_requests`、`ai_proxy_tokens`、`ai_proxy_cost` 和代理延迟直方图。

## 整体架构与数据流

调用流和指标流如下：

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

可按自己的环境选择安装方式：

### 方式 A：通过 Homebrew 安装（macOS / Linux）

macOS 或 Linux 上使用 Homebrew 时：

```bash
brew install tenfyzhong/tap/modeltap
```

### 方式 B：从 GitHub Release 下载预编译二进制文件

从 [ModelTap Releases](https://github.com/tenfyzhong/modeltap/releases) 下载对应平台的归档包，解压后把可执行文件放到 `PATH` 中：

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

仓库提供了 `Dockerfile` 与 `docker-compose.yml`：

```bash
docker compose up --build -d
```

## 2. 生成本地 Root CA 根证书

ModelTap 只会解密 `sites` 中列出的域名；其他域名仍按隧道转发。客户端要信任代理动态签发的证书，先生成一套本地根证书和私钥：

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

如果得到 OpenAI 的 `401 Unauthorized`，说明请求已通过代理完成 TLS 解密并到达上游；这里没有携带 API Key，返回 401 是预期结果。

## 4. 编写配置文件 `config.yaml`

复制仓库中的示例配置，再按自己的网络环境修改：

```bash
cp config.sample.yaml config.yaml
```

示例：

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

先检查配置，再启动代理：

```bash
# 验证配置文件正确性
modeltap validate --config config.yaml

# 启动 ModelTap 代理
modeltap run --config config.yaml
```

---

# 第二步：安装与配置 Grafana Alloy

[Grafana Alloy](https://grafana.com/docs/alloy/latest/) 负责接收 ModelTap 的 OTLP/HTTP 指标，并用 `remote_write` 写入 Grafana Cloud 托管的 Prometheus。

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

需要准备 Prometheus Remote Write 地址、用户名（Instance ID）和有写入权限的 Access Policy Token：

1. 打开 [Grafana Cloud Portal](https://grafana.com/)，在 **Manage your Grafana Cloud stack** 下点击 **Launch** 打开你的 Grafana 实例：

   ![打开 Grafana Cloud 并点击 Launch](https://tenfy.cn/picture/modeltap-grafana-cloud-launch.webp)

2. 进入 Grafana 后，在左侧导航菜单找到 **Connections** -> **Data sources**，搜索 `prometheus`，并点击进入 Prometheus 数据源详情：

   ![在 Connections 中查找 Prometheus 数据源](https://tenfy.cn/picture/modeltap-grafana-cloud-datasource-prometheus.webp)

3. 复制 **Connection** 下的 **Prometheus server URL**，作为 Alloy 的 `config.env` 中的 `AGENT_USAGE_PROMETHEUS_URL`；复制 **Authentication** 下的 **User**（数字 ID），作为 Alloy 的 `config.env` 中的 `AGENT_USAGE_PROMETHEUS_USERNAME`：

   ![复制 Prometheus server URL 与 User](https://tenfy.cn/picture/modeltap-grafana-cloud-prometheus-connection-user.webp)

4. 返回 Grafana Cloud Portal，在 **SECURITY** 的 **Access Policies** 中创建或复用包含 `set:alloy-data-write` 权限的策略。点击 **Add token** 生成 Token，保存为 Alloy `config.env` 的 `AGENT_USAGE_PROMETHEUS_PASSWORD`：

   ![在 Access Policies 中创建 Token](https://tenfy.cn/picture/modeltap-grafana-cloud-access-policies-token.webp)

## 3. 安全配置环境变量

不要把 Token 写进 `config.alloy`，用环境变量传入：

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

打开 `http://127.0.0.1:12345`，在 Alloy 状态页确认 `otelcol.receiver.otlp.agent_usage` 和 `prometheus.remote_write.default` 正常运行。

---

# 第三步：导入 Grafana Cloud 看板并查看指标

## 1. 验证指标上报

启动 ModelTap 并向代理发送几条请求后，打开 Grafana Cloud 的 **Explore** 页面，切换到对应的 Prometheus 数据源，查询以下指标：

- `ai_proxy_requests`：累计请求总数
- `ai_proxy_tokens`：累计消耗的 Token 计数器
- `ai_proxy_cost`：累计消耗的成本（USD）

能查到这些时间序列，说明数据已从 ModelTap 写入 Grafana Cloud。

## 2. 导入官方预置 Dashboard

ModelTap 仓库的 `grafana/modeltap-dashboard.json` 包含请求、Token、费用和延迟视图。

导入步骤：

1. 在 Grafana Cloud 左侧导航栏点击 **Dashboards** -> **New** -> **Import**。
2. 上传 ModelTap 仓库中的 `grafana/modeltap-dashboard.json` 文件（或者复制 JSON 内容粘贴到文本框）。
3. 在底部的 **Prometheus** 下拉框中，选择你刚刚推送指标的 Grafana Cloud Prometheus 数据源。
4. 点击 **Import**。

## 3. 看板内容

看板包含以下内容：

1. **顶部核心概览指标卡 (Stat Cards)**：
   - **Cumulative requests**：累计请求数。
   - **Total tokens in selected range**：所选时间范围内的 Token 增量。
   - **Cost in selected range (USD)**：所选时间范围内的费用。
2. **多维分布与消耗趋势 (Timeseries Charts)**：
   - **Cumulative requests by model**：按模型细分的请求增长曲线。
   - **Cumulative tokens by agent_cli, site, model, and type**：按 Agent 工具、服务商、模型和 Token 类型（`input`、`output`、`cache_read`、`cache_write`）拆分。
   - **Cumulative cost by agent_cli, site, model, and type**：按相同维度拆分的费用曲线。
3. **模型费用明细表 (Cost Table)**：
   - **Cost by model in selected range (USD)**：列出所选时间范围内各模型的费用。
4. **级联筛选变量 (Cascading Template Variables)**：
   - 顶部提供 `Agent CLI -> Site -> Model` 选择器；选定 Agent 后，站点和模型列表会相应过滤。
5. **性能与代理开销看板 (Latency & Overhead)**：
   - **Upstream first response latency**：监控从 ModelTap 接收请求到上游 API 返回首包 Header 的耗时。
   - **ai_proxy_local_processing_duration_microseconds**：记录 ModelTap 解析分块和写入遥测指标的本地耗时。可结合 p95 观察代理处理对交互的影响。

---

# 第四步：配置 AI 客户端与 Agent CLI

配置好代理和监控后，把客户端流量指向 ModelTap。

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

其他 CLI 工具也在同一 Shell 会话中设置代理变量和 `NODE_EXTRA_CA_CERTS` 后启动即可。

---

# 安全建议与生产实践

1. **保护好 CA 根证书私钥**：`modeltap-ca-key.pem` 拥有动态签发解密流量证书的能力，务必限制该文件的系统读取权限（例如 `chmod 600`），切勿将其存放在共享目录或代码仓库中。
2. **避免运行公网开放代理**：默认配置下 `proxy.listen` 为 `127.0.0.1:2080`。如果需要监听非本地地址（如 `0.0.0.0:2080`），请务必在主机防火墙或 VPC 网络层限制来源 IP，防止被扫描器利用。
3. **敏感信息保护**：ModelTap 的指标设计遵循严格的数据保护原则，所有 Metric Label 均不包含 API Key、Prompt 文本、User ID 等隐私数据。在开启 `logging.level: debug` 时，请仅在受信任的本地调试环境中使用。

---

# 总结

这套组合的职责比较清晰：

- **ModelTap** 代理请求、提取用量并计算成本；
- **Grafana Alloy** 接收并转发 OpenTelemetry 指标；
- **Grafana Cloud** 存储指标并提供查询和看板。

如果你需要按模型、CLI 或 Token 类型查看 AI 编程工具的用量，可以先从本地代理和一组基础价格规则开始。确认数据流正常后，再补充看板变量和告警规则。

- **GitHub 仓库**：[https://github.com/tenfyzhong/modeltap](https://github.com/tenfyzhong/modeltap)
- **在线文档与 Alloy 指南**：[ModelTap Documentation](https://github.com/tenfyzhong/modeltap/tree/main/docs)

遇到配置问题可在仓库提交 Issue；改进文档或功能也欢迎提交 PR。
