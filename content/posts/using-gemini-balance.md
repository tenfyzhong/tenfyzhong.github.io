---
title: 优雅绕过 Gemini API 速率限制，实现“无限”免费调用
date: 2025-07-24T20:09:24+08:00
categories:
  - ai
tags:
  - ai
  - gemini
  - api
keywords:
  - gemini, api, rate limit, balance, proxy
---

Google 的 Gemini 2.5 Pro 模型无疑是当今性能最顶尖的 AI 模型之一。更难能可贵的是，Google 提供了相当慷慨的免费使用额度，让广大开发者和 AI 爱好者都能亲身体验其强大功能。然而，这份“免费午餐”并非毫无限制，其严格的速率限制（Rate Limits）常常成为重度使用场景下的瓶颈。

本文将为你介绍一种行之有效的方法，通过负载均衡多个 API Key，优雅地绕过官方的速率限制，从而实现近乎“无限”的免费调用。
<!-- more -->

## Gemini 免费额度的“紧箍咒”

根据 [Gemini API 官方文档](https://ai.google.dev/gemini-api/docs/rate-limits)，免费套餐（Free tier）的速率限制如下：

- **Gemini 2.5 Pro:** 5 RPM (每分钟请求数), 250,000 TPM (每分钟 Token 数), 100 RPD (每天请求数)
- **Gemini 2.5 Flash:** 15 RPM, 1,000,000 TPM, 1500 RPD

对于日常的轻度使用，这个额度或许足够。但对于开发者而言，尤其是在使用 `gemini-cli` 等命令行工具进行高频交互或自动化任务时，`5 RPM` 和 `100 RPD` 的限制很快就会捉襟见肘。我个人就曾在使用 `gemini-cli` 时，在一天内轻松产生超过 1300 次请求，远超免费额度。

问题的关键在于：**Gemini 的速率限制是基于单个 Google Cloud 项目的**。这意味着，每一个项目都拥有自己独立的一套额度。这个机制，正是我们突破限制的关键。

## 解决方案：`gemini-balance` 负载均衡代理

为了利用多项目的独立额度，社区中诞生了 [gemini-balance](https://github.com/snailyp/gemini-balance) 这个优秀的开源项目。

`gemini-balance` 是一个基于 Python FastAPI 构建的轻量级应用，其核心功能是作为 Google Gemini API 的代理和负载均衡器。它允许你配置一个 API Key 池，并将进来的请求轮询分发到这些 Key 上。

通过这种方式，你的请求速率上限将成倍增加。例如，如果你配置了 10 个来自不同项目的 API Key，你的理论请求上限就变成了：

- **Gemini 2.5 Pro:** 50 RPM, 1000 RPD

这极大地提高了可用性，满足了绝大部分高强度使用场景的需求。值得注意的是，TPM（每分钟 Token 数）的限制仍然存在，但 Gemini 2.5 Pro 高达 250K 的 TPM 额度本身已经相当宽裕。

`gemini-balance` 还提供了认证、模型过滤、状态监控、OpenAI API 格式兼容等丰富功能，部署和使用都非常便捷。

![](https://tenfy.cn/picture/request-count.jpg)
*我的 `gemini-balance` 使用记录，轻松应对高频请求*

## 操作指南：三步实现额度自由

### 第一步：创建多个 Google Cloud 项目

既然限制是基于项目的，我们首先需要创建一批 Google Cloud 项目。一个标准的 Google 账户默认可以创建约 12 个项目，也可以申请提升配额。

- **项目创建地址:** [https://console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate)

建议一次性创建 10-20 个项目备用。

### 第二步：为每个项目生成 API Key

项目创建完毕后，需要为每一个项目单独生成一个 Gemini API Key。

- **API Key 生成地址:** [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

在页面右上角切换不同的项目，然后为当前选中的项目创建 API Key。将这些 Key 妥善保存下来。

### 第三步：部署并配置 `gemini-balance`

获取到足量的 API Key 后，就可以部署 `gemini-balance` 了。你可以根据官方文档的指引，将其部署在本地、个人服务器（VPS）或者 Heroku、Vercel 等云平台上。

部署完成后，你的所有 AI 应用（如 `gemini-cli`、VSCode 插件、各类开发工具等）不再需要直连 Google API，而是将请求指向你的 `gemini-balance` 服务地址。

以 `gemini-cli` 为例，只需配置两个环境变量即可：

```bash
# 将 xxxx 替换为 gemini-balance 设置的访问凭证
export GEMINI_API_KEY=xxxx
# 将 https://xxxx 替换为你的 gemini-balance 服务地址
export GOOGLE_GEMINI_BASE_URL=https://xxxx
```

通过 API Key 方式授权，配合 `gemini-balance` 的负载均衡，可以彻底告别因命中速率限制而导致模型降级或服务不可用的烦恼，同时也能保持稳定的会话上下文。

## 最后的一点建议

直接使用个人主力 Google 账户创建大量项目和 Key 可能存在被风控的风险。为了安全起见，建议使用一些非关键的 Google 账户进行操作。

对于需要大量 Key 的用户，也可以考虑通过一些第三方渠道获取，这通常更省时省力，也能有效规避个人账户的风险。

希望这篇文章能帮助你彻底释放 Gemini 的潜力，让它成为你手中更强大的生产力工具。
