---
title: "Cloudflare 电子邮件路由配置指南：免费拥有你的域名邮箱"
date: 2025-08-04T13:15:00+08:00
categories:
  - "网络技术"
tags:
  - "cloudflare"
  - "email-routing"
  - "dns"
  - "tutorial"
keywords: "cloudflare,email routing,dns,free email forward,catch-all"
---

您是否拥有一个域名，但又不想为了一个自定义的邮箱地址（例如 `info@yourdomain.com`）而支付额外的企业邮箱费用？Cloudflare 的电子邮件路由（Email Routing）功能为您提供了一个完美且免费的解决方案。它允许您创建任意数量的自定义域名邮箱地址，并将收到的邮件无缝转发到您现有的个人邮箱（如 Gmail、Outlook 等）。

本文将详细引导您完成 Cloudflare 电子邮件路由的配置过程，包括设置单个地址转发和更为强大的 Catch-all 全域地址转发。

# 准备工作

在开始之前，请确保您满足以下条件：

1. 您拥有一个自己的域名。
2. 该域名已经添加到您的 Cloudflare 账户中，并由 Cloudflare 进行 DNS 解析。

# 第一步：启用电子邮件路由并配置 DNS

当您首次在 Cloudflare 上为某个域名设置电子邮件路由时，Cloudflare 会自动为您添加必要的 DNS 记录（主要是 `MX` 和 `TXT` 记录），以确保邮件能够正确路由。

1. 登录到您的 Cloudflare 账户。
2. 选择您要配置的域名。
3. 在左侧菜单中，找到并点击 **Email** > **Email Routing**。

如果您是首次使用，Cloudflare 会引导您完成一个简单的设置流程。您只需按照提示点击按钮，Cloudflare 会自动添加或更新所需的 DNS 记录。通常，它会要求您添加以下类型的记录：

- **MX 记录**: 指示邮件服务器将发送到您域名的邮件路由到 Cloudflare。
- **TXT (SPF) 记录**: 用于验证 Cloudflare 有权代表您发送邮件，防止邮件被标记为垃圾邮件。

这个过程通常是自动化的，您只需确认即可。

# 第二步：配置单个地址转发

单个地址转发适用于您希望创建特定、独立的邮箱地址的场景，例如 `contact@yourdomain.com` 或 `support@yourdomain.com`。

1. 在 **Email Routing** 页面的 **Routes** 选项卡下，找到 **Custom addresses** 部分。
2. 点击 **Create address** 按钮。
3. 在 **Custom address** 字段中，输入您想要创建的邮箱前缀（例如 `info`）。
4. 在 **Action** 下拉菜单中，选择 **Send to**。
5. 在 **Destination address** 字段中，输入您希望接收转发邮件的个人邮箱地址（例如 `your-personal-email@gmail.com`）。
6. 点击 **Save**。

**验证目标邮箱**：
为了防止滥用，Cloudflare 会向您的目标邮箱（`your-personal-email@gmail.com`）发送一封验证邮件。您需要打开该邮件并点击其中的验证链接，该条转发规则才会生效。

您可以重复以上步骤，创建任意多个自定义地址。

# 第三步：配置 Catch-all 全域转发

Catch-all 规则是一个非常强大的功能。启用后，任何发送到您域名下**不存在的**邮箱地址的邮件，都会被自动转发到您指定的目标邮箱。这可以有效防止因发件人拼写错误而丢失邮件。

例如，如果有人错误地将邮件发送到 `infp@yourdomain.com` (拼写错误)，Catch-all 规则会捕获这封邮件并将其转发。

1. 在 **Email Routing** 页面的 **Routes** 选项卡下，找到 **Catch-all address** 部分。
2. 在 **Action** 下拉菜单中，选择 **Send to**。
3. 在 **Destination address** 字段中，输入您希望接收所有这些邮件的目标邮箱。建议使用一个专门的邮箱来处理，以免与您的主邮箱混淆。
4. 点击 **Save**。

同样，如果目标邮箱地址尚未经过验证，您需要先完成验证步骤。

# 总结

通过以上简单的几个步骤，您就可以利用 Cloudflare 免费、高效地为您的域名配置电子邮件路由。无论是创建专业的联系邮箱，还是通过 Catch-all 规则确保不漏掉任何一封重要邮件，Cloudflare Email Routing 都是一个值得推荐的强大工具。

需要注意的是，此功能仅支持**接收和转发**邮件，您不能通过这些地址直接**发送**邮件。如果您需要发送功能，则仍需考虑完整的企业邮箱解决方案。但对于绝大多数仅需接收邮件的场景，Cloudflare 已然足够。
