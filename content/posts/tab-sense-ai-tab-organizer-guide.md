---
title: "Tab Sense：用 AI 一键整理 Chrome 标签页，安装与 Agnes 免费 API 配置教程"
date: 2026-07-30T00:30:00+08:00
categories:
  - "人工智能"
tags:
  - "tab-sense"
  - "chrome-extension"
  - "agnes"
  - "tutorial"
keywords: "Tab Sense, Chrome 标签页, AI 分组, Agnes API, Chrome 插件安装"
---

如果你平时会同时打开很多网页，Chrome 顶部的标签页很快就会挤成一排：工作文档、GitHub、AI 工具、购物页面混在一起，想找刚才看过的内容只能一个个点。

我原本只是想找一个“让 AI 帮我整理标签页”的插件，需求其实很简单：点一下按钮，自动把相同主题的标签页放进同一个分组。可是在插件市场里找了一圈，很多产品都塞进了会话管理、云同步、收藏夹、稍后阅读等大量功能。它们并不是不好，只是对我来说太复杂了。

所以我做了 [Tab Sense](https://github.com/tenfyzhong/tab-sense)：一个专注于标签页去重和 AI 分组的 Chrome 插件。它没有自己的后端，也不要求绑定某一家 AI 服务。你可以使用自己的 API Key，并选择 OpenAI、Anthropic、Google Gemini 或 OpenAI 兼容服务。

这篇文章从零开始，介绍如何下载和安装 Tab Sense，并以目前可以免费使用的 Agnes API 为例完成配置。即使你从来没有手动安装过 Chrome 插件，也可以跟着做。

<!-- more -->

# Tab Sense 能做什么？

Tab Sense 主要解决四件事：

1. **关闭重复标签页**：如果当前窗口中有多个完整 URL 完全相同的页面，只保留一个。
2. **使用 AI 分组**：根据标题和 URL 判断主题，把未分组的标签页整理到 Chrome 标签组中。
3. **全部解除分组**：需要重新整理时，可以把当前窗口里的所有标签页移出分组。
4. **撤销上一次操作**：误操作后可以撤销最近一次去重、AI 分组或解除分组。

它只处理当前 Chrome 窗口。固定的标签页不会被关闭，也不会被 AI 重新分组；已经放进分组的标签页也不会被随意移动。

![Tab Sense 操作面板](https://tenfy.cn/picture/tab-sense-popup.jpg)

插件默认提供两个快捷键：

- `Alt + Shift + D`：关闭重复标签页
- `Alt + Shift + G`：使用 AI 分组

macOS 键盘上的 `Alt` 就是 `Option（⌥）`。如果快捷键与其他软件冲突，可以在 Tab Sense 设置页右上角点击“配置快捷键”修改。

# 第一步：下载 Tab Sense

Tab Sense 暂时没有上架 Chrome 应用商店，需要从 GitHub Release 下载打包好的版本。

插件要求 Chrome 116 或更高版本。如果你的 Chrome 很久没有更新，可以先打开 `chrome://settings/help`，等待浏览器完成版本检查和更新。

打开 [Tab Sense Releases](https://github.com/tenfyzhong/tab-sense/releases)，进入最新版本，在 `Assets` 区域下载名字以 `-chrome.zip` 结尾的文件。本文写作时的最新版本是 `0.1.1`，对应文件名为：

```text
tab-sense-0.1.1-chrome.zip
```

![下载 Tab Sense Chrome 发布包](https://tenfy.cn/picture/tab-sense-release-download.jpg)

不要下载下面的 `Source code (zip)`。它是给开发者看的源代码，不能直接按照本文的方法安装。

下载完成后，双击 ZIP 文件解压。你会得到一个文件夹，里面应该能看到 `manifest.json`、`options.html`、`popup.html` 等文件。

> 请把解压后的文件夹放在一个不会被清理的位置，例如“文稿”目录。安装后不要删除或移动它，否则 Chrome 下次可能无法继续加载插件。

# 第二步：开启 Chrome 开发者模式

在 Chrome 地址栏输入下面的地址并回车：

```text
chrome://extensions
```

这会打开“扩展程序”管理页面。找到页面右上角的“开发者模式”，点击开关把它打开。

开启后，页面左上方会出现三个按钮：“加载未打包的扩展程序”“打包扩展程序”和“更新”。

![开启开发者模式](https://tenfy.cn/picture/tab-sense-chrome-developer-mode.jpg)

开发者模式听起来有点吓人，但这里的作用只是允许 Chrome 加载没有经过应用商店发布的插件。后续更新也需要在这个页面操作。

# 第三步：安装插件

点击“加载未打包的扩展程序”，在弹出的文件选择窗口中，选中刚才**解压后的文件夹**，然后点击“选择”。

注意以下三个容易选错的地方：

- 不能直接选择下载的 ZIP 压缩包。
- 要选择里面含有 `manifest.json` 的文件夹。
- 如果 Chrome 提示找不到清单文件，通常是多选或少选了一层目录。

安装成功后，扩展程序列表中会出现 `Tab Sense`。

为了以后方便使用，可以点击 Chrome 工具栏上的拼图图标，在扩展程序列表里找到 Tab Sense，再点击旁边的图钉。固定以后，工具栏上会一直显示 Tab Sense 图标。

# 第四步：申请 Agnes 免费 API Key

AI 分组需要一个可以调用大模型的 API。这里使用 [Agnes AI](https://agnes-ai.com/) 举例，因为它提供 OpenAI 兼容接口，而且本文写作时 `agnes-2.0-flash` 的输入和输出 Token 当前价格均为 `$0 / 1M tokens`。免费政策和限额可能会调整，请以 [Agnes 官方模型文档](https://agnes-ai.com/zh-Hans/docs/agnes-20-flash) 为准。

先打开 [Agnes 开发者平台](https://platform.agnes-ai.com/)，注册或登录账户，然后进入“设置”里的“API 密钥”页面。

点击“创建新的密钥”，给它起一个容易识别的名字，例如：

```text
tab-sense
```

![在 Agnes 创建 API Key](https://tenfy.cn/picture/agnes-create-api-key.jpg)

创建后复制生成的 API Key。它通常以 `sk-` 开头。

> API Key 就像密码，不要把完整内容发给别人，也不要放进截图、博客或公开代码仓库。如果怀疑已经泄露，请立即回到 Agnes 控制台删除旧密钥并创建新密钥。

# 第五步：在 Tab Sense 中配置 Agnes

点击 Chrome 工具栏上的 Tab Sense 图标，再点击面板右上角的齿轮，进入设置页。

第一次使用时，点击“添加服务商”。按照下面的内容填写：

| 配置项 | 填写内容 |
| --- | --- |
| 服务商名称 | `Agnes 免费 API`，也可以填写其他便于识别的名字 |
| AI 服务商 | `OpenAI Completions` |
| API 基础地址 | `https://apihub.agnes-ai.com/v1` |
| API 密钥 | 粘贴刚才从 Agnes 复制的完整 API Key |

![配置 Agnes OpenAI 兼容接口](https://tenfy.cn/picture/tab-sense-agnes-settings.jpg)

截图为了避免泄露密钥，故意把 API 密钥留空。你实际配置时需要把自己的 Key 粘贴进去。

这里最容易出错的是“AI 服务商”：一定要选择 **OpenAI Completions**，不要选成 `OpenAI Responses`。Agnes 的文本模型使用 OpenAI 兼容的 `/chat/completions` 接口。

填写完成后，按下面的顺序操作：

1. 点击“刷新模型”。
2. Chrome 询问是否允许访问 `apihub.agnes-ai.com` 时，点击允许。
3. 等待模型列表刷新成功。
4. 在“模型”下拉框中选择 `agnes-2.0-flash`。
5. 点击“测试模型”。
6. 看到“模型连接测试成功”后，配置就完成了。

“测试模型”会向 Agnes 发送一个很短的测试请求，用来确认 API Key、地址和模型都能正常工作。

设置页还有“AI 分组前关闭重复标签页”选项。开启后，每次 AI 分组都会先清理重复页面；如果去重失败，插件会停止后续分组。新手可以先保持关闭，熟悉之后再决定是否启用。

# 第六步：让 AI 整理标签页

配置成功后，先在当前窗口打开几个不同主题的网页。例如同时打开几篇 GitHub 文档、几篇 AI 新闻和几个购物页面。

然后点击 Tab Sense 图标，再点击“使用 AI 分组”。插件会立即显示处理状态，完成后，相关页面会被放进带名字的 Chrome 标签组。

AI 分组时有几个规则值得提前知道：

- 只处理当前窗口中未分组、未固定的标签页。
- 如果现有分组适合，优先把标签页加入现有分组，避免创建太多小组。
- 至少两个相关标签页才会创建一个新分组。
- “撤销上次操作”只保留最近一次变更；下一次成功操作会覆盖上一次撤销记录。
- 关闭 Chrome 或浏览器清理会话数据后，撤销记录可能消失。

如果分组不满意，可以先点击“撤销上次操作”，也可以使用“全部解除分组”重新开始。

# 重复标签页是怎么判断的？

“关闭重复标签页”比较的是完整 URL 字符串。查询参数和网页片段不同，也会被当作不同页面。

例如下面两个地址不会被视为重复：

```text
https://example.com/search?q=chrome
https://example.com/search?q=ai
```

如果同一个 URL 有多个标签页，Tab Sense 会优先保留固定标签页；没有固定标签页时，优先保留当前正在看的那个，否则保留最左侧的标签页。

# 隐私方面需要知道什么？

Tab Sense 没有自己的服务器，也不包含广告、分析统计或网页内容脚本。API 请求会从插件直接发送到你配置的 AI 服务商。

进行 AI 分组时，插件会发送必要的标签页信息，包括：

- 标签页标题，最多 200 个字符
- 去掉查询参数和片段后的 URL，最多 500 个字符
- 当前已有分组的名称，以及少量成员标签页信息，用来判断是否可以复用现有分组

插件不会发送网页正文、Cookie、表单内容，也不会上传当前标签页集合之外的浏览历史。完整的数据范围可以查看项目的 [隐私说明](https://github.com/tenfyzhong/tab-sense/blob/main/PRIVACY.md)。

API Key 保存在 Chrome 扩展的本地存储中，不会由 Tab Sense 同步到云端，也不会在设置页面再次显示。不过 Chrome 扩展本地存储并不是加密密码库，因此不要在不可信设备上保存重要密钥。

如果你需要在无痕窗口中使用 Tab Sense，可以在 `chrome://extensions` 中打开 Tab Sense 的“详情”，再开启“在无痕模式下启用”。请注意：普通窗口与无痕窗口会共用同一套服务商配置和 API Key；在无痕窗口运行 AI 分组时，相关标签页标题和处理后的 URL 仍会发送给所选 AI 服务商。

# 常见问题

## 1. 点击“加载未打包的扩展程序”后提示清单文件丢失

你选错了目录。请进入解压后的文件夹，确认里面可以直接看到 `manifest.json`，然后在 Chrome 中选择这一层文件夹。

## 2. “刷新模型”失败

依次检查：

1. “AI 服务商”是否选的是 `OpenAI Completions`。
2. API 基础地址是否完整填写为 `https://apihub.agnes-ai.com/v1`。
3. API Key 前后是否误带了空格。
4. Chrome 弹出服务商访问权限时是否点击了允许。
5. Agnes 服务当前是否正常，账户是否触发了调用限额。

## 3. “使用 AI 分组”按钮是灰色的

当前选中的服务商还没有同时保存 API Key 和模型。回到设置页刷新模型，选中 `agnes-2.0-flash`，再运行一次“测试模型”。

## 4. 插件重启 Chrome 后不见了

检查安装时选择的解压文件夹是否被删除或移动。重新解压发布包，再到 `chrome://extensions` 重新加载即可。

## 5. 如何更新 Tab Sense？

到 [Releases 页面](https://github.com/tenfyzhong/tab-sense/releases) 下载新版本的 `-chrome.zip` 文件并解压。在 `chrome://extensions` 中移除旧版本，再用“加载未打包的扩展程序”选择新文件夹。移除插件会删除它的本地配置，因此更新前请先记好 API 地址和模型，并确认自己仍能在 Agnes 控制台管理或重新创建 API Key。

# 总结

Tab Sense 的设计目标不是取代书签、收藏夹或完整的标签页管理器，而是把最常用的两个动作做简单：清理重复页面，再让 AI 按主题分组。

如果你的 Chrome 经常同时开着几十个标签页，又不想为了一个分组功能安装过于复杂的工具，可以试试 Tab Sense。项目源码、问题反馈和最新版本都在 [GitHub 仓库](https://github.com/tenfyzhong/tab-sense)。
