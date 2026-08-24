---
title: "用 ModelTap 监控 AI 编程工具的 Token 用量与成本"
date: 2026-08-22T11:09:16+08:00
lastmod: 2026-08-24T00:00:00+08:00
categories:
  - "人工智能"
tags:
  - "modeltap"
  - "grafana-cloud"
  - "opentelemetry"
  - "ai-proxy"
keywords: "ModelTap, Grafana Alloy, Grafana Cloud, AI Proxy, Token 监控, 大模型成本, Codex, Claude Code, oh-my-pi, OpenTelemetry, OTLP"
---

使用 Codex、Claude Code、Gemini CLI、Cursor 或 oh-my-pi 写代码时，一次任务通常包含多轮对话、代码库搜索和上下文回溯。只看客户端日志，很难统一回答：到底哪个工具、哪个模型、在哪个时段消耗了多少 Token，花了多少钱？

[ModelTap](https://github.com/tenfyzhong/modeltap) 是一个用 Rust 编写的显式 HTTPS 代理。它在模型 API 的网络边界观测真实发出的请求，从 OpenAI、Anthropic、Gemini、DeepSeek 和 Cursor 流量中解析用量；再把 Token、估算成本和延迟通过 OpenTelemetry（OTLP/HTTP）导出到 Grafana Alloy、Grafana Cloud 或任意兼容后端。

它不需要 SDK、Agent 插件或厂商专有遥测接入。

![ModelTap Grafana 看板：QPS、Token、估算成本和 Agent 分布](https://tenfy.cn/picture/modeltap-grafana-dashboard.jpg)

本文以 macOS/Linux 为主，也给出 Windows、Docker 与常见证书故障的处理方法。

<!-- more -->

# 为什么用 ModelTap

Agent 自带遥测和日志解析器各有用途，但它们都不能像网络层一样，独立于客户端地观察实际离开机器、发往模型服务商的 API 流量。

| 能力 | ModelTap | Agent 原生遥测 | 日志解析器 |
| --- | --- | --- | --- |
| 汇总多个 Agent CLI | 是 | 通常只支持单一 Agent | 不一定 |
| 在 API 网络边界统计用量 | 是 | 取决于 Agent | 否 |
| 需要插件或修改代码 | 否 | 通常需要 | 否 |
| 导出标准 OTLP 指标 | 是 | 不一定 | 不一定 |
| 可与出口代理配合 | 是 | 取决于 Agent | 不适用 |

ModelTap 能提供：

- 按 Agent CLI、站点、模型和 Token 类型拆分的 Token 总量与估算成本；
- 自带 Grafana Dashboard，并支持 `Agent CLI → Site → Model` 级联筛选；
- 面向 Grafana Alloy、Grafana Cloud 等后端的标准 OTLP/HTTP 指标；
- 对 HTTP/1.1、HTTP/2、SSE 与 WebSocket 流式流量的旁路解析；
- 直连或经 HTTP、HTTPS、SOCKS5 出口代理转发。

# 工作方式

## 请求链路

```text
AI 客户端 / CLI
  │  HTTP_PROXY、HTTPS_PROXY 或 PI_PROXY
  ▼
ModelTap 显式代理
  ├─ CONNECT 主机不在 sites 中 ──► 透明隧道 ──► 上游 API
  └─ CONNECT 主机匹配 sites
       │
       ├─ TLS MITM、HTTP/1.1 或 HTTP/2 流式转发 ──► 上游 API
       ├─ SSE / WebSocket / Cursor Connect 旁路解析器
       │    └─ 识别协议并提取模型与 Token 用量
       └─ UsageObserver
            ├─ PriceBook：站点 + 模型 + 当前计费时段
            ├─ 结构化用量日志
            └─ 遥测计数器与延迟直方图
```

`sites` 是流量检查白名单。命中的主机才会使用本地 CA 解密并统计用量；未命中的 CONNECT 隧道保持透明转发。协议由解析器自动识别，不是配置项，也不会成为指标标签。

代理不会等待完整响应体才转发：解析器只读取 SSE 事件、WebSocket 文本帧和 Cursor Connect 消息的副本。因此，客户端响应路径不会因 OTLP 远程写入而阻塞。

## 用量与成本链路

```text
UsageObserver
  │  Token 用量 + 匹配到的价格规则
  ▼
ModelTap OpenTelemetry 指标
  │  OTLP/HTTP POST 到 <telemetry.otlp.endpoint>/v1/metrics
  ▼
Grafana Alloy OTLP 接收器
  │  Prometheus remote_write
  ▼
Grafana Cloud Prometheus ──► Explore 与 ModelTap Dashboard
```

ModelTap 导出累计计数器 `ai_proxy_requests`、`ai_proxy_tokens`、`ai_proxy_cost`，以及代理和遥测延迟直方图。用量指标会按 `site`、`model`、`agent_cli`、Token `type`、`price_period` 和 `currency`（适用时）标记。

# 快速开始

## 1. 安装并启动 ModelTap

### macOS / Linux（Homebrew）

Homebrew 安装会在 `$(brew --prefix)/etc/modeltap/` 创建 `config.yaml` 和 CA 证书：

```bash
# 1. 安装
brew install tenfyzhong/tap/modeltap

# 2. 配置信任根证书，下面的操作系统章节会解释原因
# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain \
  "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"

# Linux
sudo cp "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem" \
  /usr/local/share/ca-certificates/modeltap-ca-cert.crt
sudo update-ca-certificates

# 3. 先校验配置
modeltap validate --config "$(brew --prefix)/etc/modeltap/config.yaml"

# 4. 前台运行
modeltap run --config "$(brew --prefix)/etc/modeltap/config.yaml"

# 或作为后台服务运行
brew services start tenfyzhong/tap/modeltap
```

### Windows（PowerShell）

从 Release 下载预编译二进制文件，或在克隆的仓库内从源码安装。然后生成并信任本地 CA：

```powershell
# 1. 从源码安装（也可改用 Release 二进制文件）
cargo install --path .

# 2. 初始化本地根证书
New-Item -ItemType Directory -Force -Path certs
modeltap ca-init `
  --cert certs\modeltap-ca-cert.pem `
  --key certs\modeltap-ca-key.pem

# 3. 导入到当前用户的受信任根证书存储
Import-Certificate -FilePath .\certs\modeltap-ca-cert.pem -CertStoreLocation Cert:\CurrentUser\Root

# 4. 复制、校验并启动配置
Copy-Item config.sample.yaml config.yaml
modeltap validate --config config.yaml
modeltap run --config config.yaml
```

启动前，请设置遥测端点、出口路由和价格规则。示例配置把默认出口设为 `privoxy`；没有上游代理时，请改成 `egress.default: direct`。

`modeltap validate --config <配置文件>` 会校验 YAML、站点、出口代理和价格规则，但不会绑定监听端口或读取证书文件。项目还提供 Bash、Zsh、Fish 和 PowerShell 补全脚本；Homebrew 安装时会自动安装。

将浏览器、CLI 或 SDK 的 HTTP 代理设为 `http://127.0.0.1:2080`。每个 `hosts` 条目表示一个域根并包含边界正确的子域：例如 `googleapis.com` 会匹配 `generativelanguage.googleapis.com`，但不会匹配 `notgoogleapis.com`。不同站点的重叠域树会被配置校验拒绝。

> **安全提示**：入站代理没有客户端认证。即使监听在 `0.0.0.0:2080`，也不会自动要求密码。非回环监听地址必须额外使用主机防火墙、私有网络或可信访问控制层保护，避免成为开放代理。

# 安装并信任本地 CA

ModelTap 对 `sites` 中的流量执行 TLS MITM，因此客户端必须信任它动态签发的证书。只安装公钥证书，绝不要分发 CA 私钥。

## macOS

可在“钥匙串访问”中将 CA 导入**系统**钥匙串并设为“始终信任”，或执行：

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain \
  "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
```

## Linux

```bash
sudo cp "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem" \
  /usr/local/share/ca-certificates/modeltap-ca-cert.crt
sudo update-ca-certificates
```

## Windows

将 `certs\modeltap-ca-cert.pem` 导入当前用户的“受信任的根证书颁发机构”：

```powershell
# PowerShell
Import-Certificate -FilePath .\certs\modeltap-ca-cert.pem -CertStoreLocation Cert:\CurrentUser\Root

# 或 CMD
certutil -addstore -user Root certs\modeltap-ca-cert.pem
```

Windows 系统应用和 Codex 等使用系统证书存储的 Rust CLI，通常会自动读取该根证书。

# 配置客户端与 Agent

## Node.js CLI

Node.js 默认使用自己的 CA 包，未必信任刚导入到系统的本地根证书。请将 `NODE_EXTRA_CA_CERTS` 指向 ModelTap CA 的绝对路径，再重启 Agent 或后台守护进程。

### macOS / Linux（Bash / Zsh）

```bash
export NODE_EXTRA_CA_CERTS="$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
export HTTP_PROXY=http://127.0.0.1:2080
export HTTPS_PROXY=http://127.0.0.1:2080
export PI_PROXY=http://127.0.0.1:2080
omp
```

### macOS / Linux（Fish）

```fish
set -x NODE_EXTRA_CA_CERTS (brew --prefix)/etc/modeltap/certs/ca-cert.pem
set -x HTTP_PROXY http://127.0.0.1:2080
set -x HTTPS_PROXY http://127.0.0.1:2080
set -x PI_PROXY http://127.0.0.1:2080
omp
```

### Windows（PowerShell）

```powershell
$env:NODE_EXTRA_CA_CERTS = "$pwd\certs\modeltap-ca-cert.pem"
$env:HTTP_PROXY = "http://127.0.0.1:2080"
$env:HTTPS_PROXY = "http://127.0.0.1:2080"
$env:PI_PROXY = "http://127.0.0.1:2080"
omp
```

`PI_PROXY` 会将 oh-my-pi 的所有 Provider 指向 ModelTap；Provider 专用变量会覆盖它。若 Cursor 需要另一条代理路径，使用 `PI_PROXY_CURSOR`。oh-my-pi 的 Cursor Agent 流量使用专用 HTTP/2 传输，所以 Cursor 模型（包括 Grok）必须通过 `PI_PROXY` 或 `PI_PROXY_CURSOR` 才能被 ModelTap 捕获。

## Python 与其他客户端

Python 的 Requests、HTTPX、OpenAI SDK、Anthropic SDK 可显式指定 CA：

```bash
export REQUESTS_CA_BUNDLE="$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
export SSL_CERT_FILE="$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
```

Git 可使用：

```bash
git config --global http.sslCAInfo "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
```

## 作为后台服务运行

Homebrew 安装可直接用 `brew services` 管理：

```bash
brew services start tenfyzhong/tap/modeltap
brew services info tenfyzhong/tap/modeltap
brew services restart tenfyzhong/tap/modeltap
brew services stop tenfyzhong/tap/modeltap
```

未使用 Homebrew 的 Linux 环境可创建 `/etc/systemd/system/modeltap.service`：

```ini
[Unit]
Description=ModelTap AI Traffic Monitor
After=network.target

[Service]
Type=simple
User=modeltap
WorkingDirectory=/opt/modeltap
ExecStart=/opt/modeltap/modeltap run --config /opt/modeltap/config.yaml
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now modeltap
```

Windows 可使用 [NSSM](https://nssm.cc/) 或 [WinSW](https://github.com/winsw/winsw/releases) 将同一条 `modeltap run --config ...` 命令注册为服务；应配置自动重启以及 stdout/stderr 日志文件。

# 配置 ModelTap

首次从源码或 Release 使用时，复制 `config.sample.yaml` 为 `config.yaml`。下面是当前完整示例的核心部分；所有价格均为 USD / 1M Token。

```yaml
proxy:
  listen: 127.0.0.1:2080

logging:
  level: info
  # file: ./logs/modeltap.log

tls:
  ca_cert_file: ./certs/modeltap-ca-cert.pem
  ca_key_file: ./certs/modeltap-ca-key.pem

telemetry:
  otlp:
    endpoint: http://127.0.0.1:4318
    service_name: modeltap-test

egress:
  default: privoxy
  proxies:
    - id: privoxy
      url: http://127.0.0.1:8118

sites:
  - id: openai
    hosts:
      - chatgpt.com
  - id: anthropic
    hosts:
      - anthropic.com
  - id: gemini
    hosts:
      - googleapis.com
  - id: deepseek
    hosts:
      - api.deepseek.com
    egress: direct
  - id: grok
    hosts:
      - api.x.ai
  - id: cursor
    hosts:
      - cursor.sh
      - cursor.com

pricing:
  timezone: Asia/Shanghai
  peak_windows:
    - weekdays: [1, 2, 3, 4, 5]
      start: "09:00"
      end: "12:00"
    - weekdays: [1, 2, 3, 4, 5]
      start: "14:00"
      end: "18:00"
  rules:
    - model: "gpt-5.6-sol*"
      currency: USD
      rates:
        input: 5
        output: 30
        cache_read: 0.5
    - model: "gpt-5.6-terra*"
      currency: USD
      rates:
        input: 2
        output: 12
        cache_read: 0.2
    - model: "gpt-5.6-luna*"
      currency: USD
      rates:
        input: 0.2
        output: 1.2
        cache_read: 0.02
    - model: "claude-opus-4-8*"
      currency: USD
      rates:
        input: 5
        output: 25
        cache_read: 0.5
        cache_write: 6.25
    - model: "claude-sonnet-4-6*"
      currency: USD
      rates:
        input: 3
        output: 15
        cache_read: 0.3
        cache_write: 3.75
    - model: "claude-haiku-4-5*"
      currency: USD
      rates:
        input: 1
        output: 5
        cache_read: 0.1
        cache_write: 1.25
    - model: "gemini-3.7-flash*"
      currency: USD
      rates:
        input: 0.75
        output: 3.75
        cache_read: 0.075
    - model: "deepseek-v4-flash*"
      currency: USD
      peak_windows:
        - weekdays: [1, 2, 3, 4, 5]
          start: "09:00"
          end: "12:00"
        - weekdays: [1, 2, 3, 4, 5]
          start: "14:00"
          end: "18:00"
      peak:
        input: 0.445221684
        output: 1.335665051
        cache_read: 0.014840723
      off_peak:
        input: 0.222610842
        output: 0.667832526
        cache_read: 0.007420361
    - model: "deepseek-v4-pro*"
      currency: USD
      peak_windows:
        - weekdays: [1, 2, 3, 4, 5]
          start: "09:00"
          end: "12:00"
        - weekdays: [1, 2, 3, 4, 5]
          start: "14:00"
          end: "18:00"
      peak:
        input: 1.335665051
        output: 4.006995153
        cache_read: 0.044522168
      off_peak:
        input: 0.667832526
        output: 2.003497577
        cache_read: 0.022261084
    # Cursor 的站点级价格覆盖规则
    - site: cursor
      model: "gpt-5.6-sol-*"
      currency: USD
      rates:
        input: 2.5
        output: 15
        cache_read: 0.25
    - site: cursor
      model: "gpt-5.6-terra-*"
      currency: USD
      rates:
        input: 1.25
        output: 7.5
        cache_read: 0.125
    - site: cursor
      model: "gpt-5.6-luna-*"
      currency: USD
      rates:
        input: 0.5
        output: 3
        cache_read: 0.05
```

Grok 使用 `api.x.ai` 上的 OpenAI 兼容 API，Cursor 使用 `cursor.sh` 与 `cursor.com`。价格规则可以是全局规则（不含 `site`），也可以按 `site` 覆盖。`peak_windows` 可全局定义，也可针对单个模型定义；支持 `weekdays`，可跨越午夜，但同一天的窗口不能重叠。若模型全天同价，使用 `rates` 即可，它可以与给其他模型使用的全局峰谷窗口共存。

## 站点与协议识别

`sites.id` 是指标标签和 `pricing.rules` 中使用的服务身份，应采用实际服务名称，如 `openai`、`grok`、`cursor`。不要配置过去版本中的 `provider`、`provider_type` 或 `mitm` 字段：ModelTap 会自动识别 Cursor Connect/Protobuf、Gemini usage metadata、Anthropic message events 与 OpenAI Chat/Responses。DeepSeek 站点可同时处理 OpenAI 与 Anthropic 兼容流量，无需特殊设置。

Cursor Agent 使用 Connect/Protobuf。ModelTap 从请求中读取所选模型 ID，因此 GPT、Claude、Grok、GLM、Gemini 和 Composer 都无需另建模型白名单。Cursor 只报告生成 Token 的增量；如需成本，配置 `site: cursor` 的价格规则。

`agent_cli` 标签会从稳定的客户端请求头自动推断，可识别 `claude_code`、`codex`、`gemini_cli`、`oh_my_pi`、`opencode`、`pi`、`github_copilot`、`amazon_q`、`roo_code`、`qwen_code`、`factory_droid`、`crush`、`kiro`、`qoder`、`antigravity`、`cursor` 与 `unknown`。Aider、Goose、Continue 等没有稳定专用请求头的工具会保持为 `unknown`，以避免错误分类；原始 User-Agent 永远不会作为指标标签，防止高基数问题。

## 日志

支持 `error`、`warn`、`info`、`debug`、`trace` 五个级别。`info` 会输出每条已解析用量的站点、模型、Token 总量、计费周期和成本。`debug` 还会记录路由决策、响应状态、SSE 识别、WebSocket 帧大小及受限的请求/响应体预览。

设置 `logging.file` 会在保留 stderr 的同时追加写入日志文件；ModelTap 会创建文件，但不会创建父目录。

> **隐私提示**：调试预览每块最多 4 KiB，且不会记录认证头；但 Prompt 和模型回复仍可能出现在日志中。只应在可信环境开启 `debug`。

# 用 Grafana Alloy 写入 Grafana Cloud

Grafana Alloy 通过 OTLP/HTTP 接收 ModelTap 指标，再经 Prometheus Remote Write 发送到 Grafana Cloud。

## 1. 安装 Alloy

macOS：

```bash
brew install grafana/grafana/alloy
brew services start grafana/grafana/alloy
brew services info grafana/grafana/alloy
```

Debian / Ubuntu：

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

RHEL、Fedora、SUSE、Windows、Docker 和 Kubernetes 请参考 [Grafana Alloy 安装指南](https://grafana.com/docs/alloy/latest/set-up/install/)。

## 2. 获取 Grafana Cloud 凭据

1. 在 [Grafana Cloud Portal](https://grafana.com/) 的 **Manage your Grafana Cloud stack** 中点击 **Launch**。

   ![在 Grafana Cloud Portal 启动实例](https://tenfy.cn/picture/modeltap-grafana-cloud-launch.webp)

2. 在 Grafana 侧边栏进入 **Connections → Data sources**，搜索并选择当前堆栈的 Prometheus 数据源。

   ![在 Connections 中查找 Prometheus 数据源](https://tenfy.cn/picture/modeltap-grafana-cloud-datasource-prometheus.webp)

3. 将 **Connection** 下的 Prometheus server URL 填入 `AGENT_USAGE_PROMETHEUS_URL`，将 **Authentication** 下的数字 **User** 填入 `AGENT_USAGE_PROMETHEUS_USERNAME`。

   ![复制 Prometheus URL 与数字 User ID](https://tenfy.cn/picture/modeltap-grafana-cloud-prometheus-connection-user.webp)

4. 在 Portal 的 **Access Policies** 创建或复用包含 `set:alloy-data-write` 权限的策略，点击 **Add token**。把 Token 保存为 `AGENT_USAGE_PROMETHEUS_PASSWORD`。

   ![创建写入权限策略并生成 Token](https://tenfy.cn/picture/modeltap-grafana-cloud-access-policies-token.webp)

> 使用 Prometheus 的数字 User ID，不要使用 Grafana 登录名。Token 不应写进 `config.alloy`、Shell 历史、代码仓库或截图；建议设置过期时间并在到期前轮换。

## 3. 保存凭据

macOS 的 Homebrew Alloy 服务会读取 `$(brew --prefix)/etc/alloy/config.env`：

```bash
export AGENT_USAGE_PROMETHEUS_URL="https://prometheus-REGION.grafana.net/api/prom/push"
export AGENT_USAGE_PROMETHEUS_USERNAME="YOUR_NUMERIC_INSTANCE_ID"
export AGENT_USAGE_PROMETHEUS_PASSWORD="YOUR_ACCESS_POLICY_TOKEN"
```

Debian / Ubuntu 在 `/etc/default/alloy` 写入相同变量，但不带 `export`：

```bash
AGENT_USAGE_PROMETHEUS_URL="https://prometheus-REGION.grafana.net/api/prom/push"
AGENT_USAGE_PROMETHEUS_USERNAME="YOUR_NUMERIC_INSTANCE_ID"
AGENT_USAGE_PROMETHEUS_PASSWORD="YOUR_ACCESS_POLICY_TOKEN"
```

## 4. 配置指标管道

将 macOS 的 `$(brew --prefix)/etc/alloy/config.alloy` 或 Linux 的 `/etc/alloy/config.alloy` 替换为：

```alloy
logging {
  level  = "info"
  format = "logfmt"
}

otelcol.receiver.otlp "agent_usage" {
  http {
    endpoint = "127.0.0.1:4318"
  }
  output {
    metrics = [otelcol.exporter.prometheus.agent_usage.input]
  }
}

otelcol.exporter.prometheus "agent_usage" {
  add_metric_suffixes = false
  forward_to          = [prometheus.remote_write.default.receiver]
}

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

## 5. 校验与验证

```bash
# macOS
alloy validate "$(brew --prefix)/etc/alloy/config.alloy"
brew services restart grafana/grafana/alloy
tail -f "$(brew --prefix)/var/log/alloy.err.log"

# Debian / Ubuntu
sudo alloy validate /etc/alloy/config.alloy
sudo systemctl restart alloy
sudo journalctl -u alloy -f
```

在 `http://127.0.0.1:12345` 确认 Alloy 组件健康。随后通过代理发送一条请求，在 Grafana Cloud 的 **Explore** 中查询 `ai_proxy_requests`。OTLP SDK 会批量导出，指标出现可能有短暂延迟。

宿主机运行 ModelTap 时，保持 `telemetry.otlp.endpoint: http://127.0.0.1:4318`。Docker Desktop 上的 ModelTap 容器访问宿主机 Alloy 时，使用 `http://host.docker.internal:4318`。

# 指标、延迟与 Dashboard

除了累计用量指标，ModelTap 还提供四个延迟直方图：

- `ai_proxy_upstream_first_response_seconds`：请求到达 ModelTap 至上游响应头返回的时间；
- `ai_proxy_processing_duration_microseconds`：请求进入至响应离开 ModelTap 的总处理时间；
- `ai_proxy_local_processing_duration_microseconds`：每个被解析的 HTTP body chunk 或服务端到客户端 WebSocket 帧的本地处理时间，不含上游和 OTLP 导出网络耗时；
- `ai_proxy_telemetry_record_duration_seconds`：记录本地用量指标的耗时。

例如，查询遥测记录耗时的 p95：

```promql
histogram_quantile(0.95,
  sum by (le) (rate(ai_proxy_telemetry_record_duration_seconds_bucket[5m])))
```

按站点查看每块本地处理开销的 p95：

```promql
histogram_quantile(0.95,
  sum by (le, site) (rate(ai_proxy_local_processing_duration_microseconds_bucket[5m])))
```

![带 Agent、站点和模型筛选器的 ModelTap Grafana Dashboard](https://tenfy.cn/picture/modeltap-grafana-dashboard.jpg)

当 `ai_proxy_requests` 已出现在 Explore 中，在 **Dashboards → New → Import** 上传仓库中的 [`grafana/modeltap-dashboard.json`](https://github.com/tenfyzhong/modeltap/blob/main/grafana/modeltap-dashboard.json)，选择同一个 Prometheus 数据源并导入。若 JSON 更新，以相同 Dashboard UID 再次导入即可覆盖旧副本。

看板基于累计计数器，因此第一条导出的用量样本立即可见。变量按 `Agent CLI → Site → Model` 排列，前一项会筛选后一项；`test_client` 与 `benchmark_client` 会从变量和面板查询中排除。面板包括按模型的 QPS、按 `agent_cli` / `site` / `model` / `type` 拆分的 Token 和成本趋势，以及默认折叠的 Performance 行。大 Token 数值会以 K、M、B 缩写，成本以 USD 显示。

# Docker

启动容器前，先在宿主机生成 CA 文件：

```bash
mkdir -p certs
./target/debug/modeltap ca-init \
  --cert certs/modeltap-ca-cert.pem \
  --key certs/modeltap-ca-key.pem
docker compose up --build -d
docker compose logs -f modeltap
```

仓库提供的 Compose 配置将代理绑定到宿主机 2080 端口，以只读方式挂载两份 CA 文件；在 macOS Docker Desktop 上，它通过 `host.docker.internal` 访问宿主机的 GOST（1081）和 Alloy（4318）。客户端只安装 CA 证书，不安装或分发私钥。生产环境应将 CA 私钥存入 Docker Secrets、Kubernetes Secrets 或专用密钥管理服务。

# 常见问题：Codex 证书错误

## `invalid peer certificate: BadSignature`

若 Codex 通过 ModelTap 时提示以下错误：

```text
Falling back from WebSockets to HTTPS transport.
stream disconnected before completion: invalid peer certificate: BadSignature
```

通常是 macOS 系统或登录钥匙串中残留了旧的 `modeltap local CA`，它与当前 ModelTap 使用的私钥不匹配。Codex 读取旧根证书，而动态叶子证书由新私钥签发，验证就会失败。

删除旧证书，重新安装活动 CA，并比对序列号和公钥：

```bash
security delete-certificate -c "modeltap local CA" ~/Library/Keychains/login.keychain-db 2>/dev/null || true
sudo security delete-certificate -c "modeltap local CA" /Library/Keychains/System.keychain 2>/dev/null || true

sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain \
  "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"

security find-certificate -c "modeltap local CA" -p | openssl x509 -noout -serial -pubkey
openssl x509 -in "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem" -noout -serial -pubkey
```

## `invalid peer certificate: UnknownIssuer`

若 Codex 提示 `UnknownIssuer`，则根证书虽然在钥匙串中，但没有正确的根信任策略。例如执行 `security add-trusted-cert -d` 时未使用 `sudo`，导致管理员信任设置没有写入。

推荐以系统级方式重新信任：

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain \
  "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
```

或添加用户级信任（不带 `-d` 和 `sudo`，系统会要求授权）：

```bash
security add-trusted-cert -r trustRoot -k ~/Library/Keychains/login.keychain-db \
  "$(brew --prefix)/etc/modeltap/certs/ca-cert.pem"
```

可检查信任设置：

```bash
security dump-trust-settings -d | grep -A 2 "modeltap local CA" \
  || security dump-trust-settings | grep -A 2 "modeltap local CA"
```

# 安全建议

- 仅拦截有权检查的流量；TLS 解密会让代理进程可见请求和响应内容。
- 限制代理仅服务于可信客户端和网络；不要把无认证代理暴露到公网。
- CA 私钥一旦疑似泄露，应立即更换；至少限制文件权限，例如 `chmod 600`。
- 凭据应保存在环境变量、挂载的 Secret 或密钥管理服务中。
- 永远不要把 API Key、Prompt、回复、请求 ID 或用户 ID 放进指标标签。

# 总结

ModelTap 负责在网络边界提取用量与估算成本，Grafana Alloy 负责接收和转发 OTLP 指标，Grafana Cloud 负责查询、长期保存和可视化。先以本地回环代理、少量站点和基础价格规则跑通链路；确认数据正确后，再扩展价格表、看板和告警。

- GitHub：[tenfyzhong/modeltap](https://github.com/tenfyzhong/modeltap)
- 在线文档：[ModelTap Documentation](https://tenfy.cn/modeltap/)
- Dashboard：[grafana/modeltap-dashboard.json](https://github.com/tenfyzhong/modeltap/blob/main/grafana/modeltap-dashboard.json)
