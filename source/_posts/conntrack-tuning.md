---
title: nf_conntrack调优
categories:
  - 后台
tags:
  - conntrack,调优
date: 2018-12-03 20:00:55
keywords:
---

深入了解conntrack调优。
<!-- more -->
# netfilter
netfilter是linux内在的一个软件框架，用来管理网络数据包。

netfilter提供了5个hook来进行管理网络包。如下图：
![netfilter-hooks](https://tenfy.cn/picture/netfilter-hooks.png)

- PREROUTING, 所有包都会经过这个hook
- LOCAL INPUT, 进入本机的包会经过这个hook
- FORWARD, 不进入本机的包，做转发的包会经过这个hook
- LOCAL OUTPUT, 从本机出去的包会经过这个hook
- POSTROUTING, 所有出去的包都会经过这个hook

netfilter进行包的管理，则需要记录每个连接的状态信息。这就是nf_conntrack的工作了。

# nf_conntrack
nf_conntrack是netfilter的一个子系统。它记录了每个连接的状态信息。

nf_conntrack记录的信息包括，源ip、端口，目标ip、端口，连接状态，协议等。

连接状态包含以下几种：
- NEW, 新创建的连接，发起连接方发出包后，还没收到回包，都处理这种状态。
- ESTABLISHED, 已建立的连接，发起连接后，收到回包，这时处理已连接状态。
- RELATED, 与其他连接相关联，其他的连接与此连接有关联。如ftp的控制连接和数据连接。
- INVALID, 非法的连接，比如包的行为不合法。

nf_conntrack需要保存这些信息在它自己的数据结构中。其数据结构如下：
![connection-tracking-structure](https://tenfy.cn/picture/connection-tracking-structure.png)

它是一个开链的哈希表，链表是一个双向表。每个哈希节点称为一个bucket，计算出同样哈希值的连接放到链表里连起来。
每个节点记录了请求方向、响应方向的消息。

哈希表的大小，也就是说哈希表的节点数，由`nf_conntrack_buckets`配置。引用2文档描述如下：
>nf_conntrack_buckets - INTEGER
>	Size of hash table. If not specified as parameter during module
>	loading, the default size is calculated by dividing total memory
>	by 16384 to determine the number of buckets but the hash table will
>	never have fewer than 32 and limited to 16384 buckets. For systems
>	with more than 4GB of memory it will be 65536 buckets.
>	This sysctl is only writeable in the initial net namespace.

如果这个值没有配置，则默认为内存容量除以16384。对于内存大于4GB的机器，默认为65536。
但是，我看了我一台94G内存和一个8G内存的机器，它的默认值都是16384。

nf_conntrack能跟踪的最大连接数由`nf_conntrack_max`配置。引用2文档描述如下：
>nf_conntrack_max - INTEGER
>   Size of connection tracking table.  Default value is
>   nf_conntrack_buckets value * 4.

它的值默认为`nf_conntrack_buckets * 4`。由于我这边机器`nf_conntrack_buckets`都是16384，
所以`nf_conntrack_max`默认值都是65536了。

# 查看nf_conntrack配置
查看当前系统配置的bucket数
```bash
sysctl -a | grep net.netfilter.nf_conntrack_buckets
```

查看当前系统配置的最大连接跟踪数
```bash
sysctl -a | grep net.netfilter.nf_conntrack_max
```

# nf_conntrack设置
每个bucket的平均链表长度为`bucket_len = nf_conntrack_max / nf_conntrack_buckets`。系统默认是4。
每个数据包的链表查询时间复杂度为bucket_len。当bucket_len太大时，则每个数据包要花太时间在链接的查找上。
所以，我们不能把bucket_len配得太长。按照linux的默认配置，就设置成4即可。

## 临时设置
```bash
# 设置bucket数
sysctl -w net.netfilter.nf_conntrack_buckets = 163840

# 设置最大连接跟踪数
sysctl -w net.netfilter.nf_conntrack_max = 655360
```

## 设置后使系统重启还能生效
```bash
# 设置bucket数
echo 'net.netfilter.nf_conntrack_buckets = 163840' > /etc/sysctl.conf

# 设置最大连接跟踪数
echo 'net.netfilter.nf_conntrack_max = 655360' > /etc/sysctl.conf

# 使用配置立马生产
sysctl -p
```

## nf_conntrack内存占用计算
```
total_mem_used(bytes) = conntrack_max * sizeof(struct ip_conntrack) + conntrack_buckets * sizeof(struct list_head)
```

在ubuntu上, ip_conntrack结构的大小为328字节，list_head的大小为8字节。计算代码如下(引用6)：
```py
import ctypes
LIBNETFILTER_CONNTRACK = 'libnetfilter_conntrack.so.3.5.0'
nfct = ctypes.CDLL(LIBNETFILTER_CONNTRACK)
print 'sizeof(struct nf_conntrack):', nfct.nfct_maxsize()
print 'sizeof(struct list_head):', ctypes.sizeof(ctypes.c_void_p) * 2
```

对于上面的配置，nf_conntrack_max设为655360，nf_conntrack_buckets设为163840，则内存使用量为：
```
total_mem_used(MB) = (655360*328+163840*8)/1024^2 = 206.25
```
占用206.25MB。


# nf_conntrack表满的表现
当nf_conntrack满的时候，新连接过来的时候，就会直接被netfilter直接丢掉，以致连接不上。
在监控上看，可以看到脉冲式的请求。另外我们可以用`dmesg`命令看到系统的日志显示nf_conntrack表满的提示。

监控图一般会有以下的表现
![qps](https://tenfy.cn/picture/conntrack_full_qps.png)

`dmesg`可以看到以下的输出
![dmesg](https://tenfy.cn/picture/dmesg_nf_conntrack_table_full.png)



# 引用
1. [netfilter-hacking-HOWTO](https://netfilter.org/documentation/HOWTO/netfilter-hacking-HOWTO.txt)
2. [nf_conntrack-sysctl](https://www.kernel.org/doc/Documentation/networking/nf_conntrack-sysctl.txt)  
3. [wiki netfilter](https://en.wikipedia.org/wiki/Netfilter)  
4. [Netfilter's connection tracking system](http://people.netfilter.org/pablo/docs/login.pdf)  
5. [Iptables-tutorial](https://www.frozentux.net/documents/iptables-tutorial/)
6. [openstack底层技术-netfilter框架研究](https://opengers.github.io/openstack/openstack-base-netfilter-framework-overview/)
