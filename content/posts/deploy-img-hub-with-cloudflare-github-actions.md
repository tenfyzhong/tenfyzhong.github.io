---
title: "从买域名到上线：小白用 GitHub Actions 部署 ImgHub 图床完整图文教程"
date: 2026-08-09T21:30:00+08:00
categories:
  - "运维"
tags:
  - "img-hub"
  - "cloudflare"
  - "github-actions"
  - "tutorial"
keywords: "ImgHub, Cloudflare Workers, GitHub Actions, Spaceship, 域名购买, 图床部署"
---

想搭建一个属于自己的图床，却被“域名、DNS、Cloudflare、GitHub Actions、Secret”这些名词劝退？这篇文章就是为第一次接触部署的小白准备的。

我们会从零开始完成整条链路：在 Spaceship 购买域名，把域名接入 Cloudflare，注册 GitHub 并 Fork ImgHub，配置 Cloudflare Token 和 GitHub Actions Secrets，运行部署工作流，最后把 `img.example.com` 这样的自定义域名绑定到 ImgHub。

<!-- more -->

# 最后会得到什么？

[ImgHub](https://github.com/tenfyzhong/img-hub) 是一个运行在 Cloudflare 上的多用户文件与文本托管服务。它只使用以下 Cloudflare 产品：

- **Workers**：运行网站和后端程序。
- **D1**：保存用户、文件信息和站点设置。
- **R2**：保存真正的图片和其他文件。
- **Turnstile**：登录失败次数过多时进行人机验证。

部署完成后，你会得到：

- 一个 `*.workers.dev` 的默认地址；
- 一个自己的地址，例如 `https://img.example.com`；
- 一个固定用户名为 `admin` 的管理员账号；
- 上传文件、发布文本、生成公开链接和创建普通用户等功能。

整个过程不需要购买服务器。Cloudflare 和 GitHub 都有免费使用额度，但不是“永远无限免费”，正式使用前仍应查看 [Cloudflare Workers 定价](https://developers.cloudflare.com/workers/platform/pricing/)、[D1 定价](https://developers.cloudflare.com/d1/platform/pricing/) 和 [R2 定价](https://developers.cloudflare.com/r2/pricing/)。域名则需要每年付费续费。

# 开始前先准备好

请准备：

1. 一个长期使用的邮箱。
2. 一个密码管理器，用来保存各平台密码和 Cloudflare Token。
3. 一张 Spaceship 支持的付款卡，或它当前支持的其他付款方式。
4. 预先想好域名和 ImgHub 子域名。本文统一使用：
   - 根域名：`example.com`
   - ImgHub 地址：`img.example.com`

推荐使用 `img.example.com` 这样的子域名，不要一开始就占用 `example.com`。以后根域名还可以用来放博客或个人主页。

> 本文截图拍摄或整理于 2026 年 8 月。平台可能调整按钮名称和布局，但关键概念不会改变。所有账号、域名、ID 和凭据均为示例或已脱敏。

# 第一步：在 Spaceship 购买一个域名

打开 [Spaceship 域名搜索页](https://www.spaceship.com/domains/)，输入想要的完整域名，例如 `yourname.com`。如果显示可以注册，就把它加入购物车。

## 别只看第一年的低价

域名通常有三个容易混淆的价格：

- **Register**：第一年注册价格。
- **Renew**：第二年开始的续费价格。
- **ICANN fee**：部分后缀另外收取的小额管理费。

以 2026 年 8 月 9 日 [Spaceship 公开价格页](https://www.spaceship.com/domains/) 的美元价格为例：`.shop` 第一年的促销价很低，但续费价明显更高；`.com` 首年价格不是最低，续费价格却相对稳定。准备长期使用时，应该比较“首年 + 未来续费”，而不是只挑第一年最便宜的后缀。

![Spaceship域名购物车示例](https://tenfy.cn/picture/img-hub-spaceship-checkout-example.jpg)

*图 1：Spaceship 购物车示例。重点检查注册年限、续费价格、自动续费、隐私保护、ICANN 费用和最终总价；截图中的域名与价格只作界面说明，付款前以购物车实时金额为准。界面示例来源：[Kripesh Adwani](https://kripeshadwani.com/best-domain-name-registrars/)。*

结账时按页面提示完成以下操作：

1. 注册 Spaceship 账号并验证邮箱。
2. 填写真实的域名联系人信息。不要乱填，否则将来可能影响域名所有权验证。
3. 确认购物车里没有不需要的主机、邮箱或建站产品。部署 ImgHub 不需要在 Spaceship 购买主机。
4. 选择是否开启自动续费。开启可以避免忘记续费，关闭则要自己设置日历提醒。
5. 确认最终金额后付款。

域名购买完成后，可以在 Spaceship 的 **Domain List** 中看到它。

# 第二步：注册 Cloudflare，并添加域名

打开 [Cloudflare 注册页面](https://dash.cloudflare.com/sign-up)，使用邮箱创建账号并完成邮箱验证。建议立即在个人资料的认证设置中开启两步验证，避免域名和部署资源被盗。

登录 Cloudflare 后：

1. 进入 **Domains**。
2. 点击 **Onboard a domain**，有些界面会显示 **Add a domain** 或“加入域”。
3. 只输入根域名 `example.com`，不要输入 `https://`，也不要输入 `img.example.com`。
4. 新手可以选择 **Quick scan for DNS records**。
5. 套餐选择 **Free**，然后继续。

![在Cloudflare添加域名](https://tenfy.cn/picture/cloudflare-add-site.png)

*图 2：Cloudflare 添加域名页面。输入的是 `example.com` 这样的根域名；快速扫描适合新域名，但已有网站或邮箱时仍要人工检查扫描到的 DNS 记录。*

如果这是刚买的新域名，通常没有重要的旧 DNS 记录。如果域名已经在使用网站或邮箱，请不要盲目删除现有的 A、CNAME、MX 和 TXT 记录，否则原服务可能中断。

# 第三步：把 Spaceship 域名服务器改成 Cloudflare

Cloudflare 会为这个域名分配两个名称服务器，也叫 Nameserver 或 NS，例如：

```text
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

每个域名实际分配到的名称都不同，必须复制 Cloudflare 页面给你的两个值，不能照抄本文示例。

![Cloudflare分配的两个名称服务器](https://tenfy.cn/picture/cloudflare-ns.jpg)

*图 3：Cloudflare 激活页面会列出两个专属于当前域名的 Nameserver。保持这个页面打开，下一步要把它们复制到 Spaceship。*

## 先检查 DNSSEC

如果 Spaceship 中已经为这个域名启用了 DNSSEC，请先关闭它，再更换 Nameserver。Cloudflare 官方也明确提醒：带着旧 DNSSEC 配置直接更换名称服务器，可能让域名暂时无法访问。Cloudflare 激活成功后，可以再按照 Cloudflare 的 DNSSEC 页面重新开启。

## 在 Spaceship 修改 Nameserver

回到 Spaceship：

1. 打开 **Advanced DNS**，选择刚购买的域名。
2. 在 **Nameservers** 区域点击 **Change**。

![Spaceship名称服务器修改入口](https://tenfy.cn/picture/img-hub-spaceship-nameservers-change.png)

*图 4：Spaceship 的 Nameservers 卡片。绿色箭头所指的 **Change** 是修改入口；旁边的传播状态用于观察修改是否生效。*

在弹窗中：

1. 选择 **Custom nameservers**。
2. 将 Cloudflare 提供的第一个地址填入第一行。
3. 将第二个地址填入第二行。
4. 点击 **Save nameserver settings**。
5. 如果出现“现有 Spaceship 连接会断开”的提醒，确认你不依赖 Spaceship 主机或邮箱后再继续。

![Spaceship填写Cloudflare名称服务器](https://tenfy.cn/picture/img-hub-spaceship-custom-nameservers.png)

*图 5：Spaceship 的 Custom nameservers 表单。这里只填写 Cloudflare 给出的两个 NS 主机名，不填 IP，也不要添加 `https://`。*

改好后返回 Cloudflare，点击 **Check nameservers now** 或“检查名称服务器”。根据 [Spaceship 官方说明](https://www.spaceship.com/en-GB/knowledgebase/connect-domain-custom-nameservers/)，全球传播最长可能需要 48 小时，多数情况下会更快。Cloudflare 中域名状态变成 **Active** 后，再继续后面的自定义域名步骤最稳妥。

# 第四步：注册 GitHub，并 Fork ImgHub

如果还没有 GitHub 账号，打开 [GitHub 注册页面](https://github.com/signup)，完成邮箱验证并设置用户名。建议同样开启两步验证。

然后打开 [tenfyzhong/img-hub](https://github.com/tenfyzhong/img-hub)：

![ImgHub的GitHub仓库与Fork按钮](https://tenfy.cn/picture/img-hub-github-repository-fork.png)

*图 6：ImgHub 仓库首页。未登录时右上角可以注册；登录后点击仓库右上方的 **Fork**，把一份可由自己配置的代码复制到自己的 GitHub 账号。*

按下面操作：

1. 点击右上角 **Fork**。
2. **Owner** 选择自己的 GitHub 账号。
3. 仓库名保持 `img-hub`。
4. 可以勾选只复制默认分支。ImgHub 的稳定部署分支是 `main`。
5. 点击 **Create fork**。

Fork 完成后，浏览器地址应该类似：

```text
https://github.com/YOUR_GITHUB_NAME/img-hub
```

后面所有 GitHub 设置都要在你自己的 Fork 中完成，不要回到 `tenfyzhong/img-hub` 原仓库配置。

第一次打开 Fork 的 **Actions** 页时，GitHub 可能显示工作流已被禁用。点击 **I understand my workflows, go ahead and enable them**。这是 Fork 仓库常见的安全确认。

# 第五步：创建最小权限 Cloudflare API Token

GitHub Actions 需要得到你的明确授权，才能在 Cloudflare 账号中创建 Worker、D1、R2 和 Turnstile。这里使用可以随时撤销、能够限制权限的 **API Token**，不要使用权限过大的 **Global API Key**。

打开 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)，点击 **Create Token**，再选择 **Create Custom Token**。

![Cloudflare创建自定义Token](https://tenfy.cn/picture/img-hub-cloudflare-token-create.svg)

*图 7：脱敏示意图。ImgHub 应选择 **Create Custom Token**，这样才能逐项配置最小权限。*

Token 名称可以填写 `github-img-hub-deploy`。然后只添加下面七项权限：

| 范围 | 权限 | 级别 | 用途 |
| --- | --- | --- | --- |
| Account | Account Settings | Read | 识别并校验目标账号 |
| Account | Workers Scripts | Edit | 部署 Worker、静态资源、定时任务和 Secret |
| Account | D1 | Edit | 创建数据库并初始化表结构 |
| Account | Workers R2 Storage | Edit | 创建并绑定 R2 Bucket |
| Account | Turnstile | Edit | 创建和更新登录验证 Widget |
| User | User Details | Read | 让部署工具读取当前用户信息 |
| User | Memberships | Read | 确认当前用户属于目标账号 |

Cloudflare 有时会把写权限显示为 **Write**，例如 **Turnstile Sites Write**；在这个场景中，它对应上表需要的 Turnstile 写权限。

![Cloudflare Token最小权限](https://tenfy.cn/picture/img-hub-cloudflare-token-permissions.svg)

*图 8：ImgHub 部署需要的七项权限。默认的 `workers.dev` 部署不需要 KV、Workers Tail、DNS 或 Zone 权限。*

在 **Account Resources** 中选择：

```text
Include → Specific account → 你的 Cloudflare 账号
```

不要为了省一步而选择所有账号。

![限制Cloudflare Token账号范围](https://tenfy.cn/picture/img-hub-cloudflare-token-scope.svg)

*图 9：把 Token 限制到真正用于部署 ImgHub 的那个 Cloudflare 账号。下面列出的两个名称正是稍后要创建的 GitHub Secrets。*

点击 **Continue to summary**，再次检查权限和账号，然后点击 **Create Token**。Token 明文只显示一次，立即复制到密码管理器中。不要把它发到聊天、Issue、代码文件或截图里。

# 第六步：复制 Cloudflare Account ID

在 Cloudflare Dashboard 任意页面按 `Ctrl + K`，macOS 可以按 `Command + K`，搜索：

```text
Copy account ID
```

点击搜索结果即可复制。也可以进入 **Workers & Pages**，在账号详情中找到 Account ID。具体位置可参考 [Cloudflare 官方文档](https://developers.cloudflare.com/fundamentals/account/find-account-and-zone-ids/)。

![在Cloudflare搜索并复制Account ID](https://tenfy.cn/picture/img-hub-cloudflare-account-id.webp)

*图 10：Cloudflare 全局搜索中的 **Copy account ID**。这里需要的是 Account ID，不是 Zone ID，也不是邮箱或账号名称。*

# 第七步：配置 GitHub Actions Secrets

回到你 Fork 的仓库，进入：

```text
Settings → Secrets and variables → Actions
```

选择 **Secrets** 页签，然后点击 **New repository secret**。

![GitHub Actions的Secrets与Variables](https://tenfy.cn/picture/img-hub-github-actions-secrets.png)

*图 11：GitHub Actions 把敏感信息放在 Secrets，把可以公开的普通配置放在 Variables。Token 必须放在 Secrets，不能放在 Variables。*

连续创建下面两个 Repository Secret，名称必须一字不差：

| Secret 名称 | 填写内容 |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | 上一步只显示一次的 Cloudflare API Token |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Account ID |

保存 Secret 后，GitHub 不会再显示它的明文，这是正常现象。不要把 Token 填成 Secret 名称，也不要在值前后加引号或空格。

## 自定义域名用户再加一个 Variable

如果准备使用 `img.example.com`，切换到 **Variables** 页签，创建一个 Repository Variable：

| Variable 名称 | 示例值 |
| --- | --- |
| `IMG_HUB_TURNSTILE_DOMAINS` | `img.example.com` |

这个变量会把自定义域名加入 ImgHub 管理的 Turnstile Widget，确保登录保护能在自定义域名下正常工作。只使用 `workers.dev` 地址时可以不填。

> `IMG_HUB_TURNSTILE_DOMAINS` 只负责 Turnstile 授权，不会自动把域名连接到 Worker。真正的域名绑定还要在部署成功后完成，后文会继续操作。

# 第八步：运行 Deploy to Cloudflare 工作流

打开 Fork 仓库的 **Actions** 页。在左侧选择 **Deploy to Cloudflare**。

然后点击右侧 **Run workflow**：

1. 分支选择 `main`。
2. 再点击弹出区域中的绿色 **Run workflow** 按钮。

![手动运行GitHub工作流](https://tenfy.cn/picture/img-hub-github-actions-deploy-workflow.jpg)

*图 12：ImgHub 的真实 Actions 页面。先在左侧选择 **Deploy to Cloudflare**，再点击右侧红框中的 **Run workflow**。该工作流已经配置好，不需要修改 `deploy.yml`。*

等待工作流运行。它会依次：

1. 安装 Node.js 22 和项目依赖。
2. 运行本地完整测试和部署检查。
3. 检查两个 Cloudflare Secrets 是否存在。
4. 创建或复用 D1、R2 和 managed Turnstile Widget。
5. 初始化数据库表结构。
6. 部署 Worker、静态页面、每天运行的文件保留任务和 Turnstile Secret。

工作流前面测试通过、最后出现绿色对勾才算成功。打开 `Initialize D1, R2, and Turnstile, then deploy` 这一步的日志，可以找到生成的 `workers.dev` 地址。

如果日志出现下面这句话：

```text
Cloudflare deployment skipped. Add CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID repository secrets.
```

说明测试通过了，但至少有一个 Secret 没有配置成功。回到仓库的 Secrets 页面检查名称和位置。

# 第九步：把自定义域名绑定到 ImgHub Worker

部署成功后进入 Cloudflare 的 **Workers & Pages**，打开刚创建的 ImgHub Worker。默认资源名称带有 `img-hub-` 和当前 Fork 的仓库 ID，也可以从 GitHub Actions 日志确认准确名称。

![Cloudflare Workers概览页面](https://tenfy.cn/picture/img-hub-cloudflare-workers-overview.webp)

*图 13：Cloudflare Workers 概览页可以查看请求量、错误、版本和 Binding。找到刚刚由 GitHub Actions 创建的 ImgHub Worker 后进入它的设置。*

依次点击：

```text
Settings → Domains & Routes → Add → Custom Domain
```

输入：

```text
img.example.com
```

然后点击 **Add Custom Domain**。

![为Cloudflare Worker添加自定义域名](https://tenfy.cn/picture/img-hub-cloudflare-worker-custom-domain.webp)

*图 14：Custom Domain 会把整个主机名交给这个 Worker。Cloudflare 会自动创建所需 DNS 记录并签发 HTTPS 证书，不需要再手工添加 CNAME。截图中的域名只是官方示例。*

根据 [Cloudflare Custom Domains 文档](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)，目标域名必须属于当前 Cloudflare 账号中已经激活的 Zone。如果 `img.example.com` 已有同名 CNAME，先确认它不再使用，再删除冲突记录后重试。

等状态变为 Active 后，打开：

```text
https://img.example.com
```

如果你忘记提前配置 `IMG_HUB_TURNSTILE_DOMAINS`，现在回 GitHub 添加该 Variable，然后重新运行一次 **Deploy to Cloudflare**。重新部署会复用已有 D1 和 R2，不会因为正常重跑而清空数据。

# 第十步：立即初始化管理员

第一次打开全新部署时，ImgHub 会让你设置管理员密码：

- 管理员用户名固定为 `admin`。
- 密码长度为 10–256 个字符。
- 没有默认密码，也没有邮件找回密码功能。

请使用密码管理器生成并保存强密码。部署完成后应立即初始化管理员，在初始化结束前不要把站点地址公开给其他人，因为第一个成功完成初始化的人会创建这个部署的唯一管理员。

登录后可以：

1. 在 **站点设置** 中修改标题、欢迎文案和 R2 文件保留天数。
2. 在 **用户管理** 中创建普通用户并生成临时密码。
3. 上传一张测试图片。
4. 复制形如 `/pub/7b62...?v=1` 的公开链接，在无痕窗口中确认可以访问。

管理员创建的普通用户第一次登录后必须修改临时密码，之后才能上传和管理自己的内容。

# 上线检查清单

按顺序确认下面每一项：

- [ ] Spaceship 中域名状态正常，没有过期风险。
- [ ] Cloudflare 中根域名状态为 Active。
- [ ] GitHub Fork 的 Actions 已启用。
- [ ] `CLOUDFLARE_API_TOKEN` 和 `CLOUDFLARE_ACCOUNT_ID` 位于 Repository Secrets。
- [ ] 自定义域名已写入 `IMG_HUB_TURNSTILE_DOMAINS` Repository Variable。
- [ ] **Deploy to Cloudflare** 全部步骤为绿色。
- [ ] `workers.dev` 地址能够打开。
- [ ] Worker 的 Custom Domain 状态为 Active。
- [ ] `https://img.example.com` 能打开，并且浏览器没有证书警告。
- [ ] 已立即完成 `admin` 初始化并保存密码。
- [ ] 测试文件上传成功，公开链接能在无痕窗口访问。

# 常见问题排查

## Cloudflare 一直显示 Pending Nameserver Update

回到 Spaceship 检查两个 NS 是否逐字一致，确认没有保留旧 Nameserver，并确认更换前已经关闭旧 DNSSEC。修改后可能需要等待，Spaceship 官方给出的最长传播时间是 48 小时。

熟悉命令行的话，可以查询：

```sh
dig NS example.com
```

结果应该出现 Cloudflare 分配的两个 Nameserver。

## GitHub 中没有 Run workflow 按钮

确认以下三点：

1. 这是你自己的 Fork，不是上游原仓库。
2. Fork 的 Actions 已经启用。
3. 当前查看的是 **Deploy to Cloudflare**，并且 `main` 分支中存在 `.github/workflows/deploy.yml`。

## Workflow 成功，但没有部署任何东西

查看 **Check Cloudflare configuration** 步骤。如果显示 `deployment skipped`，说明两个 Repository Secret 至少缺少一个，或者 Secret 被错误地创建到了 Variables 中。

## Workflow 报 403 或权限不足

重新检查 Cloudflare Token 的七项权限、**Specific account** 范围，以及 `CLOUDFLARE_ACCOUNT_ID` 是否属于同一个账号。不要用 Zone ID 代替 Account ID。

## 第一次部署提示需要创建 workers.dev 子域名

全新的 Cloudflare 账号可能还没有初始化 `workers.dev` 子域名。先登录 Cloudflare，打开一次 **Workers & Pages** 首页；按照 [Cloudflare 官方说明](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/)，账号会在这里创建可配置的 `workers.dev` 子域名。完成后回 GitHub 重新运行部署工作流。如果第一次访问 `workers.dev` 暂时出现 523，可以等待一两分钟后刷新。

## workers.dev 能打开，自定义域名打不开

检查：

1. 根域名在 Cloudflare 中是否为 Active。
2. Worker 的 **Domains & Routes** 中是否真的添加了 `img.example.com`。
3. DNS 中是否存在同名冲突记录。
4. HTTPS 证书是否仍在签发中。

## 自定义域名能打开，但登录验证失败

检查 GitHub Repository Variable `IMG_HUB_TURNSTILE_DOMAINS` 是否等于完整主机名 `img.example.com`，不要加 `https://` 或路径。改好后重新运行部署工作流。

## 如何同步 ImgHub 后续更新？

进入自己的 Fork，点击 **Sync fork → Update branch**。保持 `main` 分支不做自己的代码修改最省心。上游更新同步到 `main` 后会再次触发部署，而你 Fork 中的 GitHub Secrets 不会被上游覆盖。

# 安全提醒

最后再强调几条：

1. 不要把 Cloudflare Token 写进代码、Issue、聊天记录或截图。
2. 不要使用 Global API Key，Token 权限只给当前部署真正需要的七项。
3. GitHub Secret 保存后看不到明文是正常的，不要为了“方便查看”改成 Variable。
4. 域名、Cloudflare、GitHub 和 ImgHub 管理员都应使用不同密码，并开启两步验证。
5. R2 中的文件和 D1 中的元数据都属于自己的重要数据，正式使用后要制定备份方案。
6. 不要随便运行仓库里的 **DESTRUCTIVE: Destroy Cloudflare deployment**，它会永久删除 Worker、R2 文件、D1 数据库和 Turnstile Widget，而且不会自动备份。

至此，一个拥有自定义域名、由 GitHub Actions 自动部署的 ImgHub 就上线了。以后更新 ImgHub 时，只需要同步 Fork；日常上传和用户管理都可以直接在网页中完成。

# 参考资料

- [ImgHub 中文 README](https://github.com/tenfyzhong/img-hub/blob/main/README.zh-CN.md)
- [Spaceship：连接第三方 Nameserver](https://www.spaceship.com/en-GB/knowledgebase/connect-domain-custom-nameservers/)
- [Cloudflare：将域名接入 Cloudflare](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/)
- [Cloudflare：创建 API Token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [Cloudflare：查找 Account ID](https://developers.cloudflare.com/fundamentals/account/find-account-and-zone-ids/)
- [Cloudflare Workers：Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/)
- [GitHub：Fork 仓库](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo)
- [GitHub Actions：使用 Secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
- [GitHub Actions：手动运行工作流](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
