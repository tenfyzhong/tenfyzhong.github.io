---
title: 用 espanso 给 Codex 补回 prompt 入口：skill/snippet 工作流实战
date: 2026-04-07T20:30:00+08:00
categories:
  - "人工智能"
tags:
  - "codex"
  - "espanso"
  - "snippet"
  - "ai"
  - "tools"
keywords: codex,espanso,snippet,skill,prompt
---

最近在用 Codex 的时候，我碰到一个很现实的问题：现在官方更提倡用 `skill` 来承载工作流能力，但不像以前那样可以直接依赖 slash command 作为调用入口。

这带来的变化是，`skill` 解决的是“怎么做”，却没有顺手解决“我怎么快速把这个意图发出去”。如果每次都手写 prompt，不仅麻烦，还很容易出现同一个动作每次描述都不一样的问题。于是我开始找一个更轻量的办法，把这些高频 prompt 固化下来，最后选了 [espanso](https://espanso.org/)。

这篇文章不打算把 espanso 写成一份全量教程，而是集中回答一个问题：在没有 slash command 之后，怎么用 `skill + prompt snippet + espanso` 这套组合，把 Codex 的常用操作重新变成低摩擦入口。

<!-- more -->

# 背景：没有 slash command 之后，问题变成了 prompt 入口

如果你已经在用 Codex，大概率已经接受了一个事实：很多能力现在是通过 `skill` 来组织的。这样做有明显好处，`skill` 可以把流程、约束和上下文组织好，比零散的命令更稳定。

但 `skill` 本身并不是一个触发器。

它更像是“这件事应该怎么做”的说明书，而不是“我现在一键发起这件事”的按钮。以前有 slash command 的时候，入口和能力比较接近；现在没有了，你仍然需要一段 prompt 去把这件事叫起来。

如果这类 prompt 需要高频重复输入，那么很快就会出现两个问题：

1. 每次手敲很浪费时间。
2. 同一个意图反复手写，表达容易漂移。

于是问题就清晰了：`skill` 依然有价值，但还需要一个 prompt 入口层。而文本展开工具，正好适合补这层能力。

# `skill`、prompt snippet 和 `espanso` 的关系

在这套工作流里，我会把三者分成三个层次来理解。

## 1. `skill` 负责“怎么做”

`skill` 的职责是定义流程、边界和推荐做法。比如创建 PR、分析问题、整理信息，这些动作本身可以由 `skill` 约束成一套稳定流程。

它解决的是方法问题。

## 2. prompt snippet 负责“怎么叫它做”

即使已经有了 `skill`，你仍然需要给 Codex 发出一个明确请求。这个请求如果经常重复，就很适合固化成 snippet。

比如：

- `创建PR`
- `根据上下文，使用英文创建issue`
- `提交代码`

这些都不复杂，但问题在于它们会高频重复出现。只要是高频重复文本，就值得被 snippet 化。

## 3. `espanso` 负责“把 snippet 变成随手可用的触发词”

`espanso` 本质上是一个系统级文本展开工具。你定义一个 trigger，它就能在输入时自动替换成你想要的文本。

放到 Codex 这个场景里，它的作用非常直接：

- 把常用 prompt 固定下来
- 保持输入的一致性
- 让触发动作变短
- 支持把多个小 snippet 再组合成一个更完整的 prompt

所以这三者的分工可以简化成一句话：

- `skill` 定义能力
- prompt snippet 定义入口文本
- `espanso` 把入口文本变成可复用触发词

# 安装与启动

本文以 macOS 为主，Linux/Windows 也能用，只是安装方式和路径会不同。

在 macOS 上，我直接用 Homebrew 安装：

```bash
brew install --cask espanso
```

安装后，把 espanso 注册并启动起来：

```bash
espanso service register
espanso service start
espanso service status
```

如果状态正常，你会看到类似 `espanso is running` 的输出。

接着用下面这个命令确认配置目录：

```bash
espanso path
```

我这边的输出是：

```text
Config: ~/.config/espanso
Packages: ~/.config/espanso/match/packages
Runtime: ~/Library/Caches/espanso
```

所以下面的示例都会以 `~/.config/espanso` 为基础来讲。你自己的路径如果不同，以 `espanso path` 的输出为准，不要死记硬背路径。

# 只在 Ghostty 里启用 Codex prompt snippet

这是我觉得这套方案里很实用的一点。

我并不希望这些用于 Codex 的 prompt trigger 在所有应用里都生效，因为它们本质上是终端工作流的一部分。更合适的做法，是只在自己常用的终端里启用。

我的做法是给 Ghostty 单独放一个配置文件：

`~/.config/espanso/config/ghostty.yml`

```yaml
filter_exec: "Ghostty"
extra_includes:
  - "../match/_prompt.yml"
```

这里有两个关键点：

1. `filter_exec: "Ghostty"` 表示这个配置只在 Ghostty 进程里生效。
2. `extra_includes` 把 `../match/_prompt.yml` 这个文件引进来，也就是只在 Ghostty 里加载这组 prompt snippet。

这样做有两个好处：

- 不会把这些 trigger 污染到所有应用
- 你可以把 Codex 相关 snippet 单独放在一个文件里维护

如果你用的不是 Ghostty，而是别的终端，那么思路是一样的：给对应终端写一个 app-specific config，然后把 `extra_includes` 指向你的 prompt 配置文件。

# `_prompt.yml` 配置示例

接下来是正文重点。

我把 Codex 常用的 prompt snippet 单独放在：

`~/.config/espanso/match/_prompt.yml`

内容如下：

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/espanso/espanso/dev/schemas/match.schema.json

matches:
  - trigger: ":pr"
    replace: "创建PR"

  - trigger: ":issue"
    replace: "根据上下文，使用英文创建issue"

  - trigger: ":ipr"
    replace: "{{issue}}，并且{{pr}}关联这个issue"
    vars:
      - name: issue
        type: match
        params:
          trigger: :issue
      - name: pr
        type: match
        params:
          trigger: :pr

  - trigger: ":cm"
    replace: "提交代码"
```

这四个 trigger 已经能覆盖不少高频动作了。

## `:pr`

展开成：

```text
创建PR
```

适合在你已经整理好上下文之后，让 Codex 直接进入创建 PR 的动作。

## `:issue`

展开成：

```text
根据上下文，使用英文创建issue
```

这个适合把 issue 的语言、动作和上下文依赖一次说清楚。对于需要英文 issue 的项目，这种固定写法比每次手敲更稳定。

## `:cm`

展开成：

```text
提交代码
```

虽然看起来很短，但短并不代表没必要做成 snippet。只要你会高频打这句话，它就值得被缩短。

## `:ipr`

这是这份配置里最有意思的一条。

它不是简单写死一整段文本，而是复用了前面两个 snippet：

- `issue`
- `pr`

最后组合成：

```text
根据上下文，使用英文创建issue，并且创建PR关联这个issue
```

这也是我为什么会选 espanso 的原因之一。它不只是做“固定文本替换”，还可以把已有 snippet 再拼成更高层的一条指令。这样你不用复制粘贴一长串 prompt，也不用在多个地方维护重复文本。

从维护角度看，这种组合方式有明显好处：

- 小 prompt 可以复用
- 改一处就能影响组合 prompt
- 高阶触发词不会变得越来越难维护

# 在 Codex 里的使用方式

有了上面的配置之后，日常使用就会很直接。

## 场景 1：创建 issue

在 Ghostty 里的 Codex 会话中输入：

```text
:issue
```

它会展开成：

```text
根据上下文，使用英文创建issue
```

这时候你再补充一两句上下文，Codex 就能直接开始处理。

## 场景 2：创建 PR

输入：

```text
:pr
```

展开后再补充一句“基于当前改动”或者“根据当前分支上下文”，通常就已经够用。

## 场景 3：先建 issue，再建 PR 并关联 issue

这个是我觉得最适合 snippet 化的场景，因为它本来就属于重复但稍微复杂一点的 prompt。

输入：

```text
:ipr
```

它会直接变成组合后的 prompt。这样你不需要每次都重新组织那句“先建 issue，再建 PR，并且把两者关联起来”的表达。

从工作流角度看，这种 snippet 很适合两类任务：

- 你已经知道自己要做什么，只是不想重复输入
- 你希望常见动作的 prompt 尽量标准化

# 验证与排查

配置完之后，建议先验证一下它是不是按你预期加载了。

因为我这里是把 `_prompt.yml` 只挂在 Ghostty 里，所以我会用下面这个命令检查：

```bash
espanso match list --exec Ghostty
```

在我这边，可以看到：

```text
:pr - 创建PR
:issue - 根据上下文，使用英文创建issue
:ipr - {{issue}}，并且{{pr}}关联这个issue
:cm - 提交代码
```

这里要注意一下，`espanso match list` 展示的是匹配定义本身，所以像 `:ipr` 这样的组合 snippet 仍然会显示 `{{issue}}`、`{{pr}}` 这种模板写法。真正输入 trigger 时，espanso 才会把它展开成最终文本。

这里有一个很容易踩坑的点：

如果你只写了 `match/_prompt.yml`，但没有在对应应用的 config 里通过 `extra_includes` 引进来，那么这些 trigger 不一定会出现在你当前应用里。

也就是说，下面两个文件要配合起来看：

- `~/.config/espanso/config/ghostty.yml`
- `~/.config/espanso/match/_prompt.yml`

如果触发词没有生效，可以优先检查这几项：

1. `espanso service status` 是否显示正在运行
2. `espanso path` 输出的目录是不是你正在编辑的那个目录
3. 对应终端的 config 是否通过 `extra_includes` 引入了 `_prompt.yml`
4. `espanso match list --exec <你的终端名>` 能不能列出这些 trigger

# 总结

没有 slash command 之后，真正缺的不是“能力”，而是“入口”。

`skill` 负责把流程定义好，但你仍然需要一种低摩擦的方式把这些意图发出去。对我来说，`espanso` 正好补上了这层入口：把常用 prompt 做成 snippet，再用 trigger 快速展开。

如果你也在用 Codex，我建议不要一开始就设计一大套复杂 prompt。先把最高频的几个动作固定下来就够了，比如：

- `:issue`
- `:pr`
- `:ipr`
- `:cm`

等这套最小配置跑顺了，再继续往上长。这样你得到的不是一堆看起来很高级的配置，而是一套真的能每天省时间的工作流。
