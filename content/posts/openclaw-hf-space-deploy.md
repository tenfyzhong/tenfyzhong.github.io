---
title: "用 Hugging Face Spaces 部署 OpenClaw（含自动备份与恢复）"
date: 2026-03-25T18:39:18+08:00
categories:
  - "运维"
tags:
  - "openclaw"
  - "hugging face"
  - "hf spaces"
  - "docker"
  - "tutorial"
keywords: "openclaw,hugging face,spaces,docker,backup,restore,sshx"
---

如果你想把 OpenClaw 放到云端，且希望配置尽量少、可恢复、可持续维护，那么 `openclaw-hf` 这个仓库是目前非常省心的方案。

仓库地址：<https://github.com/tenfyzhong/openclaw-hf>

本文基于仓库 README，整理成一套可直接执行的中文部署指南。

<!-- more -->

## 这个方案解决了什么问题

相比手动拼一套 Space + 持久化 + 备份流程，`openclaw-hf` 已经把关键链路封装好了：

- 基于 `ubuntu:24.04` 构建 OpenClaw 容器。
- 直接监听 Hugging Face Space 默认端口 `7860`。
- 支持通过环境变量预置第三方 OpenAI 兼容模型（`base_url + api_key`）。
- 默认把状态放在 `/root/.openclaw`。
- 启动时自动从 HF Dataset 恢复最近备份。
- 通过 `cron` 周期备份到 HF Dataset。
- 内置 `sshx`，方便你进入容器做远程排障或补配置。

## 先注册 Hugging Face 并生成 HF_TOKEN

如果你还没有 Hugging Face 账号，先去注册：<https://huggingface.co/join>

账号准备好后，按下面步骤创建 token（用于脚本配置备份与 Space）：

1. 打开 Hugging Face 的 Token 页面：<https://huggingface.co/settings/tokens>
2. 创建一个新 token（建议命名为 `openclaw-hf`）
3. 权限至少要包含对目标 Space 和 Dataset 的写权限（`write`）
4. 复制 token，形如 `hf_xxx...`

本地可用以下方式登录并校验：

```bash
hf auth login
hf auth whoami
```

`bootstrap-hf.sh` 在提示 `HF_TOKEN for backup dataset` 时：

- 你可以直接粘贴新建的 token
- 也可以留空，让脚本复用当前 `hf auth login` 的本地凭证

## 一键部署（推荐）

仓库已经给了交互式脚本，推荐优先走脚本，不要手搓流程。

### 1. 克隆仓库

```bash
git clone https://github.com/tenfyzhong/openclaw-hf.git
cd openclaw-hf
```

### 2. 运行引导脚本

macOS / Linux：

```bash
./scripts/bootstrap-hf.sh
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy ByPass -File .\scripts\bootstrap-hf.ps1
```

脚本会自动完成：

- 检查并安装 `hf` CLI。
- 检查 Hugging Face 登录状态（需要时触发 `hf auth login`）。
- 创建 Space 和备份 Dataset。
- 上传当前仓库内容到 Space。
- 自动配置 Variables 和 Secrets。
- 可选：重启 Space。

## 使用 Agent 自动部署（推荐给不想手动点配置的用户）

`openclaw-hf` README 提供了 Agent 专用的标准提示词，你可以把下面这段直接发给 AI Agent：

```text
Please deploy OpenClaw to Hugging Face by strictly following the "Agent Deployment SOP (Collapsed)" section in https://github.com/tenfyzhong/openclaw-hf/blob/main/README.md
```

Agent 按 README SOP 通常会做这些事：

1. 先检查依赖（`git`、`hf`、`python3`、`huggingface_hub`）
2. 按固定顺序向你收集部署参数
3. 调用 `bootstrap-hf.sh` / `bootstrap-hf.ps1` 执行部署
4. 最后返回 Space 地址、Health 地址、版本号，以及自动生成的网关凭证（如果有）

如果你希望一次性把参数给全，可以直接发这个模板给 Agent：

```text
space_name: openclaw-hf
dataset_name: openclaw-hf-backup
openclaw_version: latest
gateway_token: <留空自动生成或手动填写>
gateway_password: <留空自动生成或手动填写>
hf_token: <你的HF_TOKEN，或留空复用本地登录>
configure_custom_llm: no
restart_space_after_deploy: yes
```

## 部署前准备

脚本依赖以下命令：

```bash
git --version
hf version
python3 --version
```

还需要 Python 包：

```bash
python3 -c "import huggingface_hub" >/dev/null 2>&1 || \
  python3 -m pip install --user 'huggingface_hub[cli]'
```

## 关键变量与密钥

在 Space 的 `Settings -> Variables and secrets` 中，至少要有：

- Variable: `OPENCLAW_BACKUP_DATASET_REPO`（格式：`username/dataset-name`）
- Secret: `HF_TOKEN`（需要对备份 Dataset 有写权限）
- Secret: `OPENCLAW_GATEWAY_TOKEN`
- Secret: `OPENCLAW_GATEWAY_PASSWORD`

如果你使用 `bootstrap-hf.sh` / `bootstrap-hf.ps1`，这些会自动配置。

