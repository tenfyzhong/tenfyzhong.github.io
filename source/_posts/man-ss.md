---
title: ss手册
categories:
  - man
tags:
  - man
  - ss
date: 2017-10-16 18:52:14
keywords: man,ss
---

`ss`另一个研究socket的工具。

`ss`可以用来dump socket的统计数据。它可以像netstat一样进行展示信息。但是它可以比
其他工具展示更多的TCP和状态信息。

<!-- more -->

# 概要
```bash
ss [options] [ FILTER ]
```

# 参数
当不传参数给`ss`的时候，它显示打开的非监听且已经established连接的socket(例如TCP/UDP/UNIX)。

- `-h,--help` 显示帮助信息。
- `-V,--version` 显示版本信息。
- `-n,--numeric` 不要解释服务名。
- `-r,--resolve` 尝试解析数字的地址和端口。
- `-a,--all` 显示所有的监听和非监听(对于TCP意味着established连接)的socket。
- `-l,--listening` 只显示监听的socket(默认是忽略的)。
- `-o,--options` 显示timer信息。
- `-e,--extended` 显示socket的详细信息。
- `-m,--memory` 显示socket的内存使用。
- `-p,--processes` 显示使用socket的进程。
- `-i,--info` 显示TCP的内部信息。
- `-s,--summary` 显示总结统计信息。
- `-Z,--context` 类似于`-p`参数，但是同时显示进程的安全上下文。
    对于`netlink(7)` socket，启动进程上下文显示如下：
    1. 如果pid是有效的，则显示进程上下文。
    1. 如果目标是内核(pid=0)，则显示内存最初的上下文。
    1. 如果一个唯一的标识符已经被内核或者`netlink`用户申请，则显示"unavailable"。
       这基本表明一个进程拥有不只一个的活跃的`netlink` socket。
- `-z,--contexts` 类似于`-Z`参数，但是同时显示socket上下文。socket上下文从相关的inode提取，
  内时它也不是内存拥有的实际socket。默认的，socket会被创建进程的上下文打上标签，
  然而显示的上下文会反射出任意的安全角色、类型和规则，所以它很有参考价格。
- `-N NSNAME,--net=NSNAME` 切换到特定的网络名字空间。
- `-b,--bpf` 显示socket BPF过滤器(只有管理员才能获得这些信息)。
- `-4,--ipv4` 只显示IPv4的socket(类似于`-f inet`)。
- `-6,--ipv6` 只显示IPv6的socket(类似于`-f inet6`)。
- `-0,--packet` 显示packet的socket(类似于`-f link`)。
- `-t,--tcp` 显示TCP socket。
- `-u,--udp` 显示UDP socket。
- `-d,--dccp` 显示DCCP socket。
- `-w,--raw` 显示RAW socket。
- `-x,--unix` 显示Unix domain socket(类似于`-f unix`)。
- `-f FAMILY,--family=FAMILY` 显示FAMILY的socket。目前family支持以下的值:`unix`,`inet`,`inet6`,`link`,`netlink`。
- `-A QUERY,--query=QUERY,--socket=QUERY` 显示特定规则的socket表，以逗号分隔。
  支持以下的标志符：`all`, `inet`, `tcp`, `udp`, `raw`, `unix`, `packet`, 
  `netlink`, `unix_dgram`, `unix_stream`, `unix_seqpacket`, `packet_raw`, `packet_dgram`。
- `-D FILE,--diag=FILE` 不显示任何信息，只是把socket的raw信息dump到文件。如果FILE的值是`-`，则使用标准输出。
- `-F FILE,--fileter=FILE` 从FILE中读取过滤器信息。文件中的每一行是类似于逗号分隔的规则。
  如果FILE的值是`-`，则使用标准输入。
- `FILTER := [ state STATE-FILETER ] [ EXPRESSION ]` 请阅读官方文档(Debian package iproute-doc)了解详情的过滤器信息。

# 状态过滤器
状态过滤器允许构造任意的匹配状态。它的语法是一系列的状态关键字。

可用的标志符有：
所有的TCP 标准状态: `established`, `syn-sent`, `syn-recv`, `fin-wait-1`, `fin-wait-2`,
`time-wait`, `closed`, `closed-wait`, `last-ack`, `listen`, `closing`。  
`all` - 所有的状态。  
`connected` - 除了`listen`和`closed`的所有状态。  
`synchronized` - 除了`syn-send`的所有`connected`状态。  
`bucket` - minisockets的状态，也就是说`time-wait`和`syn-recv`。  
`big` - 与`bucket`相反的状态。  

# 使用例子
`ss -t -a` 显示所有的TCP socket。

`ss -t -a -Z` 显示所有的tcp socket和selinux安全上下文。

`ss -u -a` 显示所有的UDP socket。

`ss -o state established '( dport = :ssh or sport = :ssh )'` 显示所有ssh established的连接。

`ss -x src /tmp.X11-unix/*` 找出所有连接到X服务器的本地进程。

`ss -o state fin-wait-1 '( sport = :http or sport = :https )' dst 193.233.7/24` 
列出所有连接到193.233.7/24网络且状态为`FIN-WAIT-1`的tcp socket和它们的timer。

