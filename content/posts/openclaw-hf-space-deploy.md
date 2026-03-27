---
title: "用 Hugging Face Spaces 部署 OpenClaw（含自动备份与恢复）"
date: 2026-03-25T21:39:18+08:00
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

如果你想把 OpenClaw 放到云端，且希望配置尽量少、可恢复、可持续维护，那么 `openclaw-hf` 是目前非常省心的一套方案。

仓库地址：<https://github.com/tenfyzhong/openclaw-hf>

本文已按该仓库最新 `README.md`（2026-03-27 更新）同步整理为中文部署指南。

<!-- more -->

## 这个方案解决了什么问题

相比手动拼一套 Space + 持久化 + 备份流程，`openclaw-hf` 已经把关键链路封装好了：

- 基于 `ubuntu:24.04` 构建 OpenClaw 容器。
- 直接监听 Hugging Face Space 默认端口 `7860`。
- 支持通过环境变量预置第三方 OpenAI 兼容模型（`base_url + api_key`）。
- 默认把状态放在 `/root/.openclaw`。
- 启动时自动从 HF Dataset 恢复最近备份。
- 通过 `cron` 周期备份到 HF Dataset。
- 镜像内预装 `vim`、`opencode`、`codex`、`claude` 和 `sshx`，方便容器内排障与交互。

## 先注册 Hugging Face 并生成 HF_TOKEN

如果你还没有 Hugging Face 账号，先去注册：<https://huggingface.co/join>

账号准备好后，按下面步骤创建 token（用于脚本配置备份与 Space）：

