---
title: linux df查看磁盘空间
categories:
  - linux
tags:
  - linux
  - 监控
date: 2019-07-05 14:22:20
toc: false
---

`df`命令用于查看机器的磁盘空间使用情况。  
<!-- more -->

`df`命令一般是在磁盘空间不够进行告警的时候才会用的命令，使用上并不多。磁盘空间满的情况下，
在输命令按`<TAB>`键进行实全时，就会报错。

`df`是一个非常简单的命令。直接运行即可看到每个挂载点的空间使用情况。默认使用KB做单位。
可以加`-B`加单位，或者使用`-h`来显示更方便阅读的单位。

输出结果如下图：  
![linux-df](https://tenfy.cn/picture/linux-df.png)

第一行是列头，以下每一行是每个文件系统的情况。在上图中，最后5行是挂载的samba共享目录。

有时机器报`/`根目录满的情况下，我们去查找哪个目录占用比较大的时候，
需要把那些单独的挂载点给排除掉，它不占用根目录的空间。

`df`还支持加文件系统或者挂载点的路径做为参数，则只显示对应的文件系统或者挂载点的情况。
如下图:  
![linux-df-mount-point](https://tenfy.cn/picture/linux-df-mount-point.png)

`df`还可以通过加`-i`参数查看文件系统的inode使用情况。如下图：
![linux-df-inode](https://tenfy.cn/picture/linux-df-inode.png)

