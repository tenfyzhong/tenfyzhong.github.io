---
title: "DNS小白也能轻松搞定！Cloudflare域名解析超详细图文教程"
date: 2025-08-04T10:30:00+08:00
categories:
  - 网络
tags:
  - DNS
  - Cloudflare
  - 教程
keywords: "Cloudflare, DNS, 域名解析, 教程"
---

你是否曾经购买了一个心仪的域名，却对着一堆A、CNAME、MX记录发愁，感觉自己仿佛在破解什么上古密码？别担心，你不是一个人！域名系统（DNS）听起来高深，但实际上，只要用对工具，它比你想象的要简单得多。

今天，我们就来借助免费又强大的 Cloudflare，手把手教你如何轻松管理你的域名解析，让你的网站和服务顺利“指路上线”！

<!-- more -->

# 为什么选择 Cloudflare？

在我们开始之前，你可能会问：“为什么是 Cloudflare？” 理由很简单：

1. **免费，而且功能强大**：Cloudflare 的免费套餐已经包含了绝大多数个人用户和小型项目所需的功能，包括 DNS 解析、CDN 加速、DDoS 防护等。
2. **速度快，全球节点**：它的 DNS 解析速度在全球名列前茅，能让用户更快地访问到你的网站。
3. **界面友好，操作直观**：对于新手来说，Cloudflare 的仪表盘设计得非常清晰，操作起来毫无压力。

# 准备工作

在开始这趟旅程之前，请确保你已经准备好了两样东西：

1. **一个你自己的域名**：例如 `yourdomain.com`。
2. **一个 Cloudflare 账户**：如果没有，可以去 [Cloudflare 官网](https://dash.cloudflare.com/sign-up) 免费注册一个。

准备好了吗？我们发车！

# 第一步：将你的网站添加到 Cloudflare

登录你的 Cloudflare 账户，点击“添加站点”按钮，输入你的域名，然后按照向导点击下一步。Cloudflare 会自动扫描你现有的 DNS 记录。

![在Cloudflare添加站点](https://tenfy.cn/picture/cloudflare-add-site.png)

# 第二步：更改你的域名服务器 (Nameservers)

这是最关键的一步！Cloudflare 会给你提供两个新的域名服务器（Nameservers）地址。你需要登录到你购买域名的平台（比如 GoDaddy, Namecheap, 阿里云等），找到 DNS 管理或域名服务器设置，将原来的 NS 地址替换成 Cloudflare 提供给你的这两个。

**请注意：** 这一步是在你的**域名注册商**那里操作，而不是在 Cloudflare！

![更改NS记录](https://tenfy.cn/picture/cloudflare-nameservers.png)

完成更改后，回到 Cloudflare 点击“完成，检查域名服务器”按钮。DNS 全球生效需要一些时间，短则几分钟，长则可能需要几个小时，请耐心等待。当生效后，你会收到 Cloudflare 的邮件通知。

# 第三步：玩转 DNS 解析面板

一旦你的站点在 Cloudflare 上激活，你就可以在“DNS” -> “记录”页面看到你的 DNS 管理面板了。这里就是我们施展魔法的地方。

![DNS管理面板](https://tenfy.cn/picture/cloudflare-dns-dashboard.png)

# 第四步：常见 DNS 记录类型科普

在添加记录之前，我们先快速了解一下几个最常见的记录类型：

- **A 记录 (Address)**: 用于将你的域名指向一个 IPv4 地址。这是最基本、最常用的记录。
- **AAAA 记录**: 和 A 记录类似，但用于指向 IPv6 地址。
- **CNAME 记录 (Canonical Name)**: 用于将一个域名指向另一个域名。例如，你可以让 `www.yourdomain.com` 指向 `yourdomain.com`。
- **MX 记录 (Mail Exchanger)**: 用于指定处理你域名邮箱的邮件服务器。
- **TXT 记录 (Text)**: 允许你存放一些文本信息，常用于验证域名所有权（如 Google Search Console）或设置 SPF（发信人策略框架）来防止邮件欺诈。

# 第五步：实战！添加你的第一条 DNS 记录

理论知识够了，我们来动手操作一下。

## 示例一：添加 A 记录 (让域名指向你的服务器)

假设你的服务器 IP 地址是 `192.0.2.1`，你想让 `yourdomain.com` 这个根域名指向它。

1. 点击“添加记录”。
2. **类型** 选择 `A`。
3. **名称** 填写 `@`（`@` 代表根域名，也就是 `yourdomain.com` 本身）。
4. **IPv4 地址** 填写你的服务器 IP `192.0.2.1`。
5. 点击“保存”。

![添加A记录](https://tenfy.cn/picture/cloudflare-add-a-record.png)

## 示例二：添加 CNAME 记录 (设置 www 子域名)

我们希望用户访问 `www.yourdomain.com` 也能看到和 `yourdomain.com` 一样的内容。

1. 点击“添加记录”。
2. **类型** 选择 `CNAME`。
3. **名称** 填写 `www`。
4. **目标** 填写 `@` 或者你的根域名 `yourdomain.com`。
5. 点击“保存”。

## 重点：橙色云 vs 灰色云 (代理状态)

细心的你可能已经发现了，每条 A 记录或 CNAME 记录后面都有一朵小云彩。这可是 Cloudflare 的精髓所在！

- **橙色云 (已代理)**: 当云是橙色时，所有指向这个域名的流量都会先经过 Cloudflare 的全球网络。这意味着你的网站享受到了 CDN 加速、DDoS 防护、免费 SSL 证书等一系列好处。用户的真实 IP 也会被隐藏。
- **灰色云 (仅限 DNS)**: 当云是灰色时，Cloudflare 只提供 DNS 解析服务，流量会直接打到你的源站服务器，不享受任何加速和保护。这通常用于一些不需要或不能通过代理的记录，比如用于 SSH 连接的子域名。

![代理状态](https://tenfy.cn/picture/cloudflare-proxy-status.png)

你可以随时点击这朵云来切换状态。

# 第六步：验证与排错

添加或修改记录后，如何知道它是否生效了呢？

- **使用命令行工具**: 你可以在终端中使用 `dig` 命令来查询。例如：`dig yourdomain.com`。
- **使用在线工具**: 在 Google 上搜索 “DNS Checker”，有很多网站可以帮你从全球多个地点检查 DNS 解析情况。

如果发现不生效，请不要着急，DNS 记录的传播（Propagation）需要时间。如果超过 24 小时仍有问题，请检查你的域名服务器设置是否正确。

# 总结

恭喜你！现在你已经掌握了在 Cloudflare 上管理 DNS 的基本技能。从指向服务器的 A 记录，到设置子域名的 CNAME 记录，再到理解橙色云和灰色云的区别，你已经不再是那个面对 DNS 一头雾水的小白了。

大胆去探索吧，为你的项目配置好域名，让世界通过一个好记的名字找到你的创造！
