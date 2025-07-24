---
title: 把免费的gemini用到极致
date: 2025-07-24T20:09:24+08:00
draft: true
categories:
  - ai
tags:
  - ai
keywords:
---

众所周知 gemini 2.5 pro 现在在众多模型里排名里, 数一数二的地位. 而且, 它可以免费使用, 就非常良心. 然后, 它提供的免费额度非常低.
这里, 来看看怎么把免费额度提到完全满足自己的需求.
<!-- more -->

# Gemini 免费额度

参考 [Rate limits | Gemini API](https://ai.google.dev/gemini-api/docs/rate-limits?authuser=1), 对于免费层级的用户, gemini提供的额度如下:

- gemini-2.5-pro: 5 RPM, 250000 TPM, 100 RPD
- gemini-2.5-flash: 10 RPM, 250000 TPM, 250 RPD

在日常工作中, gemini-2.5-pro 模型 5RPM, 100RPD的额度,肯定是不够用的. 特别是在使用 gemini cli 的话, 请求数就狂烧. 我试过使用 gemini cli 一天造了 1300 个请求.

这里的限流是基于 google 的项目的, 这一点很重要. 我们就是要利用这一点, 来提高我们的额度.

# gemini-balance

Github上有一个开源项目[gemini-balance](https://github.com/snailyp/gemini-balance).

Gemini Balance 是一个基于 Python FastAPI 构建的应用程序，旨在提供 Google Gemini API 的代理和负载均衡功能。它允许您管理多个 Gemini API Key，并通过简单的配置实现 Key 的轮询、认证、模型过滤和状态监控。此外，项目还集成了图像生成和多种图床上传功能，并支持 OpenAI API 格式的代理。

这样我们只要申请多个gemini key, 配置到gemini-balance里, 这样我们要多少额度都可以了. 但是250000TPM的限制绕不开, 但是250K的上下文, 在业界也是遥遥领先了.

可以参考 gemini-balance 的文档, 在本地或者自己的vps或者一些免费的云空间上部署好gemini-balance, 然后就可以放飞自我了.

可以看看我的使用记录
![](https://tenfy.cn/picture/request-count.jpg)

# 创建gemini key

## 创建google project

在上面我们说过, 限流是基于项目的, 所以得先去申请一批项目. 一个google, 默认可以申请12个, 可以提申请增加到75个.

可以先在这里去创建一批项目 [https://console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate)

## 创建 gemini key

在上面创建好项目后, 可以到这里去创建一批 gemini key了 [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

创建好之后,就可以在 cherry studio 或者 gemini cli 或者其他ai(比如开发工具 cline, nvim...)上配置使用了.

# 配置gemini cli

使用login的方式登录使用gemini cli,总是会因为命中限流,导致降级flash,或者有时直接就不可用. 上下文也恢复不了,完全不可用.

但是, 如果使用 apikey 的方式授权, 就不会出出这个问题. 加上我们上面的方式申请的多个key进行轮询使用, 需要多少的量都可以配置.

对于 gemini cli 的配置很简单, 配置环境即可, 把下面的key和url配置成你的 gemini-balance 的即可.

```bash
export GEMINI_API_KEY=xxxx
export GOOGLE_GEMINI_BASE_URL=https://xxxx
```

# 最后

建议不要使用自己个人的google账户申请太多的key, 避免被封了, 就很难受. 可以去闲鱼上买, 5毛一个key, 100个也就50块, 可以永久使用.
