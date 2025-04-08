---
title: 生产工具接入ai
date: 2025-04-08T20:59:00+08:00
categories:
  - ai
tags:
  - ai
---

# 概要
首先先介绍一下我的工作流：
1. 使用笔记软件 obsidian 记录工作事项、知识库
2. 开发使用 nvim
3. 在终端上工作，主要用 fishshell
4. 启动工具使用 raycast

想要在工作中用到的工具都接入 ai。
1. obsidian 上使用，可以用来对笔记进行总结、誊写
2. nvim 上使用 ai，可以直接进行自然语言式开发
3. fishshell 上使用 ai，对于复杂的指令，可以直接使用自然语言进行描述，让 ai 来生成命令
4. raycast 上使用，有问题可以直接问，而不用打开浏览器，再打开聊天页面

现在国内有很多模型可以用，而最火的就数 deepseek 了。而且 deepseek 的 api 价格也会比较低。所以以上都使用 deepseek 的模型。

# 配置 deepseek api
我使用了火山方舟上的 deepseek，它相比官方的 deepseek 会更稳定一些，而且更便宜一些。新注册送 50 万 token。现在协作奖励计划，到 2025 年 5 月 31 日，每天都有 50 万的免费 token。

火山方舟官方：[火山引擎-云上增长新动力](https://www.volcengine.com/)

## 创建 API Key
在火山方向的 API Key 管理上创建自己的 API Key
![创建API Key](https://tenfy.cn/picture/20250408202956.png)

## 创建 deepseek 接入
在在线推理菜单里，创建模型接入点
![创建推理接入点](https://tenfy.cn/picture/20250408203403.png)

填好名字
![创建推理接入点](https://tenfy.cn/picture/20250408203535.png)

选择模型，分别创建出 R1 和 V3 的模型
![选择模型](https://tenfy.cn/picture/202504082036834.png)

创建好之后，点击模型的名字，就可以查看模型，复制好 API Key
![查看模型](https://tenfy.cn/picture/20250408204100.png)

创建好 deepseek 的 api key 之后，就可以为不同的工具配置使用了

# 配置工具
## Obsidian
首先先安装好 Copilot 的插件
![新加模型](https://tenfy.cn/picture/20250408204551.png)

Base URL 填 `https://ark.cn-beijing.volces.com/api/v3`

新加好之后，就可以在 `Default Chat Model` 里选择新加的模型了。可以把 r1 和 v3 都配置上，按需要使用。配置好后，就可以使用打开 Copilot 进行聊天了。

## nvim
nvim 使用插件 `olimorris/codecompanion.nvim`
配置如下：
```lua
local function clean_streamed_data(data)
    if type(data) == "table" then
        return data.body
    end
    local find_json_start = string.find(data, "{") or 1
    return string.sub(data, find_json_start)
end

local function handle_chat_output(self, data)
    local output = {}
    if data and data ~= "" then
        local data_mod = clean_streamed_data(data)
        local ok, json = pcall(vim.json.decode, data_mod, { luanil = { object = true } })
        if ok and json.choices and #json.choices > 0 then
            local choice = json.choices[1]
            local delta = (self.opts and self.opts.stream) and choice.delta or choice.message
            if delta then
                output.role = delta.role or nil
                output.content = (delta.reasoning_content or "") .. (delta.content or "")
                return { status = "success", output = output }
            end
        end
    end
end

local function deepseek_adapter(name, formatted_name, model_name)
    return require("codecompanion.adapters").extend("openai_compatible", {
        env = {
            url = os.getenv("DEEPSEEK_API_URL"),
            api_key = os.getenv("DEEPSEEK_API_KEY"),
            chat_url = os.getenv("DEEPSEEK_CHAT_URL"),
        },
        name = name,
        formatted_name = formatted_name,
        handlers = {
            chat_output = handle_chat_output,
        },
        schema = {
            model = {
                default = model_name,
            },
            temperature = {
                order = 2,
                mapping = "parameters",
                type = "number",
                optional = true,
                default = 0.0,
                desc =
                "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.",
                validate = function(n)
                    return n >= 0 and n <= 2, "Must be between 0 and 2"
                end,
            },
        },
    })
end

local function deepseek_adapter_v3()
    return deepseek_adapter("deepseek_v3", "Deepseek-V3", os.getenv("DEEPSEEK_MODEL_V3_ID"))
end

local function deepseek_adapter_r1()
    return deepseek_adapter("deepseek_r1", "Deepseek-R1", os.getenv("DEEPSEEK_MODEL_R1_ID"))
end

local codecompanion = {
    "olimorris/codecompanion.nvim",
    config = function()
        require('codecompanion').setup({
            display = {
                chat = {
                    icons = {
                        pinned_buffer = " ",
                        watched_buffer = "👀 ",
                    },
                },
                token_count = function(tokens, adapter)
                    return " (" .. tokens .. " tokens)"
                end,
            },
            adapters = {
                opts = {
                    show_defaults = false,
                },
                deepseek_r1 = deepseek_adapter_r1,
                deepseek_v3 = deepseek_adapter_v3,
            },
            strategies = {
                chat = {
                    adapter = "deepseek_r1",
                },
                inline = {
                    adapter = "deepseek_r1",
                },
            },
            opts = {
                language = "Chinese",
            },
        })
    end,
    dependencies = {
        "nvim-lua/plenary.nvim",
        "nvim-treesitter/nvim-treesitter",
    },
}

return { codecompanion }
```

里面配置了几个环境变量：

| 环境变量                 | 值                                          |
| -------------------- | ------------------------------------------ |
| DEEPSEEK_API_URL     | `https://ark.cn-beijing.volces.com/api/v3` |
| DEEPSEEK_API_KEY     | 火山上的 API Key                               |
| DEEPSEEK_CHAT_URL    | `/chat/completions`                        |
| DEEPSEEK_MODEL_R1_ID | 火山的 R1 模型的 id                              |
| DEEPSEEK_MODEL_V3_ID | 火山的 R3 模型的 id                              |

## fish shell
fish shell 使用插件 `realiserad/fish-ai`。

fish shell 建议使用 v3 模型，r1模型非常慢，然后看不到推理输出

配置文件：~/.config/fish-ai.ini

```ini
[fish-ai]
history_size = 5
preview_pipe = True
configuration = deepseek-v3

[deepseek-v3]
provider = self-hosted
api_key = xxxx
server = https://ark.cn-beijing.volces.com/api/v3
model = model_id

[deepseek-r1]
provider = self-hosted
api_key = xxxx
server = https://ark.cn-beijing.volces.com/api/v3
model = model_id
```

## raycast
raycast 安装插件: Deepseek Quick Actions

Custom API Endpoint: https://ark.cn-beijing.volces.com/api/v3

Custom Model Name 使用火山的模型 id

LLM Model 使用 deepseek-chat

raycast 我也使用了 v3 模型，会比较快一些
