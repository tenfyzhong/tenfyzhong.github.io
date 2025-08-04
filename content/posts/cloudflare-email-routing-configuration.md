---
title: "Cloudflare 电子邮件路由配置指南：免费、高效的邮件转发服务"
date: 2025-08-04T13:00:20+08:00
categories:
  - "技术"
tags:
  - "cloudflare"
  - "email"
  - "dns"
  - "tutorial"
keywords: "cloudflare,email routing,dns,email forward,catch-all"
---

Cloudflare 的电子邮件路由（Email Routing）是一项非常实用且免费的服务，它允许你为自己的域名创建自定义的电子邮件地址，并将收到的邮件转发到你指定的个人邮箱（如 Gmail、Outlook 等）。这不仅提升了专业形象，还能有效保护你的真实邮箱地址不被泄露。

本文将详细介绍如何配置 Cloudflare 的电子邮件路由，包括设置单个地址转发和 catch-all 全域地址转发。

### 前提条件

在开始之前，请确保你拥有一个已经添加到 Cloudflare 并正常托管 DNS 的域名。

### 步骤一：启用电子邮件路由并添加 DNS 记录

1. 登录到你的 Cloudflare 仪表板。
2. 选择你需要配置的域名。
3. 在左侧的菜单栏中，找到并点击 **“电子邮件”** -> **“电子邮件路由”**。

如果你是第一次使用该功能，Cloudflare 会引导你完成初始设置。这通常包括添加几条用于接收邮件的 DNS 记录（`MX` 记录和 `TXT` 记录）。

你通常只需要点击 “**添加记录并启用**” 按钮，Cloudflare 就会自动为你配置好所有必需的 DNS 记录。等待几分钟，DNS 记录生效后，你的域名就具备了接收邮件并进行路由转发的能力。

### 步骤二：配置单个地址转发

如果你希望为特定的目的创建邮箱地址，例如 `contact@yourdomain.com` 或 `support@yourdomain.com`，可以按照以下步骤操作。

1. 在 “电子邮件路由” 页面，确保你位于 **“路由”** 选项卡下。
2. 点击 **“创建地址”** 按钮。
3. 在 **“自定义地址”** 字段中，输入你想要的邮箱前缀（例如 `contact`）。
4. 在 **“目标地址”** 字段中，输入你希望接收邮件的真实邮箱地址（例如 `your.personal.email@gmail.com`）。
5. 点击 **“保存”**。

![创建自定义地址](https.wp-assets.tenfy.cn/wp-content/uploads/2024/08/05024458/cloudflare-create-custom-address.png)

保存后，Cloudflare 会向你的目标邮箱发送一封验证邮件。请务必点击邮件中的链接完成验证，否则路由规则不会生效。

验证通过后，任何发送到 `contact@yourdomain.com` 的邮件都会被自动转发到 `your.personal.email@gmail.com`。

### 步骤三：配置 Catch-all 全域地址转发

Catch-all（全域捕获）规则非常强大，它能将所有发送到你域名下、但又没有精确匹配路由规则的任意邮箱地址的邮件，全部转发到指定的邮箱。例如，有人将邮件发送到 `random-stuff@yourdomain.com`，你依然可以收到它。

1. 在 **“路由”** 选项卡下，找到 **“Catch-all 地址”** 这个部分。
2. 默认情况下，它的操作可能是 “丢弃(Drop)”。将其更改为 **“发送到电子邮件”**。
3. 在下方的 **“目标地址”** 框中，输入你希望接收所有这些邮件的真实邮箱地址。
4. 点击 **“保存”**。

![配置 Catch-all 地址](https.wp-assets.tenfy.cn/wp-content/uploads/2024/08/05024501/cloudflare-catch-all-address.png)

启用 Catch-all 规则后，你就再也不用担心因为别人输错邮箱前缀而收不到邮件了。

### 总结

通过以上简单的几步，你就成功配置了 Cloudflare 强大的电子邮件路由功能。它不仅完全免费，而且配置简单、运行稳定，是你管理域名邮箱的绝佳选择。无论是为不同场景创建独立的邮箱地址，还是通过 Catch-all 规则确保不漏掉任何一封邮件，Cloudflare Email Routing 都能轻松满足你的需求。
