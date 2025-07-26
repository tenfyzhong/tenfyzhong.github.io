---
title: 告别手写 commit message, gitai-让AI成为你的git贴心助手
date: 2025-07-26T16:24:09+08:00
categories:
  - ai
tags:
  - ai
keywords:
---

作为一名程序员，我们都热爱创造，热衷于用代码改变世界。但不得不承认，在日常的开发流程中，总有一些“烦人”的小事，比如写文档、写注释，以及——写 `git commit` 信息。这些任务虽然重要，但往往会打断我们心流，让人觉得索然无味。

在AI技术日新月异的今天，我们完全可以将这些重复性的文字工作交给AI来完成。今天，我就向大家隆重介绍一款能让你从这些繁琐任务中解脱出来的神器——`gitai`。
<!-- more -->

## `gitai` 是什么？

[gitai](https://github.com/tenfyzhong/gitai) 是一款集成了AI能力的git命令行工具集，它能帮你自动生成 `commit` 信息、创建 `pull request`，甚至是生成 `tag` 的发布说明。它的目标只有一个：将你从繁琐的文字工作中解放出来，让你专注于真正重要的代码创造。

## 依赖配置: `llm`

`gitai` 的强大功能依赖于 [llm](https://github.com/simonw/llm) 这款命令行工具。`llm` 为我们提供了与各种大型语言模型（LLM）交互的统一接口。因此，在使用 `gitai` 之前，我们需要先对 `llm` 进行简单的配置。

### 安装 `llm`

你可以通过 `pip` 或 `brew` 来安装 `llm`：

```bash
# 使用 pip
pip install llm

# 使用 Homebrew
brew install llm
```

### 配置 API Key

`llm` 需要使用 API Key 来访问各大厂商的语言模型。以 OpenAI 为例，你可以通过以下命令配置你的 API Key：

```bash
llm keys set openai
```

然后，根据提示输入你的 OpenAI API Key。

`llm` 也支持其他多种模型，比如 `gemini`, `claude` 等。你可以通过安装相应的插件来使用它们：

```bash
# 安装 gemini 插件
llm install llm-gemini

# 配置 gemini API Key
llm keys set gemini
```

### 选择默认模型

为了方便起见，你可以设置一个默认使用的模型。例如，将 `gpt-4o-mini` 设置为默认模型：

```bash
llm models default gpt-4o-mini
```

这样，`gitai` 在执行时就会默认使用 `gpt-4o-mini` 模型来生成内容。

完成了 `llm` 的配置后，我们就可以开始享受 `gitai` 带来的便利了。

## 安装

安装 `gitai` 非常简单，只需要一行命令：

```bash
brew install tenfyzhong/tap/gitai
```

## `gitai` 的“三板斧”

`gitai` 主要提供了三个核心工具，每一个都能在你的git工作流中发挥巨大作用。

### 1. `ai-commit-msg`: 会呼吸的 `commit` 信息

你是否曾为了一个 `commit` 信息而绞尽脑汁？`ai-commit-msg` 就是你的救星。它是一个 `git hook`，在你执行 `git commit` 时，它会自动分析你的代码变更，并生成一条清晰、规范的 `commit` 信息。

**全局配置 (推荐)**

为了让所有项目都能享受到这个便利，推荐你进行全局配置：

1. 创建全局 `hooks` 目录：

    ```bash
    mkdir -p ~/.git-hooks
    ```

2. 配置 `git` 使用该目录：

    ```bash
    git config --global core.hooksPath ~/.git-hooks
    ```

3. 将 `ai-commit-msg` 链接到 `hooks` 目录：

    ```bash
    ln -s "$(which llm-commit-msg)" ~/.git-hooks/prepare-commit-msg
    ```

配置完成后，你就可以像往常一样使用 `git commit`，`gitai` 会在后台默默为你准备好 `commit` 信息，你只需要检查并保存即可。

**项目内配置**

如果你只想在特定的项目中使用，可以进入项目`.git/hooks`目录，然后执行`ln -s "$(which llm-commit-msg)" ./prepare-commit-msg`。

### 2. `aipr`: 一键生成 `Pull Request`

写 `Pull Request` 的标题和描述同样是一件耗时的事情。`aipr` 工具可以根据你的分支和代码变更，自动为你生成 `Pull Request` 的标题和内容。

**使用方法**

```bash
aipr [options]
```

`aipr` 支持 `gh pr create/edit` 的所有参数，你可以用它来指定目标分支、远程仓库等。比如：

```bash
# 为当前分支创建一个pr, 合并到main分支
aipr -B main
```

`aipr` 会自动为你生成标题和描述，并打开编辑器让你确认。

### 3. `aitag`: 智能生成 `Release Tag`

发布新版本时，需要为 `tag` 编写发布说明。`aitag` 可以帮你自动完成这项工作。它会分析从上一个 `tag` 到现在的代码变更，并生成一份详尽的发布说明。

**使用方法**

```bash
aitag [OPTIONS] TAG_NAME [COMMIT]
```

比如，要创建一个名为 `v1.0.0` 的 annotated tag：

```bash
aitag -a v1.0.0
```

`aitag` 会为你生成 `tag` 的说明，让你的版本发布更加专业。

## 高级定制

`gitai` 还提供了强大的定制功能。你可以通过修改 `~/.config/gitai/prompts` 目录下的 `prompt` 文件，来调整 `gitai` 生成内容的风格和格式，让它更符合你或团队的规范。

同时，`gitai` 也支持通过环境变量进行配置，例如 `GITAI_MODEL`、`GITAI_LANGUAGE` 等，让你对 `gitai` 的行为有更精细的控制。

## 总结

`gitai` 是一款能显著提升 `git` 工作效率的工具。它将AI的强大能力融入到我们日常的开发流程中，让我们从繁琐的文字工作中解放出来。如果你也厌倦了手写 `commit` 信息和 `Pull Request`，不妨试试 `gitai`，让AI成为你的贴心 `git` 助手吧！
