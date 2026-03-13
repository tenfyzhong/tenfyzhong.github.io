---
title: "openclaw-docker：一条命令启动 OpenClaw 网关"
date: 2026-03-14T00:18:12+08:00
categories:
  - "运维"
tags:
  - "docker"
  - "openclaw"
  - "devops"
  - "tutorial"
keywords: "openclaw,docker,openclaw-docker,compose,tutorial"
---

最近我单独做了一个仓库：[tenfyzhong/openclaw-docker](https://github.com/tenfyzhong/openclaw-docker)。

这篇文章主要说两件事：为什么要做它，以及你怎么最快把 OpenClaw 跑起来。

<!-- more -->

## 为什么我要做这个仓库

我一开始也是按官方方式折腾 Docker 运行 OpenClaw，但实际体验里有几个明显门槛：

1. 需要先 clone 官方仓库再走一套安装流程，对只想快速跑起来的人来说步骤偏多。
2. 初次运行时经常要根据日志继续调整配置，容错和上手成本都不低。
3. 对于“我只想先把网关跑起来再说”的场景，不够直接。

所以我做了 `openclaw-docker`，目标很明确：

- 减少启动步骤
- 降低首次运行排障成本
- 把默认配置和持久化目录准备好

## 怎么用：`docker compose up -d` 直接启动

仓库地址：<https://github.com/tenfyzhong/openclaw-docker>

### 1. 获取仓库

```bash
git clone https://github.com/tenfyzhong/openclaw-docker.git
cd openclaw-docker
```

### 2. 一键启动

```bash
docker compose up -d
```

就这一条命令，服务会按仓库里的 `docker-compose.yml` 启动起来。你不需要再去 clone OpenClaw 官方仓库。

### 3. 检查服务状态

```bash
docker compose ps
curl http://127.0.0.1:18789/healthz
```

如果需要看日志：

```bash
docker compose logs -f openclaw-gateway
```

## 第一次启动后的配置指引

第一次起来后，需要在容器里完成 onboarding：

```bash
docker compose exec openclaw-gateway bash
openclaw onboard
```

几点建议：

1. onboarding 过程中网关可能会重启，终端断开属于正常现象。
2. 如果中断，重新进入容器再次执行 `openclaw onboard` 即可，已有进度会复用。
3. 配置文件和工作目录默认持久化在本机：
   - `./.docker/openclaw/config`
   - `./.docker/openclaw/workspace`

如果你想在首次启动前就指定端口或 token，可以在仓库根目录新建 `.env`，例如：

```dotenv
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_BRIDGE_PORT=18790
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_GATEWAY_TOKEN=your-token
```

如果你没有手动设置 `OPENCLAW_GATEWAY_TOKEN`，容器会在首次启动时自动生成并写入 `openclaw.json`。

## 自动跟进官方版本同步更新

`openclaw-docker` 的另一个重点是“持续跟进官方版本”。

仓库内置了自动化流程：

1. 通过 GitHub Actions 检查 OpenClaw 官方稳定版本 tag。
2. 同步最新主版本 tag 到本仓库。
3. 自动触发镜像构建与推送。

这样做的好处是：

- 你不用自己盯着每次官方发版。
- 仓库维护侧会持续把 Docker 镜像跟进到官方新版本。
- 你只要按这篇文章的方式启动和更新容器即可。

## 小结

如果你想要的是“尽快把 OpenClaw 网关先跑起来”，`openclaw-docker` 就是为这个目标做的：

- 启动方式简单：`docker compose up -d`
- 首次配置明确：`openclaw onboard`
- 持续更新可用：自动跟进官方版本

欢迎直接用起来，有问题也可以到仓库提 issue。
