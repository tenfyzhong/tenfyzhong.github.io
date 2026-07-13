---
title: "Codex skill 太多触发 2% 上下文告警：用 Plugin 实现按需加载"
date: 2026-07-13T14:42:34+08:00
categories:
  - "人工智能"
tags:
  - "codex"
  - "plugin"
  - "skill"
  - "context-window"
keywords:
  - codex
  - codex plugin
  - skill
  - lazy loading
  - context budget
---

当 Codex 里安装的 skill 越来越多时，我遇到了下面这个告警：

```text
⚠ Skill descriptions were shortened to fit the 2% skills context budget. Codex can still see every skill, but some descriptions are shorter. Disable unused skills or plugins to leave more room for the rest.
```

它不会让 Codex 直接停止工作，但暴露了一个很实际的问题：skill 数量太多、描述太长时，Codex 为 skill 元数据预留的上下文不够用了。部分 description 被截短后，虽然 skill 仍然可见，隐式触发的准确性却可能下降。

我最后的解决方案不是继续压缩每个 description，而是把同一领域的 skills 收进一个 Codex Plugin，只向 Codex 注册一个轻量的 router skill。用户请求命中 router 后，再扫描插件内部的 skill 元数据，选择并读取真正需要的 `SKILL.md`。

本文会以我做的 [lark-cli-skills Plugin](https://github.com/tenfyzhong/agent-plugins-hub/tree/main/plugins/lark-cli-skills) 为例，拆解这套按需加载方案。

<!-- more -->

## 先理解告警：被挤占的是 skill 元数据预算

根据 [Codex Skills 文档](https://developers.openai.com/codex/concepts/customization#skills)，skill 使用渐进式披露：

1. 启动时先提供 `name` 和 `description`，让 Codex 能发现并选择 skill。
2. 某个 skill 被选中后，才加载完整的 `SKILL.md`。
3. skill 引用的 references 和 scripts 继续按需读取或执行。

所以，严格来说，这个告警不是“所有 `SKILL.md` 正文都被塞进了启动上下文”，而是“所有 skills 的 `name` 和 `description` 超过了 2% 的 skills context budget”。

description 往往不仅写“这个 skill 做什么”，还会写触发条件、排除条件、与相邻 skill 的边界。它一旦被截短，最先损失的通常正是这些路由信息。例如：

- 文档内容编辑走 `lark-doc`
- 云盘文件移动走 `lark-drive`
- 表格数据修改走 `lark-sheets`
- 历史会议查询走 `lark-vc`

这些描述各自都合理，但当系统里存在几十甚至上百个类似 skill 时，它们会共同竞争有限的启动上下文。

## 解决思路：把一层路由改成两层路由

普通的 skill 发现流程是一层结构：

```text
用户请求
  -> Codex 在所有已注册 skill 的 description 中匹配
  -> 加载命中的 SKILL.md
```

我的方案是在同一业务领域内增加一个 router：

```text
用户请求
  -> Codex 只匹配轻量 router skill
  -> router 读取内部 skills 的 name/description/path
  -> router 选择最小可用 skill 集合
  -> 只加载被选中的 SKILL.md
```

这样，Codex 启动时只需要为整个领域保留一条 description。内部 skills 仍然可以保持清晰、完整的边界描述，只是把它们的发现过程推迟到了 router 真正被命中之后。

这里有一个容易混淆的点：这不是在运行时向 Codex 重新注册 skills，而是 router 把未注册的 `SKILL.md` 当作插件内部资源读取，并按照其中的工作流继续执行。它是一种基于文件和指令约定实现的懒加载。

## Plugin 的目录结构

[官方 Plugin 文档](https://developers.openai.com/codex/plugins/build#plugin-structure)规定，每个 Plugin 都需要 `.codex-plugin/plugin.json`，并可以携带 skills、hooks、MCP 配置和其他资源。

`lark-cli-skills` 采用标准的 Plugin 目录约定：把 router 放进 `skills/`，把不参与 Codex 自动发现的具体工作流放进 `internal-skills/`。

```text
lark-cli-skills/
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── lark/
│       ├── SKILL.md
│       └── scripts/
│           └── discover_internal_skills.py
└── internal-skills/
    ├── lark-doc/SKILL.md
    ├── lark-drive/SKILL.md
    ├── lark-calendar/SKILL.md
    ├── lark-task/SKILL.md
    └── ...
```

这样 `skills/lark` 是唯一注册给 Codex 的 skill，27 个具体工作流都留在 `internal-skills/`。

## 第一步：manifest 只注册 router

最关键的配置在 `.codex-plugin/plugin.json`：

```json
{
  "name": "lark-cli-skills",
  "version": "0.2.0",
  "description": "Lazy-loaded official Lark CLI workflows for operating Lark and Feishu from Codex.",
  "skills": "./skills/"
}
```

重点只有这一行：

```json
"skills": "./skills/"
```

manifest 使用标准的 `skills/` 路径，而这个目录里只放 router。具体工作流放在 `internal-skills/`，不会被当成 Plugin 的顶层 skills 自动发现。

实际项目中的 manifest 还应保留作者、界面展示等完整字段，可以直接参考 [lark-cli-skills 的 plugin.json](https://github.com/tenfyzhong/agent-plugins-hub/blob/main/plugins/lark-cli-skills/.codex-plugin/plugin.json)。

## 第二步：用一个短 description 覆盖整个领域

router 的 frontmatter 要覆盖这个 Plugin 的顶层触发范围，同时尽量短。`lark` router 的描述是：

```yaml
---
name: lark
description: "Route Lark and Feishu (飞书) operations to bundled lark-cli workflows on demand. Use for Lark or 飞书 messages, documents, Drive, calendar, meetings, tasks, mail, Base, Sheets, approvals, attendance, OKRs, whiteboards, authentication, events, apps, or OpenAPI work."
---
```

这条 description 不需要解释 `lark-doc` 和 `lark-drive` 的全部边界，只负责回答一个问题：当前请求是否属于 Lark/飞书领域？

router 被选中后，再执行以下流程：

1. 运行 discovery script，读取内部 skills 的 frontmatter。
2. 根据用户的完整意图选择最小的 skill 集合。
3. 完整读取每个被选中的 `SKILL.md`。
4. 按内部 skill 的要求继续读取 references、调用 scripts 或执行命令。

完整路由规则可以查看 [router skill](https://github.com/tenfyzhong/agent-plugins-hub/blob/main/plugins/lark-cli-skills/skills/lark/SKILL.md)。

## 第三步：动态生成内部 skill 目录

discovery script 不读取所有 `SKILL.md` 正文，只解析 YAML frontmatter 中的 `name` 和 `description`，再补上绝对路径：

```python
DEFAULT_SKILLS_DIRECTORY = Path(__file__).resolve().parents[3] / "internal-skills"


def discover_skills(skills_directory):
    catalog = []
    for skill_file in sorted(skills_directory.glob("*/SKILL.md")):
        fields = parse_frontmatter(skill_file)
        catalog.append(
            {
                "name": fields["name"],
                "description": fields["description"],
                "path": str(skill_file.resolve()),
            }
        )
    return catalog
```

输出是一个供 Codex 二次路由的 JSON 目录：

```json
[
  {
    "name": "lark-calendar",
    "description": "飞书日历：管理日历日程和会议室……",
    "path": "/path/to/plugin/internal-skills/lark-calendar/SKILL.md"
  },
  {
    "name": "lark-task",
    "description": "飞书任务：管理任务、清单和任务智能体……",
    "path": "/path/to/plugin/internal-skills/lark-task/SKILL.md"
  }
]
```

为什么要返回绝对路径？因为 Plugin 安装后的缓存目录不应该被硬编码。脚本从自身位置推导 Plugin 根目录，再返回实际安装位置，router 才能稳定地读取目标文件。

完整的 frontmatter 解析和错误处理见 [discover_internal_skills.py](https://github.com/tenfyzhong/agent-plugins-hub/blob/main/plugins/lark-cli-skills/skills/lark/scripts/discover_internal_skills.py)。

## 一次请求实际会怎样执行

假设用户输入：

```text
帮我查看今天的日程和未完成任务
```

实际加载链路是：

1. 初始上下文中的 `lark` description 命中“日程”和“任务”。
2. Codex 加载 `skills/lark/SKILL.md`。
3. router 运行 discovery script，得到 27 个内部 skills 的元数据目录。
4. 二次路由选择 `lark-calendar` 和 `lark-task`，或者选择已经封装好的组合工作流。
5. Codex 只读取被选中的内部 `SKILL.md`，再执行具体流程。

对于完全无关的编码、数据库或运维任务，`lark` router 不会被触发，27 个内部 skills 的描述也不会进入这次任务的上下文。

## 为什么要使用 Plugin，而不是只写一个大 skill

把所有内容塞进一个巨大的 `SKILL.md` 也能减少初始 description 数量，但会带来新的问题：

- 不同子领域的规则混在一起，修改和审查困难。
- 每次命中都要加载整份大文件，失去正文层面的渐进式披露。
- scripts、references 和测试难以按子领域维护。
- 团队安装、升级和分发不够清晰。

Plugin 更适合作为分发边界，router skill 负责一级发现，内部 skills 继续保留原来的模块边界。这样既没有丢掉 skill 的可维护性，也减少了 Codex 启动时的元数据压力。

## 实现时最容易踩的几个坑

### 1. router 的 description 太窄

内部 skill 再完整，如果一级 router 没被命中，也没有机会参与二次路由。router 的 description 应覆盖整个业务域的稳定关键词、产品名和常见意图，但不要把每个内部 skill 的详细边界重新复制一遍。

### 2. 扫描脚本直接输出完整正文

discovery 阶段只需要 `name`、`description` 和 `path`。如果脚本把所有 `SKILL.md` 全文输出到上下文，就只是把启动时的膨胀推迟到了第一次调用，没有真正做到按需加载。

### 3. 选中后没有完整读取内部 skill

内部 description 只负责路由，不能替代工作流说明。router 必须明确要求：选中 skill 后先完整读取 `SKILL.md`，再执行任何操作。

### 4. router 一次加载太多内部 skills

应选择能够覆盖请求的最小集合。跨服务请求可以加载多个 skills，但不能因为“可能有用”就把整个目录全部读进来。

### 5. 没有验证真正注册了几个 skills

我在参考项目里加了测试，确保：

- 标准 `skills/` 注册目录里只有 `lark` 一个 router
- `internal-skills/` 没有进入 Codex 的顶层 skill 列表
- 内部 skill 数量不少于预期
- discovery 输出的每一项都只有 `name`、`description` 和 `path`
- 所有返回路径都真实存在

这类测试很重要，因为一次目录调整或 manifest 修改，就可能让内部 skills 意外重新暴露给 Codex。

## 这套方案的边界

二级路由不是没有代价。第一次进入某个业务域时，会多一次脚本执行和 skill 选择；内部 skill 也不能再作为顶层已注册 skill 直接参与全局匹配。因此它更适合下面这类情况：

- 同一个产品或业务域下有大量 skills
- skills 共享明显的顶层关键词
- 每次请求通常只会使用其中一小部分
- 这些 skills 需要作为一个整体安装、升级和分发

如果只有少量彼此无关的 skills，优先禁用不使用的 skill 或 Plugin、缩短冗长 description，通常更直接。只有当一组 skills 天然形成一个领域时，才值得增加 router 这一层。

## 安装参考实现

如果想直接体验这套结构，可以把我的 Plugin marketplace 加到 Codex：

```bash
codex plugin marketplace add tenfyzhong/agent-plugins-hub --ref main
codex plugin add lark-cli-skills@tenfyzhong-agent-plugins-hub
```

安装后新开一个会话，再输入 Lark 或飞书相关请求即可。

## 总结

这个 2% 告警的核心不是 skill 正文太多，而是可发现的 skill 元数据太多。我的处理方式可以概括成三句话：

1. 用 Plugin 把同一领域的 skills 收到一个分发单元里。
2. manifest 只注册一个描述精简但覆盖完整的 router skill。
3. router 命中后只发现元数据，并完整加载真正需要的内部 skills。

这样做不会突破 Codex 的上下文预算，而是改变内容进入上下文的时机：全局启动时只保留一条领域入口，具体工作流等到真正需要时再加载。对于 skill 数量持续增长的工具集，这比不断压缩 description 更容易长期维护。