![](https://tenfy.cn/picture/create-new-hf-access-token.png)

1. 打开 Hugging Face Token 页面：<https://huggingface.co/settings/tokens>
2. 创建一个新 token（建议命名为 `deploy-openclaw`）
3. 至少授予 `write` 权限
4. 复制 token（形如 `hf_xxx...`）

本地可先登录并校验：

```bash
hf auth login
hf auth whoami
```

`bootstrap-hf.sh` 提示 `HF_TOKEN for backup dataset` 时：

- 可以直接粘贴新建 token
- 也可以留空，让脚本复用当前 `hf auth login` 的本地凭证

## 一键部署（推荐）

仓库已提供交互式脚本，建议优先走脚本，不要手搓流程。

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

- 检查并安装 `hf` CLI（如缺失）。
- 检查 Hugging Face 登录状态（需要时触发 `hf auth login`）。
- 询问并确认部署参数（包含一次最终 `Proceed with these settings?` 确认）。
- 创建私有 Space 与私有备份 Dataset，并上传当前仓库到 Space。
- 自动写入 Variables / Secrets（含备份、网关凭据等）。
- 默认写入安全相关变量：
  - `OPENCLAW_GATEWAY_CONTROLUI_ALLOW_INSECURE_AUTH=false`
  - `OPENCLAW_GATEWAY_CONTROLUI_DANGEROUSLY_DISABLE_DEVICE_AUTH=false`

如下图：

![](https://tenfy.cn/picture/20260327110552830.png)

## 使用 Agent 自动部署（适合不想手动点配置的用户）

`openclaw-hf` README 提供了 Agent 专用提示词，你可以直接发给 AI Agent：

```text
Please deploy OpenClaw to Hugging Face by strictly following the "Agent Deployment SOP (Collapsed)" section in https://github.com/tenfyzhong/openclaw-hf/blob/main/README.md
```

Agent 按 README SOP 通常会做这些事：

1. 先检查依赖（`git`、`hf`、`python3`、`huggingface_hub`）
2. 按固定顺序向你收集部署参数
3. 调用 `bootstrap-hf.sh` / `bootstrap-hf.ps1` 执行部署
4. 回传 Space / Dataset / App / Health 地址与版本信息
5. 如果网关凭据是自动生成的，也会一并回传

如果你希望一次性把参数给全，可以发这个模板给 Agent：

```text
space_name: openclaw-hf
dataset_name: openclaw-hf-backup
openclaw_version: latest
gateway_token: <留空自动生成或手动填写>
gateway_password: <留空自动生成或手动填写>
hf_token: <你的 HF_TOKEN，或留空复用本地登录>
configure_custom_llm: no
openclaw_sshx_auto_start: true
proceed_with_settings: yes
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
- Secret: `OPENCLAW_GATEWAY_TOKEN`（推荐）
- Secret: `OPENCLAW_GATEWAY_PASSWORD`（可选）

如果你使用 `bootstrap-hf.sh` / `bootstrap-hf.ps1`，以上会自动配置。

### 可选：预置 LLM（三项必须同时提供）

- `OPENCLAW_LLM_BASE_URL`
- `OPENCLAW_LLM_MODEL`
- `OPENCLAW_LLM_API_KEY`

只填其中 1-2 项不会生效，入口脚本会跳过模型预配置。

### 常见可选变量

- `OPENCLAW_VERSION`（默认自动探测 npm 最新版本，失败回退 `latest`）
- `OPENCLAW_BACKUP_CRON`（默认 `*/30 * * * *`）
- `OPENCLAW_BACKUP_KEEP_COUNT`（默认 `48`）
- `OPENCLAW_SSHX_AUTO_START`（默认 `false`，需要自动起 `sshx` 时设为 `true`）

## 脚本会问你哪些问题

按 README 流程，主要输入如下：

1. `space_name`（默认 `openclaw-hf`）
2. `dataset_name`（默认 `<space_name>-backup`）
3. `OPENCLAW_VERSION`（默认自动探测最新版本）
4. `OPENCLAW_GATEWAY_TOKEN`（可留空自动生成）
5. `OPENCLAW_GATEWAY_PASSWORD`（可留空自动生成）
6. `HF_TOKEN`（可留空，复用本地已登录 token）
7. 是否立即配置 LLM（三项全填才生效）
8. 如果不配 LLM，是否把 `OPENCLAW_SSHX_AUTO_START` 设为 `true`
9. 最终确认：`Proceed with these settings?`（选 `no` 会退出，不做远端变更）

如果 token/password 由脚本自动生成，会在结束时打印出来，请及时保存。

## 部署完成后如何验证

假设 Space repo 是 `<owner>/<space_name>`，可用地址如下：

- Space 页面：`https://huggingface.co/spaces/<owner>/<space_name>`
- 应用地址：`https://<owner>-<space_name>.hf.space`
- 健康检查：`https://<owner>-<space_name>.hf.space/healthz`

例如：

```bash
SPACE_ID="yourname/openclaw-hf"
SPACE_HOST="${SPACE_ID/\//-}.hf.space"
echo "https://${SPACE_HOST}/healthz"
```

## 如何进行 OpenClaw 首次配置

1. 打开 Hugging Face Space 页面，进入容器日志，找到 `sshx` 输出的临时访问链接。
2. 在浏览器打开该链接进入容器 shell，执行 `openclaw onboard` 按引导完成配置。
3. onboarding 过程中 OpenClaw 可能重启，`sshx` 链接也可能变化；若当前链接失效，回到日志获取新链接继续执行。
4. 官方向导可参考：<https://docs.openclaw.ai/start/wizard>
5. 配置完成后，记得回到 `Settings -> Variables and secrets`，将 `OPENCLAW_SSHX_AUTO_START` 改为 `false`（或删除该变量），然后重启 Space，把 `sshx` 关闭。

如果你修改了 OpenClaw 配置并希望立即生效，可以重启对应进程（示例）：

```bash
ps -ef | grep 'openclaw-gateway' | grep -v 'grep' | awk '{print $2}' | xargs -I{} kill {}
```

## 备份与恢复机制（核心能力）

`openclaw-hf` 的数据生命周期如下：

- 启动恢复：容器启动时尝试从 Dataset 拉取 `latest-backup.tar.gz` 并恢复。
- 定时备份：根据 `OPENCLAW_BACKUP_CRON` 周期上传。
- 退出兜底：容器收到停止信号时再做一次最终备份。
- 产物包含：
  - `backups/openclaw-backup-<timestamp>.tar.gz`
  - `latest-backup.tar.gz`
  - `latest-backup.json`
- 保留策略：只保留最近 `OPENCLAW_BACKUP_KEEP_COUNT` 个时间戳归档（默认 `48`）。

## Keep-Alive 与 24/7 运行建议

README 的结论很明确：

- 免费 `cpu-basic` 会休眠（当前一般约 48 小时无访问后）。
- 严格 24/7 需要付费硬件，并把 `Sleep time` 设为 `Never`。
- 私有 Space 做健康检查必须带 `Authorization: Bearer <HF_TOKEN>`，否则会看到 404（正常权限行为）。

如果你只是减少冷启动概率，可以定时请求 `/healthz`；但在免费层这不是官方保证的常驻方案。

### 使用 cron-job.org 做保活（实操）

如果你不想自己维护定时任务，可以用 <https://cron-job.org/>。

根据其官方 FAQ（<https://cron-job.org/faq/>），支持自定义 Header、HTTPS，以及最高每分钟一次调用。对 OpenClaw Space 来说，每 10-15 分钟 ping 一次通常就够。

#### 1. 创建任务

1. 打开 <https://cron-job.org/> 并注册/登录（控制台在 `console.cron-job.org`）
2. 新建 HTTP cron job
3. URL 填：`https://<owner>-<space_name>.hf.space/healthz`
4. Method 选 `GET`
5. 调度建议每 10-15 分钟一次

#### 2. 私有 Space 添加 Header

```text
Authorization: Bearer <HF_TOKEN>
```

建议单独创建一个仅用于保活的低权限 token，不要复用高权限备份 token。

#### 3. 先做 Test Run 再开告警

创建任务后先手动测试一次，再启用失败通知（邮件等），方便第一时间发现 Space 不可用或 token 过期。

## sshx 用法（可选）

镜像已预装 `sshx`（以及 `vim`、`opencode`、`codex`、`claude`）。

1. 自动启动（环境变量）：

```bash
OPENCLAW_SSHX_AUTO_START=true
```

2. 容器内手动启动：

```bash
sshx
```

3. 让 OpenClaw 终端后台启动：

```bash
nohup sshx >/proc/1/fd/1 2>/proc/1/fd/2 &
```

后续如果临时需要 `sshx`，也可以通过 IM 让 OpenClaw 启动一个；使用完成后，记得再通过 IM 让 OpenClaw 把 `sshx` 关掉。

使用结束后建议及时清理：

```bash
pgrep -fa sshx
pkill -TERM -f '(^|/)sshx($| )'
```

## 总结

如果你的目标是“在 Hugging Face 上快速跑起来一个可恢复的 OpenClaw 实例”，`openclaw-hf` 已经覆盖了部署、配置、备份、恢复、保活和远程调试这些关键环节。

建议优先使用仓库自带的 `bootstrap-hf` 脚本先跑通默认配置，再按需叠加 LLM、保活和 `sshx` 策略。
