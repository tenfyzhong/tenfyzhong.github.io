---
title: linux iostat查看磁盘io速率
categories:
  - linux
tags:
  - linux
  - 监控
date: 2019-07-10 08:45:40
keywords: linux,监控,iostat
toc: false
---

`iostat`是一个查看当前磁盘io速率的命令。

<!-- more -->
> 这是[《后台程序员应该懂的linux监控命令》](/subjects/linux-monitoring.html)的内存篇关于free的使用指南。  

`iostat`使用上比较简单，输出也是比较简洁的。不加任何参数即可查看从机器启动到当前的平均io情况。
iostat最后可以加两个可选的interval参数和count参数。指定interval参数则每interval秒去刷新反馈一次结果。
指定count则总共反馈count次结果。

默认情况下，`iostat`的第一个反馈结果是从系统启动到当前时间的平均速率。
之后的每一个反馈结果是从上一次到当时间的io情况计算来的。如果加`-y`参数强制加interval参数，
则会忽略从系统启动到当前时间的那次结果。

下图为不加参数的结果  
![linux-iostat](https://tenfy.cn/picture/linux-iostat.png)

下图为加参数`-y 1 2`的结果。可以看到第一个结果跟上面不太一样，上图每个值比较大，
因为它包含了机器启动到当前时间的io情况。  
![linux-iostat-y-1-2](https://tenfy.cn/picture/linux-iostat-y-1-2.png)

对于`iostat`的结果也是比较简单，包含了三块信息。第一块在第1行，显示了当前系统的信息，
包含linux内核版本、时间、cpu架构、cpu个数。第二块信息是当前cpu的负载情况。
第三块信息是磁盘信息。

cpu信息字段解析：
- %user 用户态空间cpu使用率
- %nice nice优化级的用户态空间cpu使用率
- %system 内核态空间cpu使用率
- %iowait 等待io的cpu时间
- %steal 其他虚拟机的cpu使用率
- %idle 空余cpu

磁盘信息字段解析：
- tps 磁盘io每秒次数
- kB_read/s 每秒读磁盘的速度
- kb_wrtn/s 每秒写磁盘的速度
- kb_read 读磁盘的数据量
- kb_wrtn 写磁盘的数据量


对于io密集型的服务器，我们需要留意一下磁盘io的速率，因为磁盘io会产生中断来切换cpu，
会降低业务的计算性能。
