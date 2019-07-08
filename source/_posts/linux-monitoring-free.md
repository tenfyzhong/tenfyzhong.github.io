---
title: linux free查看内存状态
categories:
  - linux
tags:
  - linux
  - 监控
date: 2019-07-05 13:04:41
keywords: linux,free,监控
---

`free`是一个查看内存状态的命令。

<!-- more -->
> 这是[《后台程序员应该懂的linux监控命令》](/subjects/linux-monitoring.html)的内存篇关于free的使用指南。  

# free命令
输出结果如下图：  
![linux-free-2line](https://tenfy.cn/picture/linux-free-2line.png)

不加参数支持，会直接KB做单位显示。支持`-b`, `-k`, `-m`, `-g`这样的参数，指定显示的单位。
一般情况下，使用`-h`可以输出更方便阅读的单位。

这个命令输出都是我们需要关注的内容，然而内容并不多。命令输出了两行，
第一行表示的是内存的使用情况，第二表示的是swap的使用情况。

- total表示总内存大小。  
- used表示已经使用的内存大小。  
- free表示的空闲内存大小。  
- shared表示共享内存大小。  
- buff/cache表示的是内核用到的buffer和page cache。下面有专门的讲解。  
- avaliable表示可用内存大小。  

只要可用内存够用，都不会有什么性能问题了。

对于swap，我们需要used是否会增长，如果有增长，说明内存用光了，需要使用到swap分区，
swap其实是磁盘设备，所以如果有增长的话，服务器性能肯定是会大大下降的。

# buffer/cache
cache是缓存从磁盘块设备中读的文件。可以更快的提供给后续需要使用的程序。

buffer保存即将要写的文件。写文件操作时，会先数据写到buffer里，然后写操作就完成了。
操作系统会慢慢地去把buffer的数据写到磁盘。如果没有buffer机制，那么需要实时写到磁盘，
但是磁盘的速度非常慢，就会导致写操作非常慢。

我们也可以直接去清掉这些占用。
```
# To free pagecache:
sync; echo 1 > /proc/sys/vm/drop_caches
# To free dentries and inodes:
sync; echo 2 > /proc/sys/vm/drop_caches
# To free pagecache, dentries and inodes:
sync; echo 3 > /proc/sys/vm/drop_caches
```

但是在生产服务器，不建议手动删除。对于读入的缓存文件，如果清掉了，下次需要使用时，
还需要再从磁盘读入，速度会非常慢，影响服务性能。而且在内存不够的时候，
操作系统会主动去做清除的工作。

# 另外的输出格式
![linux-free](https://tenfy.cn/picture/linux-free.png)  
有些机器会输出这样的结果，包含了三行。结果显示上只是有了一些小区别。  
第一行的used包含了buffer/cache的占用。  
第一行的free减去了buffer/cache的占用。  
第二行的used显示的是不包含buffer/cache的占用，这是真正占用的内存。  
第二行的free加上了buffer/cache的占用，这才是真正free可用的内存。  
