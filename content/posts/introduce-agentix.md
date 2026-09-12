---
title: "Agentix：把本地 Codex、Claude Code、Pi 接入 Telegram/飞书/Slack，随时随地掌控 AI 编程"
date: 2026-09-12T17:35:00+08:00
categories:
  - "人工智能"
tags:
  - "agentix"
  - "codex"
  - "claude-code"
  - "rust"
keywords: "Agentix, taskix, Codex, Claude Code, Pi, Oh My Pi, Telegram Bot, 飞书机器人, Slack Bot, AI 编程, 远程控制, 异步协同, Obsidian"
---

随着 OpenAI Codex CLI、Anthropic Claude Code、Pi 和 Oh My Pi 等本地 AI 编程 Agent 的流行，很多开发者的日常工作流已经变成了：“给 Agent 一个目标，让它去阅读代码库、规划方案、编写代码、跑测试并修复问题”。

但这也带来了新的困扰：一个复杂的重构或排错任务，Agent 往往需要自主执行几分钟甚至更久。当你离开工位去吃饭、开会、通勤或躺在沙发上休息时：
- **无法掌握进度**：想知道 Agent 跑完了没有，只能干等回电脑前；
- **阻塞在权限审批**：Agent 遇到高危操作或多选提问（Tool Approval / Clarification）时会暂停执行，原地等待用户确认，白白浪费时间；
- **手机 SSH 体验极差**：小屏幕上敲终端命令、滚动长日志，体验非常痛苦；
- **云端托管方案存在隐私与环境断层**：云端 Agent 既碰不到本地内网和未提交的代码，又存在 API 凭据和代码外泄的风险。