### 可选：预置 LLM（三项必须同时提供）

- `OPENCLAW_LLM_BASE_URL`
- `OPENCLAW_LLM_MODEL`
- `OPENCLAW_LLM_API_KEY`

只填其中 1-2 项不会生效，入口脚本会跳过模型预配置。

## 脚本会问你哪些问题

按 README 的流程，主要是这些输入：

1. `space_name`（默认 `openclaw-hf`）
2. `dataset_name`（默认 `<space_name>-backup`）
3. `OPENCLAW_VERSION`（默认自动探测最新版本）
4. `OPENCLAW_GATEWAY_TOKEN`（可留空自动生成）
5. `OPENCLAW_GATEWAY_PASSWORD`（可留空自动生成）
6. `HF_TOKEN`（可留空，复用本地已登录 token）
7. 是否立即配置 LLM
8. 是否在结尾重启 Space

如果 token/password 由脚本自动生成，它会在结束时打印出来，请及时保存。

## 部署完成后如何验证

假设你的 Space repo 是 `<owner>/<space_name>`，访问地址是：

- 应用地址：`https://<owner>-<space_name>.hf.space`
- 健康检查：`https://<owner>-<space_name>.hf.space/healthz`

例如：

```bash
SPACE_ID="yourname/openclaw-hf"
SPACE_HOST="${SPACE_ID/\//-}.hf.space"
echo "https://${SPACE_HOST}/healthz"
```

## 备份与恢复机制（这个方案的核心）

`openclaw-hf` 的数据生命周期大致如下：

- 启动恢复：容器启动时尝试从 Dataset 拉取 `latest-backup.tar.gz` 并恢复。
- 定时备份：根据 `OPENCLAW_BACKUP_CRON` 定时上传备份。
- 退出兜底：容器收到停止信号时，再执行一次最终备份。
- 保留策略：只保留最近 `OPENCLAW_BACKUP_KEEP_COUNT` 个带时间戳归档。

默认值里，`OPENCLAW_BACKUP_CRON` 是每 30 分钟一次，`OPENCLAW_BACKUP_KEEP_COUNT` 是 `48`。

## Keep-Alive 与 24/7 运行建议

README 对这点讲得很明确：

- 免费 `cpu-basic` 会休眠（通常约 48 小时无访问后）。
- 真正 24/7 需要付费硬件，并将 `Sleep time` 设为 `Never`。
- 私有 Space 做健康检查要带 `Authorization: Bearer <HF_TOKEN>`，否则会看到 404（正常权限行为）。

如果你只是减少冷启动概率，可以定时请求 `/healthz`；但在免费层这不是绝对常驻保证。

### 使用 cron-job.org 做保活（实操）

如果你不想自己维护服务器定时任务，可以用 <https://cron-job.org/>。

根据 cron-job.org 官方 FAQ（<https://cron-job.org/faq/>），它支持自定义 Header、支持 HTTPS、最小可到每分钟一次调用。对于 OpenClaw Space，通常每 10-15 分钟 ping 一次就够了。

#### 1. 创建 cron-job.org 账号并新建任务

1. 打开 <https://cron-job.org/> 并注册/登录（控制台在 `console.cron-job.org`）
2. 新建一个 HTTP cron job
3. URL 填你的健康检查地址：`https://<owner>-<space_name>.hf.space/healthz`
4. Method 选 `GET`
5. 调度建议选每 10-15 分钟一次（不要过于激进，遵守 fair usage）

#### 2. 私有 Space 必配 Authorization Header

如果你的 Space 是私有的，在任务 Header 中添加：

```text
Authorization: Bearer <HF_TOKEN>
```

建议不要直接复用备份链路的高权限 `HF_TOKEN`，而是专门创建一个用于保活的低权限 token（仅满足访问该 Space 的最小权限），降低泄露风险。

#### 3. 启用失败通知并先做一次 Test Run

创建任务后，建议立即执行一次测试并确认返回成功，然后开启失败告警（邮件通知），方便你第一时间发现 Space 无法访问或 token 过期。

#### 4. 预期效果说明

- 这个方法能显著降低冷启动概率。
- 对免费硬件，它是“尽量保持活跃”的策略，不是官方保证的 24/7 常驻。
- 如果业务要求严格在线，请使用付费硬件并将 `Sleep time` 设为 `Never`。

## sshx 用法（可选）

仓库镜像已预装 `sshx`。

启用自动启动：

```bash
OPENCLAW_SSHX_AUTO_START=true
```

或进入容器手动执行：

```bash
sshx
```

结束后建议及时清理进程：

```bash
pgrep -fa sshx
pkill -TERM -f '(^|/)sshx($| )'
```

## 总结

如果你的目标是“在 Hugging Face 上快速跑起来一个可恢复的 OpenClaw 实例”，`openclaw-hf` 这套方案已经覆盖了部署、配置、备份、恢复、保活和远程调试这些关键环节。

建议直接使用仓库自带的 `bootstrap-hf` 脚本，先跑通默认配置，再按需叠加 LLM 与保活策略。
