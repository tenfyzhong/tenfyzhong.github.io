---
title: free手册
categories:
  - man
tags:
  - free
keywords: man,free
date: 2017-11-06 15:11:00
---

显示系统空闲和已经使用的内存数。
<!-- more -->
# 概要
```
free [options]
```

# 描述
`free`显示操作系统所有的空闲和已经使用的物理和swap内存，同时也显示内存使用的buffer。
shared列表示MemShared值(2.4的内核)或者Shmem值(2.6及以后的内核)，从`/proc/meminfo`中读取。
如果内核没有导出任何实体，则为0。


# 参数
- `-b`,`--bytes` 以bytes为单位显示内存信息。
- `-k`,`--kilo` 以kilobytes为单位显示内存信息，这是默认值。
- `-m`,`--mega` 以megabytes为单位显示内存信息。
- `-g`,`--giga` 以gigabytes为单位显示内存信息。
- `--tera` 以terabytes为单位显示内存信息。
- `-h`,`--human` 所有的域都缩成3个数字及对应的单位显示。支持的单位有B, K, M, G, T。
  如果是petabytes的数据，则会以terabytes显示，并且不会与头对齐。
- `-c`,`--count` `count` 显示count次，需要与`-s`一起使用。
- `-l`,`--lohi` 显示最高最低的内存统计数据。
- `-o`,`--old` 以旧的格式显示。唯一的区别是不显示"buffer adjusted"那一行。
- `-s`,`--seconds` `secons` 每隔seconds秒显示一次结果。可以使用小数点。
- `--si` 使用1000做为基数，而不是1024。
- `-t`,`--total` 增加一行显示总数。
- `--help` 打印帮助信息。
- `-V`, `--version` 显示版本信息。

# 相关文件
`/proc/meminfo` 内存信息。
