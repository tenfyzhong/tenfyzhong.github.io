---
title: introduce-docker
date: 2017-09-08 09:14:21
categories:
  - 后台
tags: 
  - docker
keywords: docker
---
这篇文章是只是简单的入门，所以这里会教你怎么可以简单的上手。比如以前完全没有用过
docker，现在要跑一个服务要用docker来跑。

<!-- more -->

# 什么是docker
以下是docker官网的介绍
>Docker is the leading Containers as a Service (Caas) platform

通俗地说，docker是一个工具，能将应用封装在独立的容器里运行。

# 为什么需要docker
docker帮你把所有的东西都打包在一起了，所以要进行扩容的话，直接就使用打包好的这个
image来拉起服务就行了，再也不会有那些把程序交给运维，运维在启动服务的时候，因为
各种依赖，各种配置不一致而导致服务不了的破事了。

docker很好的把各个服务给隔离了，不会因为其他服务而影响到服务的运行。比如其他开了
一个httpd要监听80端口，这时nginx也要监听80端口。这时在同一个机器上进程是起不来的。
通过docker端口映射，就可以解决了。

如果这些还不能说服你，可以看一下下面的这篇文章。
[开发者可以使用Docker做什么？](http://dockone.io/article/378)

# 怎么使用docker
docker的使用只有两步：  
1. 打包image
2. 使用image拉起一个container，然后这个container就可以进行服务了。

image就相当于程序，container相当于该程序对应的进程。

另外docker还提供了一个仓库用来存放image的，基本你要用到的image都已经在那里了。
所以很多时候，不用你自己去打包image，当然除了你自己的应用程序外。

下面以一个简单的例子看一下这两步工具。

## 使用image拉起一个container
首先看一下用image怎么拉起一个container来跑。
```sh
docker run --rm alpine /bin/echo 'hello world'
```
在命令行执行上面的语句，就可以看到输出了一个`hello world`。这个例子非常简单。
`docker run` 就是用来跑起一个container的。它使用alpine镜像跑了一个container，
然后执行`/bin/echo`的程序进行输出。alpine是一个非常小型的linux发行版，所以它可以
执行echo命令。`--rm`参数让进程执行完了，把container给删除掉。

从这个例子可以看出，跑起一个container需要两样东西，一是image，它包含了要跑的程序。
一是container要跑的程序，这是container的入口。

对于已有的image，我们可以很简单就用起来了。但是，对于我们自己的服务程序，就需要
自己来打包image了。下面看一下例子。

## 打包image
你需要告诉docker，你要打包一个怎样的东西到这个image里，docker的机制是通过一个名
字为Dockerfile的文件来描述的，当然也可以用其他名字，但是文件内容必须符合
dockerfile语法，然后在构建的时候指定docker用这个文件。

step 0，我们创建一个目录用来放我们的程序和Dockerfile文件。
```sh
mkdir helloworld
```

step 1，在helloworld目录里面建一个helloworld.go的文件，我用go来做例子。
```go
package main

import (
	"net/http"
)

type helloHandler struct{}

func (h *helloHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, world!\n"))
}

func main() {
	http.Handle("/", &helloHandler{})
	http.ListenAndServe(":12345", nil)
}
```

step 2，在当前目录编译go生成可执行文件helloworld
```sh
go build
```
如果你不是在linux系统上，需要使用交叉编译成linux的可执行文件，因为接下来我们要说
的是在linux上跑的container。
```sh
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build
```

step 3，编写Dockerfile文件
```dockerfile
FROM alpine:3.6
MAINTAINER tenfyzhong "tenfyzhong@qq.com"
COPY helloworld /opt/helloworld/bin/helloworld
EXPOSE 12345
CMD /opt/helloworld/bin/helloworld
```
dockerfile也是非常简单。  
`FROM`使用一个基础镜像，alpine:3.6，这个基础镜像就是一个linux系统，然后在这个系
统上再加上其他东西。后面的`:3.6`指定了使用3.6版本的镜像。  
`MAINTAINER`只是简单的加上维护者信息。  
`COPY`把当前上下文（下面会讲到）的helloworld复制到指定的目录里去。  
`EXPOSE`告诉用户这个image要使用12345端口。  
`CMD`就是指定了这个镜像的入口启动程序了。这里指定的话，就不用像上面的例子那样在
启动时指定了。

step 4，构建image  
```sh
docker build --tag helloworld:1.0.0 .
```
执行这一条指令就可以构建一个名为helloworld，版本为1.0.0的镜像了。最后的`.`就是上
面说的上下文了。构建的时候，docker会把当前这个上下文的文件传给docker server，然
后dockerfile里面用到的文件就会根据当前这个目录结构去找到它们了。

step 5，拉起helloworld
还是像上面拉起echo的例子一样：
```sh
docker run --rm -d -p 12345:12345 --name=helloworld helloworld:1.0.0
```
这里跟上面的例子有些不同。
加了`-d`参数，`-d`指定了这个container在后台执行，我们可以通过下面的命令来看当前
在执行的container。
```sh
docker ps
```

加了`-p 12345:12345`，上面的例子中，我们使用12345端口来监听http请求。这里我们用
宿主机的12345映射到container的12345上去，也就是说请求宿主机的12345端口，就会把
请求转发到container上去了。

同时也没有了后面的启动参数，因为我们已经在Dockerfile文件里写好了。

然后我们用curl来请求一下本机的12345端口。
```sh
curl localhost:12345
```
可以看到它输出了`Hello, world!`


# 基本指令
通过上面的介绍，启动一个container已经没有问题了。但是在使用还需要懂些基础的使用。

### `docker images`
查看当前宿主机上已经有的image。

### `docker ps`
查看当前运行中的container，加上`-a`参数，还可以看到已经停止了的container。

### `docker stop`
`Usage:  docker stop [OPTIONS] CONTAINER [CONTAINER...]`  
停止一个container，可以传入docker的名字或者`docker ps`看到的第一个字段id。

### `docker start`
`Usage:  docker start [OPTIONS] CONTAINER [CONTAINER...]`  
启动通过stop命令停止的container。

### `docker rm`
删除一个container

### `docker rmi`
删除一个image。特别要注意不要跟rm指令搞混，rm删除的是一个container。

### `docker pull`
从仓库拉取一个镜像。
eg: 
```sh
docker pull alpine:3.6
```
### `docker run`
这个在上面已经介绍过。

### `docker build`
这个在上面已经介绍过。

