---
title: golang交叉编译
categories:
  - 后台
tags:
  - golang
date: 2017-10-17 09:00:35
keywords: golang,cross,compile
---

golang的交叉编译。

<!-- more -->

golang的交叉编译非常简单，只要配好对应的环境变量后再`go build`就可以了。
需要配置以下的环境变量。

# `CGO_ENABLED`
默认情况下这个变量为1。  
交叉编译不支持cgo，所以需要关闭cgo。  
linux/unix下为`CGO_ENABLED=0`。  
windows下为`set CGO_ENABLED=0`。  

# `GOOS`
需要编译的目标运行系统。默认情况下，这个变量设置对应的操作系统。mac为`darwin`，
linux为`linux`，windows为`windows`。  

所有的值如下：
```go
const goosList = "android darwin dragonfly freebsd linux nacl netbsd openbsd plan9 solaris windows zos "
```
定义在https://github.com/golang/go/blob/master/src/go/build/syslist.go#L7

我们只要把这个变量设置到对应的操作系统即可。  
linux/unix下为
```bash
GOOS=darwin
GOOS=linux
GOOS=windows
```

windows下为
```bat
set GOOS=darwin
set GOOS=linux
```

# `GOARCH`
需要编译的目标cpu架构。支持amd64和386等。  

所有的值如下：
```go
const goarchList = "386 amd64 amd64p32 arm armbe arm64 arm64be ppc64 ppc64le mips mipsle mips64 mips64le mips64p32 mips64p32le ppc s390 s390x sparc sparc64 "
```
定义在https://github.com/golang/go/blob/master/src/go/build/syslist.go#L8

linux/unix下为
```bash
GOARCH=amd64
GOARCH=386
```

windows下为
```bat
set GOARCH=amd64
set GOARCH=386
```

# 例子
## Mac下交叉编译linux
```bash
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build
```

## Mac/linux下交叉编译windows
```bash
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build
```

## linux下编译编译Mac
```bash
CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build
```

## windows下编译linux
```bat
SET CGO_ENABLED=0
SET GOOS=linux
SET GOARCH=amd64
go build
```

## windows下编译mac
```bat
SET CGO_ENABLED=0
SET GOOS=darwin
SET GOARCH=amd64
go build
```

