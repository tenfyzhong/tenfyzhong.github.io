---
title: ntp客户端同步时间
categories:
  - misc
tags:
  - linux
  - ntp
date: 2019-05-13 10:03:52
keywords: ntpdate,ntp
---

linux使用ntp客户端自动更新时间。
<!-- more -->

使用ntp客户端工具ntpdate定期执行来进行同步时间。ntpdate只需要加ntp服务器的机器即可。
假如ntp的服务器为10.1.2.3，则同步命令为`ntpdate 10.1.2.3`。同步完时间后，
还可以使用`hwclock -w`来同步到硬件时间。

我们可以使用root用户的crontab来配置定期同步，如5分钟自动同步
```sh
*/5 * * * * /usr/sbin/ntpdate 10.1.2.3; /sbin/hwclock -w
```

