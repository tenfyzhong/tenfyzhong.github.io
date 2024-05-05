---
title: 创建homebrew/tap安装规则
date: 2024-05-05T12:13:52+08:00
categories:
  - 工具
tags:
  - 工具
keywords: 工具,homebrew
---

<!-- more -->

# 创建自己的homebrew/tap
在github上创建一个名为`homebrew-tap`的仓库，创建一个`Formula`的目录。

然后就有一个自己的名为`username/tap`的homebrew仓库了。username改为自己的Github名字。

使用brew命令，把自己的仓库加到tap上
```sh
brew tap username/tap
```

# 创建程序版本
由于homebrew需要使用指定版本来创建仓库。对于我们的程序需要建立一个tag，推到Github上。之后，我们可以基于该tag，来创建homebrew的formula。以[dashdog](https://github.com/tenfyzhong/dashdog)，创建好0.1.0版本后，在Github上复制tag的链接。执行以下命令创建一个formula
```bash
brew create https://github.com/tenfyzhong/dashdog/archive/refs/tags/0.1.0.tar.gz --tap tenfyzhong/homebrew-tap
```

formula文件会在`/usr/local/Homebrew/Library/Taps/tenfyzhong/homebrew-tap/Formula`生成一个`dashdog.rb`的配置文件，并且打开。

修改配置：
```ruby
class Dashdog < Formula
  desc "dashdog is a tool to generate docset for [dash](https://kapeli.com/dash)"
  homepage "https://github.com/tenfyzhong/dashdog"
  url "https://github.com/tenfyzhong/dashdog/archive/refs/tags/0.1.3.tar.gz"
  sha256 "3f5531d35e71d1d941e1ccfcaabc597441eb0b1a94bbfe5e5bf992f68a32efc3"
  license "MIT"

  depends_on "go" => :build

  def install
    system "go", "build", "-ldflags", "-X 'github.com/tenfyzhong/dashdog/cmd/dashdog/version.Version=#{version}'", "-o", bin/"dashdog", "./cmd/dashdog"
    bash_completion.install "cmd/dashdog/completions/dashdog.bash" => "dashdog"
    zsh_completion.install "cmd/dashdog/completions/_dashdog" => "dashdog"
    fish_completion.install "cmd/dashdog/completions/dashdog.fish" => "dashdog.fish"

    bin.install "cmd/dashdog-go/dashdog-go"
    bash_completion.install "cmd/dashdog-go/completions/dashdog-go.bash" => "dashdog-go"
    zsh_completion.install "cmd/dashdog-go/completions/_dashdog-go" => "dashdog-go"
    fish_completion.install "cmd/dashdog-go/completions/dashdog-go.fish" => "dashdog-go.fish"

    pkgshare.install "conf"
  end

  test do
    output = shell_outpu("#{bin}/dashdog -h")
    assert_equal "NAME:
   dashdog - a tool to generate docset from html for dash

USAGE:
   dashdog -c|--config <file> [--log off] [config options]

VERSION:
   dev

AUTHOR:
   tenfyzhong

GLOBAL OPTIONS:
   --config file, -c file  the config file to load
   --help, -h              show help (default: false)
   --log level             log level, the log will print to stdout, available value:[debug,info,warn,error,off] (default: \"off\")
   --version, -v           print the version (default: false)

   config

   --bundle-pattern pattern          a pattern to match the path of the sub module name, the group captured can be use in the --bundle-replace flag, it will overwrite the value of `sub_path_bundle_name->pattern` item in the config
   --bundle-replace replace-pattern  a replace-pattern to replace the path which matched by --bundle-pattern flag, it will overwrite the value of `sub_pattern_bundle_name->replace` item in the config
   --cfbundle bundle                 the bundle of the root page, it will overwrite the value of `plist->cfbndle_name` item in the config
   --depth depth                     the max depth of sub page to generate, at least 1, it will overwrite the value of `depth` item in the config (default: 1)
   --name name                       the name of the docset, it will overwrite the value of `name` item in the config file
   --path path                       the path to generate docset, it will overwrite the value of `path` item in the config file (default: \"$HOME/Documents/dashdog-doc/\")
   --path-regex pattern              the sub path which match the pattern will be able to generate, it will overwrite the value of `sub_path_regex` item in the config
   --url url                         the source url of the docset, it will overwrite the value of `url` item in the config


COPYRIGHT:
   Copyright (c) 2024 tenfy
", output
  end
end
```

我们主要修改install部分和test部分，install部分指导brew怎么安装程序。test是安装后的测试，可忽略。
instal部分里的的安装对象可以参照[Formula-Cookbook#variable-for-directory-locations](https://docs.brew.sh/Formula-Cookbook#variables-for-directory-locations)

修改完后，我们推上Github，就完成配置了。

接下来可以使用
```bash
brew install tenfyzhong/tap/dashdog
```
进行安装


# 程序自动更新
经过以上配置好homebrew formula之后，当我们的程序版本更新的时候，我们需要更新homebrew的规则，可以使用以下命令
```bash
brew bump-formula-pr
```

但是每次都需要自动去执行，还挺麻烦的。我们可以配置github action，在tag推到Github的时候，自动创建pr进行更新。

在我们的程序工程上，创建以下文件`.github/workflows/homebrew.yml`，文件名可以随便改。
```yaml
name: Bump Homebrew formula

on:
  push:
    tags:
      - '*'

jobs:
  homebrew:
    runs-on: ubuntu-latest

    steps:
      - name: Update Homebrew formula
        uses: dawidd6/action-homebrew-bump-formula@v3
        with:
          # GitHub token, required, not the default one
          token: ${{secrets.TOKEN}}
          # Optional, defaults to homebrew/core
          tap: tenfyzhong/tap
          # Formula name, required
          formula: dashdog
          # Optional, will be determined automatically
          tag: ${{github.ref}}
          # Optional, will be determined automatically
          revision: ${{github.sha}}
          # Optional, if don't want to check for already open PRs
          force: false # true
```

之后我们创建好tag推上去的时候，就会自动提交pr了。如果安装规则不修改，我们只需要直接去合mr即可。如果规则需要修改，则需要在homebrew-tap的pr上进行修改。
