---
title: route手册
categories:
  - man
tags:
  - route
keywords: man,route
date: 2017-12-02 23:47:00
---

`route`显示和操作IP路由表。
<!-- more -->
# 概要
```
route [-CFvnee]

route [-v]  [-A  family] add [-net|-host] target [netmask Nm] [gw Gw] [metric N] 
      [mss M] [window W] [irtt I] [reject] [mod] [dyn] [reinstate]  [[dev] If]

route [-v]  [-A  family] del [-net|-host] target [gw Gw] [netmask Nm] [metric N] [[dev] If]

route [-V] [--version] [-h] [--help]
```

# 描述
`route`操作内核的IP路由表。它主要用于在设置网卡到特定主机或者网络的表态路由表。

当使用`add`或者`del`选项，`route`会修改路由表。其他选项，`route`会打印当前路由表的内容。


# 参数
- `-A family` 使用指定的地址族(例如`inet`，使用`route --help`查看完整列表)。
- `-F` 操作内存的FIB(Forwarding Information Base)路由表，这是默认选项。
- `-C` 操作内存路由表缓存。
- `-v` 选择berbose操作。
- `-n` 显示数字地址，而不要尝试解释符号主机名。这对于检查为什么路由到名字空间不生效非常有用。
- `-e` 使用netstat的格式显示路由表。`-ee`会产生一个非常长行，显示路由表的所有参数。
- `del` 删除一条路由。
- `add` 增加一条新路由。
- `target` 目标网络或者主机，你可以提供一个点分式的IP地址或者主机/网络名。
- `-net` 目标是一个网络。
- `-hone` 目标是一个主机。
- `netmask NM` 增加网络路由，使用指定的掩码。
- `gw GW` 通过网关进行路由。注意，特定的网关必须可达的。这意味着，你必须提前设置一条静态路由到这个网关。
          如果指定的地址是你的本地接口，它会决定哪些包会被路由到这个接口。
- `metric M` 设置路由表中的metric域为M。
- `mss M` 设置通过这个路由的连接mss(TCP Maximum Segment Size)的值为M字节。它的默认值是设置的MTU减去包头，
          或者mtu发现机制生效的话，则为最小的MTU。这个在另一端不支持mtu发现的网络上设置强制使用更小的TCP包。
- `window W` 设置通过这个路由的TCP窗口值为W字节。
- `irtt I` 设置通过这个路由的TCP连接的irtt(initial round time)为I毫秒(1-12000)。
- `reject` 安装一条屏蔽路由，它强制一个路由查找失败。
- `mod,dyn,reinstate` 安装一个动态或者可以修改的路由。这些标识是为了用来诊断和默认的被路由守护程序设置。
- `dev If` 强制路由关联指定的设备。如果不使用，则由内核去决定使用哪个设备。大部分情况下都不需要指定。
           如果`dev If`是命令行中的最后一个参数，那么它可以会被忽略掉。

# 例子
```sh
route add -net 127.0.0.0 netmask 255.0.0.0 dev lo
```
增加环回条目，使用掩码`255.0.0.0`和关联到lo的设备上。

```sh
route add -net 192.56.76.0 netmask 255.255.255.0 dev eth0
```
增加一条路由到本地网络`192.56.76.x`通过eth0。这里的dev可以忽略。

```sh
route del default
```
删除当前的默认路由。

```sh
route add default gw mongo-gw
```
增加一个默认路由。所有的使用这个路由的包都会发到mongo-gw的网关上。

```sh
route add ipx4 s10
```
增加路由到ipx4主机，通过SLIP接口。

```sh
route add -net 192.57.66.0 netmask 255.255.255.0 gw ipx4
```
添加网络`192.57.66.x`到网络前置路由到SLIP接口。

```sh
route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0
```
设置所有的D类网络路由通过eth0。

````sh
route add -net 10.0.0.0 netmask 255.0.0.0 reject
````
这个安装一个屏蔽`10.x.x.x`的路由。

# 输出
内核路由表以以下的列组织显示。
## Destination
目标网络或者目标主机。

## Gateway
网关地址，或者`*`如果没设的话。

## Netmask
目标网络的网关。`255.255.255.255`是目标主机，`0.0.0.0`是默认路由。

## Flags
支持的flags如下：

| flag | 说明                       |
|:----:|----------------------------|
|   U  | 路由生效                   |
|   H  | 目标是一个主机             |
|   G  | 使用网关                   |
|   R  | 恢复路由为动态路由         |
|   D  | 守护进程安装由或者重新调配 |
|   M  | 守护进程修改或者重新调配   |
|   A  | 由addrconf安装             |
|   C  | 缓存条目                   |
|   !  | 屏蔽路由                   |

## Metric
目标的距离。最近的内核已经不使用，但是路由守护进程需要用到。

## Ref
这个路由的引用数。linux内核不使用。

## Use
查表数。通过`-F`或者`-C`可以指定不命中或者命中的值。

## Iface
这个路由中会发送到的接口。

## MSS
这个路由表的默认mss。

## Window
这个路由表的默认窗口大小。

## irtt
内核使用这个来猜最好的TCP协议参数，而不用等待答案。

## HH (cached only)
ARP条目的数据和缓存路由到指向硬件头缓存。

## Arp (cached only)
当前缓存硬件地址是否到期。
