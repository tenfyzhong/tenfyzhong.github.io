---
title: 后台程序员应该懂的linux监控命令
date: 2019-07-04 14:50:14
---

这是一系列用于查看linux状态的监控命令指南。作为一台后台程序员，除了会写代码外，
还要懂得查看当前的服务器状态是否存在异常，出现异常时去分析问题出在哪里及怎么处理。
<!-- more -->

# cpu
uptime: {% post_link linux-monitoring-uptime linux uptime查看负载 %}

# 内存
free: {% post_link linux-monitoring-free linux free查看内存状态 %}

# 磁盘
df: {% post_link linux-monitoring-df linux df查看磁盘空间 %}

iostat

iotop

# 文件系统
lsof

# 网络
iftop

netstat

tcpdump

# 其他 
dmesg

top

vmstat

strace

ltrace

