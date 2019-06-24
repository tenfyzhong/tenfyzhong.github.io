---
title: 关于redis geohash的性能测试
categories:
  - 数据库
tags:
  - redis
  - 数据库
  - 后台
date: 2019-06-24 14:28:19
keywords: redis,数据库,后台
---

redis于3.2版本加入了geohash的数据库结构。使坐标的计算变得非常方便。
下面对redis的geohash做性能测试，看可以支持怎样的并发。
<!-- more -->
# 环境
redis版本:使用了docker的redis:5-alpine的版本。  
服务器配置如下图：
![lscpu-free](https://tenfy.cn/picture/241-lscpu-free.png)

压测客户端使用go语言编码。所有代码在：[redis-geo-test](https://github.com/tenfyzhong/redis-geo-test)

我们分别产生10000,100000,1000000个数据加入到redis，然后再随机生产一个坐标来去计算与redis里的坐标小于10千米的点。

因为redis是单线程程序，cpu最高跑到100%，在生产环境，CPU超过80%就高负载，要考虑扩容了。
所以我们以80%的负载做临界点来看qps。

# 结果
在原始数据为10000的情况下，20个并发，每个并发sleep 500微秒，cpu压力83%左右，内存使用5.5MB，qps 26000。
结果如下图：
![redis-geo-10000](https://tenfy.cn/picture/redis-geo-10000.png)

在原始数据为100000的情况下，20个并发，每个并发sleep 600微秒，cpu压力84%左右，内存使用14MB，qps 22000。
结果如下图：
![redis-geo-100000](https://tenfy.cn/picture/redis-geo-100000.png)

在原始数据为1000000的情况下，20个并发，每个并发sleep 1500微秒，cpu压力84%左右，内存使用102MB，qps 10000。
结果如下图：
![redis-geo-1000000](https://tenfy.cn/picture/redis-geo-1000000.png)


对比如下表：

| 原始数据大小 | mem   | 80%cpu qps |
|--------------|-------|------------|
| 10000        | 5.5MB | 26000      |
| 100000       | 14MB  | 22000      |
| 1000000      | 102MB | 10000      |
