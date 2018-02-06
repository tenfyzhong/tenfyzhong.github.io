---
title: mongo跨集群复制集同步
categories:
  - 后台
tags:
  - mongo
date: 2018-02-06 16:39:10
keywords: mongo,mongo-connector
---

mongo的跨集群复制集同步方案。

<!-- more -->

在生产环境上使用mongo，需要考虑容灾。在跨idc的容灾方案上，我们需要把数据库同步到其他的idc去，
这样即使一个idc挂了，另一个idc还可以服务，而且数据不会丢。

对于mongo的复制集，我们可以有两种方案，一是idc间建成一个复制集。二是使用工具去同步oplog进行写重放。

# idc间建复制集
这种方案是时简单的，只要把各个idc都加入到一个复制集就行了。

但是，会引起非常多的问题。

mongo的复制集只能往master写，所以我们不好控制。当master挂掉之后，
重新选master的过程我们控制不了，这样就不知道选了哪个idc的机器来当主了。

二是带宽问题。如果带宽不够用，mongo内部的心跳过程丢掉了，有可能导致不能及时发现而当成结点挂了。

# idc间同步
这种方法需要额外的工具，每个idc都建自己的复制集。以一个idc为主写，所有的写请求都写到主写的复制集上，
然后开工具把写入的oplog同步操作到其他的idc上。

我们使用[mongo-connector](https://github.com/mongodb-labs/mongo-connector)

这样做的方案，可能有效的解决主写master挂掉的切换问题。可以确定主写集群的master挂掉后，
会在同一个idc上重新选master。

同时，不存在机房间mongo集群的心跳，这样不会因为丢包而导致节点被挂掉。

但是，对于带宽不够问题，会产生同步非常慢的问题。这样会导致写进去了，但是去不能及时读到。

## idc间步方案
下面我们以两个mongo单独的复制集来看一下操作步骤。为了方便演示，以下均使用docker进行操作。

### 建立2个单独的mongo复制集
以下是docker-compose.yml配置
```docker-compose
mongo1:
  image: mongo:3.5.13
  container_name: mongo1
  ports:
    - "17017:27017"
  command:
    - '--replSet'
    - 'singleNodeRepl'
    - '--bind_ip'
    - '0.0.0.0'

mongo2:
  image: mongo:3.5.13
  container_name: mongo2
  ports:
    - "37017:27017"
  command:
    - '--replSet'
    - 'singleNodeRepl'
    - '--bind_ip'
    - '0.0.0.0'
```

我们建立一个目录mongo，在其下新建docker-compose.yml文件，粘入以上的内容。
然后通过在mongo目录下docker-compose拉起来：
```sh
docker-compse up -d
```

### 初始化复制集
连接到mongo上，初始化复制集
```sh
mongo localhost:17017
```

```mongo
rs.initiate()
```

因为我们在docker里面跑，mongo的配置会以docker里面的host命名，在外面会找不到。
我们需要把mongo的配置改成host的ip，注意，这里不能使用localhost，
因为在docker里面的localhost在外面是访问不到的。

还是在mongo里面操作，假如主机ip是10.11.12.13
```mongo
cfg = rs.conf()
cfg.members[0].host = "10.11.12.13:17017"
rs.reconfig(cfg)
```

这样即初始化了第一个集群。同样操作第二个注意，注意把端口改成37017，我们在docker-compose里配了这个端口。

### 配置mongo-connector
mongo-connector的[wiki](https://github.com/mongodb-labs/mongo-connector/wiki)  
配置[模板](https://github.com/mongodb-labs/mongo-connector/blob/master/config.json)  
```json
{
    "mainAddress": "10.11.12.13:17017",
    "oplogFile": "/var/log/mongo-connector/oplog.timestamp",
    "noDump": false,
    "batchSize": -1,
    "verbosity": 3,
    "continueOnError": true,

    "logging": {
        "type": "file",
        "filename": "/var/log/mongo-connector/mongo-connector.log",
        "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
    },

    "docManagers": [
        {
            "docManager": "mongo_doc_manager",
            "targetURL": "10.11.12.13:37017",
        }
    ]
}
```
跟mongo目录同级建一个connector的目录，新建config.json加入以上的配置内容。

```docker-compose
connector:
  image: tenfyzhong/mongo-connector:1.0.0
  container_name: connector
  net: host
  volumes:
    - $PWD/config.json:/etc/config.json
    - $PWD/mongo-connector:/var/log/mongo-connector
  command:
    - "-c"
    - "/etc/config.json"
```
在connector目录下新建docker-compose.yml文件加入以上的内容。
在connector目录下使用docker-compose拉起服务。

```sh
docker-compose up -d
```

接下来连接到mongo1上去新建数据，就会同步到mongo2上了。
