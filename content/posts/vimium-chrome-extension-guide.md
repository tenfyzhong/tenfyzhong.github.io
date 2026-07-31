---
title: "Vimium Chrome 插件完整使用教程：68 个默认 Key Mapping 全解"
date: 2026-07-31T17:52:15+08:00
categories:
  - "工具"
tags:
  - "vimium"
  - "chrome-extension"
  - "keyboard-shortcuts"
keywords: "Vimium, Chrome 插件, Key Mapping, 键盘快捷键, Vimium 教程"
---

浏览网页时，鼠标最常打断节奏的地方通常不是复杂操作，而是滚动页面、点链接、切换标签页和回到输入框。Vimium 把这些动作变成了一套接近 Vim 的键盘操作：按 `j`、`k` 滚动，用 `f` 点击页面上的链接，用 `J`、`K` 切换标签页。

这篇文章基于 Chrome 中 Vimium 2.4.2 的 `Vimium Commands` 页面整理，完整收录该版本的 **68 条默认 Key Mapping**，同时列出 **10 个默认没有绑定快捷键的命令**。除了查表，我也会说明 Vimium 的模式、按键写法、常用工作流和自定义配置方法。

<!-- more -->

# Vimium 是什么？

[Vimium](https://github.com/philc/vimium) 是一个用键盘操作浏览器的 Chrome 扩展。它借用了 Vim 的按键习惯，但不要求你先学会 Vim：只要记住滚动、链接提示和标签页管理这三组快捷键，就已经能覆盖大部分日常浏览操作。

可以从 [Chrome 应用商店](https://chromewebstore.google.com/detail/vimium/dbepggeogbaibhgnhhndojpepiihcmeb) 安装。安装完成后，建议先打开任意普通网页，再按 `?`。Vimium 会显示当前生效的快捷键帮助。

完整命令页可以在 Chrome 地址栏中打开：

```text
chrome-extension://dbepggeogbaibhgnhhndojpepiihcmeb/pages/command_listing.html
```

这个页面不只显示默认快捷键，还会根据你的自定义 Key Mapping 更新命令旁边的按键。

# 先看懂 Vimium 的按键写法

Vimium 区分大小写，也区分“依次按下”和“同时按下”。

| 写法 | 实际操作 |
| --- | --- |
| `j` | 按一次小写 `j` |
| `G` | 按 `Shift + g`，得到大写 `G` |
| `gg` | 连续按两次 `g`，不是同时按 |
| `gU` | 先按 `g`，再按 `Shift + u` |
| `<c-e>` | 同时按 `Ctrl + e` |
| `<a-f>` | 同时按 `Alt + f`；macOS 上的 `Alt` 就是 `Option（⌥）` |
| `<m-x>` | 同时按 `Meta + x`；macOS 上通常对应 `Command（⌘）` |
| `<s-tab>` | 同时按 `Shift + Tab` |

多按键序列不需要追求很快，只要不要在中间插入无关按键即可。许多可重复命令还支持数字前缀，例如 `5j` 向下滚动 5 次、`3x` 连续关闭 3 个标签页。

# 最重要的三个使用方式

在查看完整表格前，可以先掌握最常用的三个入口。

## 1. 用 `j`、`k` 浏览长页面

- `j` 向下滚动，`k` 向上滚动。
- `d` 向下滚动半页，`u` 向上滚动半页。
- `gg` 回到顶部，`G` 到达底部。

它们与 Vim 的移动习惯一致，也是最容易形成肌肉记忆的一组键。

## 2. 用 `f` 点击链接

按下 `f` 后，Vimium 会在可点击元素旁显示一组提示字符。继续输入目标提示字符，就等于用鼠标点击该元素。

- `f`：在当前标签页打开。
- `F`：在新标签页打开。
- `yf`：不打开链接，只复制 URL。
- `Alt + f`：进入队列模式，连续选择多个链接并在新标签页打开。

提示字符不是下面完整映射表中的固定快捷键，而是 Vimium 根据当前页面临时生成的。

## 3. 用 `J`、`K` 和 `x` 管理标签页

- `J` 切到左侧标签页，`K` 切到右侧标签页。
- `x` 关闭当前标签页，`X` 恢复刚关闭的标签页。
- `T` 搜索所有已打开的标签页，标签页很多时比逐个切换更快。

# 全部默认 Key Mapping

下面的表格基于 Vimium 2.4.2 的默认配置整理。命令名与 `Vimium Commands` 页面保持一致，后面自定义快捷键时可以直接使用。

## 页面滚动

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `j` | `scrollDown` | 向下小幅滚动 |
| `k` | `scrollUp` | 向上小幅滚动 |
| `h` | `scrollLeft` | 向左滚动 |
| `l` | `scrollRight` | 向右滚动 |
| `gg` | `scrollToTop` | 滚动到页面顶部 |
| `G` | `scrollToBottom` | 滚动到页面底部 |
| `zH` | `scrollToLeft` | 滚动到页面最左侧 |
| `zL` | `scrollToRight` | 滚动到页面最右侧 |
| `<c-e>` | `scrollDown` | 向下小幅滚动，与 `j` 作用相同 |
| `<c-y>` | `scrollUp` | 向上小幅滚动，与 `k` 作用相同 |
| `d` | `scrollPageDown` | 向下滚动半页 |
| `u` | `scrollPageUp` | 向上滚动半页 |

`h`、`l`、`zH` 和 `zL` 只会在页面存在横向滚动区域时表现出明显效果。

## 页面操作、URL 与模式

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `r` | `reload` | 正常刷新当前页面 |
| `R` | `reload` | 强制刷新并绕过浏览器缓存；默认附带 `hard` 选项 |
| `yy` | `copyCurrentUrl` | 复制当前页面 URL |
| `p` | `openCopiedUrlInCurrentTab` | 把剪贴板中的 URL 在当前标签页打开 |
| `P` | `openCopiedUrlInNewTab` | 把剪贴板中的 URL 在新标签页打开 |
| `gi` | `focusInput` | 聚焦页面中的第一个文本输入框 |
| `[[` | `goPrevious` | 跟随标记为 previous 或 `<` 的上一页链接 |
| `]]` | `goNext` | 跟随标记为 next 或 `>` 的下一页链接 |
| `gf` | `nextFrame` | 把操作焦点切到页面中的下一个 frame |
| `gF` | `mainFrame` | 把操作焦点切回页面的主 frame |
| `gu` | `goUp` | 沿 URL 层级向上一级 |
| `gU` | `goToRoot` | 回到当前 URL 的站点根路径 |
| `i` | `enterInsertMode` | 进入插入模式，让按键交给网页处理 |
| `v` | `enterVisualMode` | 进入可视模式，按字符选择文本 |
| `V` | `enterVisualLineMode` | 进入可视行模式，按行选择文本 |

`gu` 和 `gU` 的区别可以用这个地址说明：

```text
https://example.com/docs/guide/start
```

按一次 `gu` 会向上一级，例如进入 `/docs/guide/`；按 `gU` 则直接回到 `https://example.com/`。

插入模式适合网页编辑器、游戏或拥有自己快捷键的 Web 应用。按 `Esc` 或 `Ctrl + [` 可以退出并回到 Vimium 的普通模式。光标已经位于输入框时，Vimium 通常也会自动把普通字符交给输入框。

## 链接提示

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `f` | `LinkHints.activateMode` | 显示链接提示，在当前标签页打开目标 |
| `F` | `LinkHints.activateModeToOpenInNewTab` | 显示链接提示，在新标签页打开目标 |
| `<a-f>` | `LinkHints.activateModeWithQueue` | 连续选择多个目标，并在新标签页打开 |
| `yf` | `LinkHints.activateModeToCopyLinkUrl` | 显示链接提示并复制目标 URL，不打开链接 |

`f` 不只识别普通链接，也能识别按钮、输入框等可点击元素。队列模式选择完多个目标后，可以按 `Esc` 结束。

## 页面内查找

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `/` | `enterFindMode` | 进入页面内查找模式 |
| `n` | `performFind` | 跳到下一个匹配结果 |
| `N` | `performBackwardsFind` | 跳到上一个匹配结果 |
| `*` | `findSelected` | 向后查找当前选中的文本 |
| `#` | `findSelectedBackwards` | 向前查找当前选中的文本 |

按 `/` 后输入关键字，再按 `Enter` 确认；按 `Esc` 取消。这里的 `*` 和 `#` 需要页面上已经存在选中文本，通常可以先用鼠标选择，或者配合 Vimium 的可视模式使用。

## Vomnibar：打开网址、历史、书签和标签页

Vomnibar 是 Vimium 自带的命令输入框，作用类似 Chrome 地址栏，但可以直接从网页中唤起。

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `o` | `Vomnibar.activate` | 搜索并在当前标签页打开 URL、书签或历史记录 |
| `O` | `Vomnibar.activateInNewTab` | 搜索 URL、书签或历史记录，在新标签页打开 |
| `T` | `Vomnibar.activateTabSelection` | 搜索并切换到已打开的标签页 |
| `b` | `Vomnibar.activateBookmarks` | 搜索书签，在当前标签页打开 |
| `B` | `Vomnibar.activateBookmarksInNewTab` | 搜索书签，在新标签页打开 |
| `ge` | `Vomnibar.activateEditUrl` | 编辑当前 URL，并在当前标签页打开 |
| `gE` | `Vomnibar.activateEditUrlInNewTab` | 编辑当前 URL，并在新标签页打开 |

打开 Vomnibar 后直接输入关键词，用方向键选择结果，按 `Enter` 打开，按 `Esc` 关闭。`T` 是处理大量标签页时非常实用的命令：输入标题或 URL 的一部分，就能快速跳到目标标签页。

## 浏览历史

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `H` | `goBack` | 后退到当前标签页的上一条历史记录 |
| `L` | `goForward` | 前进到下一条历史记录 |

这里的 `H`、`L` 是大写字母，分别需要按 `Shift + h` 和 `Shift + l`。小写 `h`、`l` 用于横向滚动。

## 标签页与缩放

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `K` | `nextTab` | 切换到右侧标签页 |
| `J` | `previousTab` | 切换到左侧标签页 |
| `gt` | `nextTab` | 切换到右侧标签页，与 `K` 作用相同 |
| `gT` | `previousTab` | 切换到左侧标签页，与 `J` 作用相同 |
| `^` | `visitPreviousTab` | 回到最近访问过的上一个标签页 |
| `<<` | `moveTabLeft` | 把当前标签页向左移动 |
| `>>` | `moveTabRight` | 把当前标签页向右移动 |
| `g0` | `firstTab` | 切换到第一个标签页 |
| `g$` | `lastTab` | 切换到最后一个标签页 |
| `W` | `moveTabToNewWindow` | 把当前标签页移动到一个新窗口 |
| `t` | `createTab` | 新建标签页 |
| `yt` | `duplicateTab` | 复制当前标签页 |
| `x` | `removeTab` | 关闭当前标签页 |
| `X` | `restoreTab` | 恢复最近关闭的标签页 |
| `<a-p>` | `togglePinTab` | 固定或取消固定当前标签页 |
| `<a-m>` | `toggleMuteTab` | 静音或取消静音当前标签页 |
| `zi` | `zoomIn` | 放大页面 |
| `zo` | `zoomOut` | 缩小页面 |
| `z0` | `zoomReset` | 恢复默认缩放比例 |

`^` 表示按 `Shift + 6`。它不是简单切到左侧标签页，而是在当前标签页和最近访问的标签页之间来回跳转。

`<<` 和 `>>` 都是连续输入两个字符。在常见英文键盘布局上，分别相当于按两次 `Shift + ,` 和两次 `Shift + .`。

## 标记

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `m` | `Marks.activateCreateMode` | 创建一个位置标记 |
| `` ` `` | `Marks.activateGotoMode` | 跳转到已有标记 |

创建标记时，先按 `m`，再输入一个字母。例如 `ma` 创建标记 `a`，之后输入 `` `a`` 就能跳回来。

- 小写字母创建当前标签页内的本地标记。
- 大写字母创建可以跨标签页使用的全局标记。

标记适合长文档：看到需要稍后回看的位置时按 `ma`，浏览其他章节后再用 `` `a`` 返回。

## 其他命令

| 按键 | 命令 | 作用 |
| --- | --- | --- |
| `?` | `showHelp` | 显示当前生效的快捷键帮助 |
| `gs` | `toggleViewSource` | 查看当前页面源代码 |

`?` 展示的是你当前实际生效的映射，因此修改配置后，优先以这个帮助窗口为准。

# 10 个默认未绑定的命令

`Vimium Commands` 页面还列出了 10 个没有默认 Key Mapping 的命令。它们不是不能使用，而是需要先在 Vimium Options 中自行绑定。

| 命令 | 作用 |
| --- | --- |
| `scrollFullPageDown` | 向下滚动一整页 |
| `scrollFullPageUp` | 向上滚动一整页 |
| `passNextKey` | 把接下来的一个按键原样交给网页 |
| `LinkHints.activateModeToOpenInNewForegroundTab` | 在新标签页打开链接并立即切换过去 |
| `LinkHints.activateModeToDownloadLink` | 下载链接指向的资源 |
| `LinkHints.activateModeToOpenIncognito` | 在无痕窗口中打开链接 |
| `closeTabsOnLeft` | 关闭当前标签页左侧的所有标签页 |
| `closeTabsOnRight` | 关闭当前标签页右侧的所有标签页 |
| `closeOtherTabs` | 关闭当前标签页以外的所有标签页 |
| `setZoom` | 把页面缩放比例设置为指定值，范围为 `0.25` 到 `5.0` |

其中关闭一侧或其他标签页的命令影响范围较大，绑定时最好选择不容易误触的多键序列。

# 自定义 Key Mapping

点击 Chrome 工具栏中的 Vimium 图标，进入 `Options`，找到 `Custom key mappings`。也可以直接打开：

```text
chrome-extension://dbepggeogbaibhgnhhndojpepiihcmeb/pages/options.html
```

最常用的配置语法有四种：

```text
map 按键 命令 [选项]
unmap 按键
unmapAll
mapKey 原按键 目标按键
```

- `map`：把一个按键序列绑定到命令。
- `unmap`：取消某个按键的绑定。
- `unmapAll`：清空所有默认和自定义绑定，适合完全自己配置。
- `mapKey`：把一个单键转换成另一个单键，只支持单个字符。

下面是一份可以直接参考的配置：

```text
# 整页滚动
map D scrollFullPageDown
map U scrollFullPageUp

# 新标签页打开链接并立即切换
map gA LinkHints.activateModeToOpenInNewForegroundTab

# 关闭右侧标签页
map gr closeTabsOnRight

# 设置为 200% 缩放
map z2 setZoom level=2

# 取消容易误触的关闭标签页快捷键
unmap x
```

这里的 `#` 和英文双引号开头的行都可以作为注释。修改完成后点击页面底部的 `Save Changes`，再回到普通网页测试。

同一个按键如果先由默认配置绑定、后面又在自定义配置中重新 `map`，后面的自定义规则会覆盖前面的规则。改乱了也不用逐条恢复：清空自定义文本并保存，就会重新使用默认映射。

# 为特定网站禁用 Vimium

有些网站本身就是键盘应用，例如在线 IDE、终端、游戏、Figma 或其他重度使用快捷键的 Web 应用。让 Vimium 和网站同时监听按键，容易产生冲突。

在 Vimium Options 的 `Excluded URLs and keys` 中可以添加排除规则：

- `Patterns` 填 URL 匹配模式。
- `Keys` 留空时，在匹配页面完全禁用 Vimium。
- `Keys` 填指定按键时，只把这些按键交给网页，其他 Vimium 快捷键仍然可用。

例如，可以针对某个站点只放行 `j`、`k`、`x`，而保留 `f` 和标签页操作。临时需要网页接收下一次按键时，也可以给前面提到的 `passNextKey` 命令设置快捷键。

# 常见问题

## 1. 按快捷键没有反应

先确认焦点是否还在 Chrome 地址栏、开发者工具或网页输入框中。点击一下网页空白处，按 `Esc` 回到普通模式，再试一次。

Chrome 的内部页面、Chrome 应用商店和部分受保护页面不允许普通扩展注入脚本，因此 Vimium 可能无法工作。例如 `chrome://extensions`、`chrome://settings` 这类页面不响应 Vimium 属于正常现象。

## 2. 输入文字时总是触发 Vimium

按 `i` 进入插入模式，或者在 Vimium Options 中为这个网站添加排除规则。完成输入后按 `Esc` 返回普通模式。

## 3. `F` 打开新标签页后为什么没有立即切换？

默认的 `F` 使用 `LinkHints.activateModeToOpenInNewTab`，只负责在新标签页打开。若希望打开后立即切换，需要把一个快捷键绑定到默认未绑定的 `LinkHints.activateModeToOpenInNewForegroundTab`。

## 4. macOS 上的 `<a-f>` 怎么按？

`a` 代表 `Alt`，在 macOS 键盘上对应 `Option（⌥）`，所以 `<a-f>` 就是 `Option + f`。

## 5. 如何确认自己的配置有没有漏掉或覆盖命令？

保存配置后按 `?` 查看当前快捷键，或者重新打开本文开头的 `command_listing.html`。命令页会显示所有可用命令，并把当前绑定的按键列在命令名右侧；没有按键的命令就是当前未绑定。

# 一套容易记住的日常工作流

如果一次记不住 68 条映射，可以先按下面的顺序练习：

1. 用 `j`、`k`、`d`、`u` 浏览页面，用 `gg`、`G` 快速到达两端。
2. 用 `f` 点击，用 `F` 在新标签页打开，用 `yf` 复制链接。
3. 用 `J`、`K` 切换标签页，用 `x` 关闭、`X` 恢复。
4. 用 `/` 查找页面文字，再用 `n`、`N` 前后跳转。
5. 用 `o` 打开网址或历史记录，用 `T` 搜索已打开的标签页。
6. 最后再学习标记、frame、URL 层级和自定义映射。

Vimium 的价值不在于完全消灭鼠标，而是让高频、重复、无需精确定位的浏览器操作回到键盘上。先熟练十来个常用按键，再把真正适合自己的命令绑定进去，通常比一开始强记整张表更有效。