为了彻底解决这个痛点，我开发了 **[Agentix](https://github.com/tenfyzhong/agentix)** —— 一个用 Rust 编写的 Local-First 跨平台桥接工具，能将本地运行的 Codex、Claude Code、Pi 和 Oh My Pi 会话无缝接入 **Telegram**、**飞书（Feishu/Lark）** 或 **Slack**。

<!-- more -->

所有的代码、凭据、进程和日志**100% 留在你的本地电脑**，你只需要通过手机或随身的聊天软件，就能随时随地查看流式输出、下发 Prompt、批准操作、管理任务进度。

---

## 为什么选择 Agentix？

市面上也有一些远程控制或聊天桥接方案，但 Agentix 从第一天起就是围绕**本地 AI Coding Agent 的真实开发痛点**深度定制的。

| 核心维度 | Agentix | 传统 SSH / 手机终端 | 云端托管 Agent SaaS |
| :--- | :--- | :--- | :--- |
| **数据与代码隐私** | **100% 本地运行**，无任何第三方云端转发 | 本地运行 | 代码与凭据需上传云端 |
| **移动端交互体验** | **原生 IM 富文本卡片**，单卡片流式刷新，一键按键审批 | 终端乱码、小屏幕排版差、无交互按钮 | 网页/App 体验参差不齐 |
| **多 Agent 兼容** | **Codex、Claude Code、Pi、Oh My Pi** 全面支持 | 需手动 attach 各自终端 | 仅支持单一厂商模型 |
| **防串线与状态管理** | 严格的单会话绑定、Draining 排水机制、重启持久化 | 多个 tmux 窗口容易混淆 | 依赖云端会话管理 |
| **任务系统联动** | 内置 **taskix** 与 **Obsidian 双向看板** 协同 | 无 | 平台内置封闭任务板 |
| **性能与资源开销** | **纯 Rust 打造**，亚毫秒级路由，极低 CPU/内存占用 | 低 | 取决于云端服务稳定性 |

---

## 核心功能与技术亮点

### 1. 多 Agent 后端深度打通

Agentix 不仅仅是简单地转发终端输入输出，而是针对各个 Agent 的内部机制做了原生协议级适配：

- **OpenAI Codex**：通过 Managed App-Server 代理模式直连，支持 FIFO 队列（`/queue`，在 Agent 执行中无缝追加后续指令）、动态模型切换（`/model`）与思考深度调节（`/reasoning`）。
- **Anthropic Claude Code**：通过官方 Plugin 机制 + `rmux`/`tmux` 终端桥接，自动捕获终端草稿与 Hook 回调，无需依赖受限的第三方代理或破坏原有终端体验。
- **Pi & Oh My Pi (OMP)**：通过高性能 Socket Bridge 插件，原终端进程与 IM 实时互通，支持随时 `/detach` 脱离而不中断终端后台运行。

```text
  ┌────────────────────────────────────────────────────────┐
  │                   Your Local Machine                   │
  │                                                        │
  │   ┌──────────────┐   ┌──────────────┐   ┌──────────┐   │
  │   │  Codex CLI   │   │ Claude Code  │   │  Pi/OMP  │   │
  │   └──────┬───────┘   └──────┬───────┘   └────┬─────┘   │
  │          │ App-Server       │ Plugin+rmux    │ Bridge  │
  │          ▼                  ▼                ▼         │
  │  ┌──────────────────────────────────────────────────┐  │
  │  │                  Agentix (Rust)                  │  │
  │  │   • Strict Invariant Engine  • Durable State     │  │
  │  │   • Outbound View Renderer   • Taskix Engine     │  │
  │  └──────────────────────────┬───────────────────────┘  │
  └─────────────────────────────┼──────────────────────────┘
                                │ WebSocket / OpenAPI / Bot API
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
   ┌───────────┐          ┌───────────┐          ┌───────────┐
   │ Telegram  │          │  Feishu   │          │   Slack   │
   └───────────┘          └───────────┘          └───────────┘
```

---

### 2. 专为 IM 打造的极致交互体验

在聊天软件里看 AI 写代码，最怕被成百上千条流式消息刷屏。Agentix 针对不同平台进行了针对性渲染：

- **单 Turn 原地卡片刷新（In-Place Update）**：每个回合（Turn）对应一条独立的消息/卡片。Agentix 会在节流控制下原地编辑更新消息内容，既保证了流式输出的实时性，又不会产生消息刷屏。
- **动态运行计时 ⏱️**：
  - Telegram 每 5 秒刷新一次；
  - 飞书每 1 秒刷新一次；
  - Slack 每 2 秒刷新一次；
  即使 Agent 在深度思考没有文字吐出，卡片状态也会实时跳动耗时，让你清晰知道它正在全力运算。
- **语义化状态颜色**：
  - 🔵 **运行中**（蓝色 + 实时耗时）
  - 🟠 **等待审批 / 警告**（橙色）
  - 🟢 **执行成功**（绿色）
  - 🟣 **后台会话完成**（紫色）
  - 🔴 **执行异常 / 失败**（红色）
- **一键交互式审批（Interactive Approval）**：当 Agent 请求执行高危 Shell 命令或修改文件时，IM 卡片会弹出独立的不透明单次 Token 按钮，点击即可直接 `Approve` 或 `Reject`。遇到多选 Clarification 提问时，不仅支持选项点击，还支持 `Other…` 自由文本回复。

---

### 3. 严谨的并发模型：零串线与优雅后台通知

在多会话、多终端并发的场景下，最容易出现“消息发错窗口”、“旧任务输出冲掉新任务卡片”的问题。Agentix 设计了极其严密的并发状态机：

- **严格单激活不变式**：一个 IM 对话在同一时刻至多绑定一个激活会话；一个 Agent 会话在同一时刻至多在一个 IM 对话中处于激活状态。
- **Draining（排水）机制**：在 Agent 跑长任务时切换到新会话，旧会话会自动进入 Draining 状态。繁杂的流式 Delta 输出会被静默抑制，只有当任务彻底完成、或者触发了关键的人工审批时，才会向你推送带有后台标识（Purple Card）的卡片，并附带一键 Attach 切回按钮。
- **断线重连与重启恢复**：Agentix 服务重启或本地 Agent 进程异常退出恢复后，所有绑定的会话关系、运行中的状态卡片均会自动重新订阅与恢复，无需重新配置。

---

### 4. 不止聊天：内置 Taskix 与 Obsidian 双向任务看板

如果只是单轮问答，IM 桥接就够了；但真实的工程研发往往需要**多任务拆解与长期追踪**。

Agentix 内置了独立的任务管理子系统 **`taskix`**（基于 SQLite WAL 本地数据库）：

- **Project → Job → Task 三层状态机**：支持从需求池（Inbox）到 Job 规划，再到具体 Task 的两阶段（Planning → Executing）生命周期与依赖 DAG 校验。
- **IM 随时录入需求**：在聊天窗口发送 `/inbox 重构用户认证模块支持 OAuth2`，自动追加进项目的待办需求池。
- **Obsidian 完美联动**：执行 `taskix obsidian setup` 即可自动配置 Obsidian TaskNotes 插件。你在 Obsidian 笔记中打勾 `- [x]`、新建 Checkbox 或修改任务描述，状态会在后台毫秒级与 Agentix 数据库双向同步；若校验失败还会自动回滚，保持数据绝对一致。
- **任务验收与提审（Review Policy）**：Agent 完成全部 Task 后，Job 会进入 `PENDING_REVIEW` 状态，由你在 IM 或 Obsidian 中确认验收通过后才算正式交付。

---

## 快速上手

### 1. 安装

#### macOS / Linux（推荐 Homebrew）

```sh
brew tap tenfyzhong/tap
brew install agentix
```

> 如果需要独立使用任务看板，也可以单独安装 `taskix`：`brew install tenfyzhong/tap/taskix`。

#### Windows

从 [GitHub Releases](https://github.com/tenfyzhong/agentix/releases/latest) 下载预编译的 `agentix-<version>-x86_64-pc-windows-msvc.zip` 解压并加入 `PATH` 即可。

---

### 2. 初始化配置

以 macOS / Linux 为例，生成配置文件：

```sh
mkdir -p ~/.config/agentix
cp "$(brew --prefix agentix)/share/agentix/agentix.example.toml" ~/.config/agentix/config.toml
chmod 600 ~/.config/agentix/config.toml
```

编辑 `~/.config/agentix/config.toml`，按需开启你的 Agent 后端和 IM 平台：

```toml
# 1. 启用 Agent 后端（可同时启用多个）
[agent.codex]

[agent.claude]
command = "claude"
session_dir = "~/.claude/projects"

# 2. 配置 IM 通道（telegram / feishu / slack 三选一）
[channel]
kind = "feishu" # 或 "telegram" / "slack"

[channel.feishu]
app_id = "cli_a1b2c3d4e5"
app_secret = "your_app_secret"
# 首次运行 owner_ids 留空，通过 /claim 认领
owner_ids = []
```

---

### 3. 启动与认领

启动 Agentix 服务：

```sh
agentix serve
```

在另一个终端生成认证 Claim 码：

```sh
agentix client claim
```

将终端打印出的 `/claim <code>` 指令发送给你在 Telegram / 飞书 / Slack 中创建的 Bot，即可完成主人身份绑定。后续任何其他人向 Bot 发送消息都会被默认拒绝（Default Deny），安全无忧。

---

### 4. 日常使用姿势

1. **本地开工**：在电脑上正常启动 Codex、Claude Code 或 Pi 开启写代码会话；
2. **出门前连接**：在 IM 窗口向 Bot 发送 `/sessions`，点击对应会话的 **Attach** 按钮；
3. **随身掌控**：
   - 直接向 Bot 发送文字，即可作为 Prompt 驱动 Agent；
   - 收到审批提示，点击 Inline Button 一键确认；
   - 发送 `/stop` 随时中断当前正在执行的 Turn；
   - 发送 `/history` 翻阅历史对话；
   - 发送 `/queue` 查看 Codex 待执行的追问队列；
   - 使用 `/rmux` 或 `/tmux` 直接在远程新建终端会话！

---

## 总结

在 AI 辅助编程越来越智能的今天，限制我们的不再是写代码的速度，而是**人与 Agent 之间的协同延迟**。

有了 Agentix：
- 复杂的重构任务，你可以下发指令后放心合上电脑去吃饭；
- 遇到审批卡点，手机收到一条飞书/TG卡片，顺手点一下“允许”；
- 路上有了新灵感，直接发一段语音识别后的文本丢进队列；
- 回到工位，任务早已全部跑通测试，整装待发。

如果你也是 Codex、Claude Code、Pi 的重度用户，欢迎尝试并 Star 这个项目！

- **GitHub 仓库**：[https://github.com/tenfyzhong/agentix](https://github.com/tenfyzhong/agentix)
- **Homebrew Tap**：[https://github.com/tenfyzhong/homebrew-tap](https://github.com/tenfyzhong/homebrew-tap)
- **问题与反馈**：欢迎在 GitHub Issues 提出建议或交流使用心得！
