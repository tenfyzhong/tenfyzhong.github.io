---
title: strace命令介绍
date: 2017-09-18 20:22:26
categories: 后台
tags: 
  - linux
  - man
keywords:
  - strace
---

linux下跟踪系统调用和信号的命令。

<!-- more -->

# 概要
```bash
strace  [  -dDffhiqrtttTvVxx ] [ -acolumn ] [ -eexpr ] ...  [ -ofile ] [ -ppid ] ...  [ -sstrsize ] [ -uusername ] [ -Evar=val ] ...  [-Evar ] ...  [ command [ arg ...  ] ]
strace -c [ -D ] [ -eexpr ] ...  [ -Ooverhead ] [ -Ssortby ] [ command [ arg ...  ] ]
```

# 描述
记录系统调用和收到的信号打到标准错误里或者-o指定的文件中。  
`strace`是一个好用的调试、诊断工具。  

输出结果包括系统调用的错误，括号包着的参数以及等号后面的为返回值。  
信号的输出结果为信号值和对应的字符串描述。  

>[pid 28772] select(4, [3], NULL, NULL, NULL <unfinished ...>  
>[pid 28779] clock_gettime(CLOCK_REALTIME, {1130322148, 939977000}) = 0  
>[pid 28772] <... select resumed> )      = 1 (in [3])  

这里后面的unfinished表示当前的系统调用(select)还没完成，就被其他的调用(clock\_gettime)给中断了，后面会当clock\_gettime完成后，会恢复调用  

# 常用选项
`-c` 统计系统的调用时间次数等，打印一个表格输出   
`-D` 以一个分离的子进程来调用  
`-d` 显示strace自己的debug信息到标准错误  
`-ff` 如果指定`-o filename`选项，则会将输入打到`filename.pid`上，与`-c`不兼容  
`-i` 打印系统调用的指针  
`-r` 打印每个系统调用的时间点，与程序启动的时间为起始  
`-t` 打印每个系统调用的时间点，精确到秒  
`-tt` 打印每个系统调用的时间点，精确到微秒  
`-ttt` 打印每个系统调用的时间点，精确到微秒，秒以时间戳的形式显示  
`-T` 打印每个系统调用的耗时，在一行的最后
`-x` 将非ascii字符串以16进制的方式打印  
`-xx` 将所有的字符串都以16进制的方式打印  
`-e expr` 指定的过滤，expr可以是*trace, abbrev, verbose, raw, signal, read write*，值跟其expr相关，默认是trace，如`-eopen`跟`-e trace=open`一致。具体的到下面的过滤章节再分析。  
`-o filename` 将结果写到filename中  
`-p pid` attach到特定的进行去trace  
`-s strsize` 指定打印的最大字符数，打到文件时忽略，默认是32  
`-S sortby` `-c`选项时输出的排序  
`-E var=val` 使用var环境变量来进行command
`-E var` 移出var环境变量

# 过滤
这里对`-e trace`指定的过滤进行讲解，以下的二级标题是`-e`指定的类型，其下为对应的值，如第1个为：  
```bash
strace -e trace=set
```

## trace
- set 指定特定的系统调用，如`trace=open,close,read,write`只trace这四种类型 
- file trace提供了文件名作为参数的系统调用  
- process trace所有的进程管理器调用，这对于观察fork, wait, exec非常有用  
- network trace所有以网络相关的系统调用    
- signal trace所有信号相关的系统调用  
- ipc trace所有与ipc相关的系统调用
- desc trace所有文件描述符相关的系统调用

# 例子
查看进程号2000的网络调用，同时打印每个的耗时和系统调用时的时间戳  
```bash
strace -p 2000 -ttt -T
```
