---
title: ip手册
categories:
  - man
tags:
  - man
  - ip
date: 2017-10-17 19:30:49
keywords: man,ip
---

`ip`显示和操作路由、设备、路由策略、隧道的工具。

<!-- more -->
# 概要
```bash
ip [ OPTIONS ] OBJECT { COMMAND | help }

ip [ -force ] -batch filename

OBJECT := { link | addr | addrlabel | route | rule | neigh | ntable | tunnel | tuntap | maddr | mroute |
       mrule | monitor | xfrm | netns | l2tp | tcp_metrics }

OPTIONS := { -V[ersion] | -s[tatistics] | -r[esolve] | -f[amily] { inet | inet6 | ipx | dnet | link } |
       -o[neline] }
```

# 参数
- `-V,-Version` 打印版本信息。
- `-b,-batch <FILENAME>` 从文件或者标准输入读取命令并执行它们。只要一发现错误就会引起`ip`退出。
- `-force` 在batch模式下，当发生错误时不要退出。如果执行过程中出现错误，则退出码为非0。
- `-s,-stats,-statistics` 显示更多信息。如果这个参数出现多次，则输出的信息会增加。
  对于一个rule，输出信息是统计信息或者某时间的值。
- `-l,-loops <COUNT>` 指定`ip addr flush`尝试的次数。默认值是10。0会一直到删除所有的地址。
- `-f,-family <FAMILY>` 指定family协议。可以是以下的值:`inet`, `inet6`, `bridge`, `ipx`, `dnet`, `link`。
  如果这个参数没指定，会从其他参数中进行猜测。如果其他的参数不能猜测出使用的协议，
  `ip`会回退到默认的值，一般是`inet`或者`any`。`link`是一个特殊的family标识符，
  意味着不涉及网络协议。
- `-4` `-family inet`的缩写。
- `-6` `-family inet6`的缩写。
- `-B` `-family bridge`的缩写。
- `-D` `-family decnet`的缩写。
- `-I` `-family ipx`的缩写。
- `-0` `-family link`的缩写。
- `-o,-oneline` 一行输出一个记录。方便使用`wc`或者`grep`等。
- `-r,-resolve` 使用主机名替换主机地址。

# 命令语法
## OBJECT
- `address` 设备的地址。
- `addrlabel` 选择地址配置的label。
- `l2tp` 隧道以太网ip(L2TPv3)。
- `link` 网络设备。
- `maddress` 广播地址。
- `monitor` 观察连接器信息。
- `mroute` 广播路由缓存。
- `mrule` 广播路由规则数据库的规则。
- `neighbour` 管理`ARP`或者`NDISC`缓存。
- `netns` 管理网络命令空间。
- `ntable` 管理neighbor缓存操作。
- `route` 路由表。
- `rule` 路由规则数据的规则。
- `tcp_metrics/tcpmetrics` 管理TCP metrics。
- `tunnel` IP隧道。
- `tuntap` 管理TUN/TAP设备。
- `xfrm` 管理IPSec策略。

所有的object都可以写全称或者缩写，例如`address`可以写成`addr`和`a`。

## COMMAND
指定对object的操作。针对不同的object有不同的操作集。通常，可以是`add`, `delete`, 
`show`(或者`list`)，但是有一些object不支持所有的这些操作，或者支持一些附加的命令。
`help`命令对于所有的object都支持，它打印对应object可用的命令和参数规则。

如果不指定命令，会使用默认的命令。一般都是`list`，如果该object没有`list`命令则为`help`。
