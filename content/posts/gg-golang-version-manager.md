---
title: golang多版本管理
date: 2023-12-28T13:19:05+08:00
categories:
  - 后台
tags:
  - 后台
  - golang
keywords: golang,后台
---

在我们的开发环境中，使多个golang版本并存。  
<!-- more -->

大部分情况下，一个比较新的golang版本就能满足我们的日常的开发需求。  
但是项目中，因为协作的原因，或者由于项目启动比较早，可能我们不同的工程需要用不同的golang版本。甚至有些工作用比较新的版本编译不了。  
这时候，我们就需要让本地的开发环境支持多个golang版本。

# 官方解决方案
当前，golang提供了一个官方的解决方案，我们只要`go install`对应的go版本，然后就能使用特定的版本进行工作了。  
官方repo：[golang.org/dl](https://github.com/golang/dl)

使用方式也比较简单，比如我们要安装一个1.18的版本，只需要两步
1. `go install golang.org/dl/go1.18@latest`
2. `go1.18 download`

之后只需要用`go1.18`替换`go`命令，即可使用特定的这个版本进行go相关的工作了。

但是`go1.18`比`go`多了好几个字符，而且由于肌肉记忆，可能我们敲了go之后就会敲后面的内容了。为了让`go`直接当成特定的版本使用，我们可以设置环境变量，
设置好`GOROOT`和把特定版本的go放到`PATH`前面即可。  
如下，我们把下面的内容设置到我们的shell加载配置里。
```bash
export GOROOT=$(go1.18 env GOROOT)
export PATH=$GOROOT/bin:$PATH
```

如果是bash，放在`~/.bashrc`里，如果是zsh，则放在`~/.zshrc`里，如果是fish则放在`~/.config/fish/config.fish`里

到此，我们就可以使用特定版本的golang了，一个开发环境也安装了多个版本的golang。

# 不同工程自动加载特定的版本
以上在shell配置中配置特定版本，在不同的工程中就行不通了。因为配置文件是全局的。如果用特定的版本号来运行，我们除了要敲多版本号外，还需要记得每个工作用的是哪一个版本的go。

有没有办法在我们cd到特定的目录时，自动配置环境变量，离开的时候，自动释放这些环境变量呢？

[direnv](https://direnv.net/)可以帮我们完成这一项工作。它可以在特定目录上，把环境变量写到`.envrc`，那cd进去就会自动加载，离开就会自动释放。

使用自己操作系统的包管理安装好direnv后，接下来cd到我们特定的工程，假如这个工程使用1.18的版本，我们只要把下面这一段配置放到`.envrc`即可。
```bash
export GOROOT=$(go1.18 env GOROOT)
export PATH=$GOROOT/bin:$PATH
```
配置好后，direnv会提示需要对这个目录进行授权，执行以下命令即可
```bash
direnv allow
```

这样我们就可以安装好多个golang版本，然后在不同的工程中配置好`.envrc`，就能在特定的工程用特定的版本go了。

direnv使用的是bash的方案配置环境变量，所以在fish这种非标准POSIX shell，也需要使用以上的语法进行配置。

# [gg](https://github.com/tenfyzhong/gg)管理golang版本
基于官方的解决方案，我们解决了多个版本的并存问题和运行问题。但是，我们本地安装了哪些版本，官方发布了哪些版本可以给我们用？

[gg](https://github.com/tenfyzhong/gg)这个工具为我们提供了非常方便的管理方式。它支持以下能力
- 查看本地版本列表
- 官方的所有版本列表
- 安装官方版本到本地
- 删除版本
- 打印特定版本的环境变量

它直接基于官方的解决方案做了包装，把安装的两步合成了一个步，打印环境变量配置。

目前`gg`只支持fish shell

## `gg ls` 查看本地版本
`golang.org/dl`的安装，会把go的数据下载到`~/sdk`目录下。`gg ls`命令会去查看这个目录存在哪些版本，进行打印。

## `gg ls-remote` 查看官方版本
`gg ls-remote`会去爬出官方的版本进行展示，同时会把结果缓存起来。缓存有效期24小时。使用缓存后，可以避免每次去爬取，加快运行速度。

## `gg install` 安装特定的版本
比如上面我们介绍的安装1.18版本，我们只需要运行下面的命令
```bash
gg install 1.18
```
它会使用全局的go版本，去完成安装的两步
1. `go install golang.org/dl/go1.18@latest`
2. `go1.18 download`

## `gg remove`删除特定版本
删除特定的版本，只需要把`$GOPATH/bin`下特定的版本删除，把`~/sdk`下特定版本删除即可。所以`gg remove`的工作比较简单。
```bash
gg remove 1.18
```

## `gg use`使用特定的版本
这个命令会把特定版本需要的环境变量打印出来，可以直接进行`source`或者重定向到`.envrc`上。
比如对于bash的环境变量  
```bash
gg use --bash 1.18
```
它会输出以下的内容
```
# source this code to enable it
# for example:
# > gg use --bash 1.18 | source

# if you use direnv to manage environment, you can redirect the output to .envrc in the current directory
# > gg use --bash 1.18 >> .envrc; direnv allow

export GOROOT=$(go1.18 env GOROOT)
export PATH=$GOROOT/bin:$PATH
```

或者fish的环境变量
```bash
gg use --fish 1.18
```
它会输出以下的内容
```
# source this code to enable it
# for example:
# > gg use --fish 1.18 | source

set -gx GOROOT (go1.18 env GOROOT)
fish_add_path $GOROOT/bin
```

如果不指定特定的shell，它会指定为当前的登录shell。  
如果要使用direnv，则需要指定为bash

# 总结
基于以上，只需要使用[gg](https://github.com/tenfyzhong/gg)即可完成官方方案的多版本解决版本。再加上[direnv](https://direnv.net/)即可让我们在特定的工程自动使用特定的版本。
