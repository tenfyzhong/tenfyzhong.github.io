---
title: strace手册
categories:
  - man
tags:
  - strace
date: 2017-10-27 08:43:05
keywords: man,strace
---

`strace`跟踪系统调用和信号。
<!-- more -->
# 概要
```bash
strace [-CdffhiqrtttTvVxxy] [-In] [-bexecve] [-eexpr]...  
       [-acolumn] [-ofile] [-sstrsize] [-Ppath]... 
       -ppid... / [-D] [-Evar[=val]]... [-uusername] 
       command [args]

strace -c[df] [-In] [-bexecve] [-eexpr]...  [-Ooverhead] 
       [-Ssortby] -ppid... / [-D] [-Evar[=val]]... 
       [-uusername] command [args]
```


# 描述
最简单的使用方法是`strace`运行指定的命令一直到它退出。它捕捉和记录进程调用的系统调用和被进程接收的信号。
每个系统调用的名字，它的参数和返回值会被打印到标准错误，如果指定`-o`参数则输出到指定的文件。

`strace`不用重新编译就可以重复跟踪。

跟踪信息的每一行包含系统调用名，跟着是它的参数和返回值。一个跟踪`cat /dev/null`的例子：
```
open("/dev/null", O_RDONLY) = 3
```

错误(通常返回值为-1)还有错误名和错误信息。
```
open("/foo/bar", O_RDONLY) = -1 ENOENT (No such file or directory)
```

信号会打印信号名和信息信息。一个捕捉跟踪`sleep 666`的例子：
```
sigsuspend([] <unfinished ...>
--- SIGINT (Interrupt) ---
+++ killed by SIGINT +++
```

如果一个系统调用在执行过程中被另一个线程/进程的系统调用打断，`strace`会尝试保存事件的顺序，
把正在进程中的调用标记为`unfinished`。当调用被恢复执行，则标记为`resumed`。
```
[pid 28772] select(4, [3], NULL, NULL, NULL <unfinished ...>
[pid 28779] clock_gettime(CLOCK_REALTIME, {1130322148, 939977000}) = 0
[pid 28772] <... select resumed> )      = 1 (in [3])
```

信号处理中断一个可以重新启动的系统调用与内核终止一个系统调用不同，它会安排信号处理完后立即重新运行。
```
read(0, 0x7ffff72cf5cf, 1)              = ? ERESTARTSYS (To be restarted)
--- SIGALRM (Alarm clock) @ 0 (0) ---
rt_sigreturn(0xe)                       = 0
read(0, ""..., 1)                       = 0
```

参数会以符号的方式打印出来。下面是一个shell定向`>>xyzzy`的例子：
```
open("xyzzy", O_WRONLY|O_APPEND|O_CREAT, 0666) = 3
```

结构体指针会解引用和打印成员。所有的参数如果可以都会打印成C语言的格式。例如，
`ls -l /dev/null`命令会捕捉到这样的信息：
```
lstat("/dev/null", {st_mode=S_IFCHR|0666, st_rdev=makedev(1, 3), ...}) = 0
```
注意`struct stat`参数是怎么解引用和怎么展示成员的。特别地，观察`st_mode`成员会解码成符号和数字的位或。
这个例子中的第一个参数是传入给系统调用的，第二个参数是转出的。因为系统调用失败，
输出参数会被修改，参数有可能不会一直被解引用。例如使用`ls -l`打开一个不存在的文件会产生以下的输出：
```
lstat("/foo/bar", 0xb004) = -1 ENOENT (No such file or directory)
```

字符指针会被打印成C字符串。不可见字符会打印成普通的C语言转义代码。只有字符串的前
`strsize`个字符会被打印(默认是32)，更长的字符串在双引号之后会有一个省略号。
这里有一个`ls -l`的例子：
```
read(3, "root::0:0:System Administrator:/"..., 1024) = 422
```

简单的指针和数组会使用中括号打印，每个成员以逗号分隔。以下是一个`id`命令的例子：
```
getgroups(32, [100, 0]) = 2
```

另外，位集也使用中括号打印，但是成员之间使用空格分隔，而不是逗号。下面是shell准备执行一个外部命令的例子：
```
sigprocmask(SIG_BLOCK, [CHLD TTOU], []) = 0
```
这里的第二个参数是一个位集，包含两个信号`SIGCHLD`和`SIGTTOU`。另一些案例中，
位集是比较满的，会打印没设置的成员，它会以一个`~`开头。例如：
```
sigprocmask(SIG_UNBLOCK, ~[], NULL) = 0
```
这里的第二个参数打印了信号的全集。


# 参数
- `-c` 计算时间、系统调用、错误的次数和程序退出时打印总结信息。在linux上，
  这会试图打倒系统时间(CPU运行时间)，而不是实际的时间。如果`-c`结合`-f`或者`-F`使用，
  会聚合所有的跟踪进程。
- `-C` 像`-c`一样，但是当进程还在执行时也会打印标准输出。
- `-D` 以分离孙子进程运行跟踪程序。
- `-d` 显示`strace`的调试信息到标准错误。
- `-f` 跟踪当前跟踪进程fork, vfork, clone出来的子进程。注意，`-p PID -f`会附加到当前进程的所有线程。
- `-ff` 如果`-o filename`有作用的，则每个跟进进程都会写到`filename.pid`文件去，pid是进程号。
  这个参数与`-c`不兼容，它不会去记录每个进程的计数。
- `-F` 已被`-f`替换。
- `-h` 打印帮助信息。
- `-i` 打印系统调用的指令指针。 
- `-q` 抑制附加、分离等信息。重定向到文件会自动产生这个效果。
- `-qq` 如果指定两个`q`，会抑制进程的退出状态。
- `-r` 打印与上一条系统调用的相对时间。 
- `-t` 每行打印当天的时间。
- `-tt` 指定两个`t`，会打印到微秒。
- `-ttt` 指定三个`t`，打印时间戳，并且打印到毫秒精度。
- `-T` 打印每个系统调用的耗时。
- `-v` 打印未缩写版本的环境变量、统计、终端接口等调用。这些结构在调用中是非常公用的，
  所以默认的行为只打印结构合理的子集。
- `-V` 打印`strace`的版本号。
- `-x` 把非ASCII字符串打印成十六进制的格式。
- `-xx` 把所有的字符串打印成十六进制的格式。
- `-y` 打印文件描述符相关的路径。
- `-a column` 把返回在指定的列对齐，默认是40。
- `-b syscall` 如果到达了指定的syscall，则从当前跟踪的进程分离。目前只支持`execve`系统调用。
  这对于需要跟踪多线程进程是非常有用的，需要指定`-f`，但是又不想跟进它的子进程。
- `-e expr` 指定跟踪事件和怎么跟踪它们的修饰符表达式。表达式格式如下：  
  `[qualifier=][!]value1[,value2]...`  
  qualifier是以下的一个值：`trace`, `abbrev`, `verbose`, `raw`, `signal`, `read`, `write`。
  `value`是qualifier相关的一个符号或者数字。默认的qualifier是trace。使用感叹号对值的集合取反。
  例如，`-e open`意味着`-e trace=open`，捕捉所有的open系统调用。相反的，`-e trace=!open`
  意味着除了open外的所有系统调用。另外还有all和none表示所有和空。  
  注意，在一些shell上，感叹号会展开成历史表达式，即使在括号里面。这种情况下需要使用反斜杠转义。
- `-e trace=set` 跟踪指定集合的系统调用。结合`-c`可以查看指定系统调用的时间和次数。
  例如，`trace=open,close,read,write`意味着只跟踪这四个信号。默认值是`trace=all`。
- `-e trace=process` 跟踪所有涉及进程管理的系统调用。方便于观察fork, wait, exec的过程。
- `-e trace=network` 跟踪所有网络相关的系统调用。
- `-e trace=signal` 跟踪所有信号相关的系统调用。
- `-e trace=ipc` 跟踪所有IPC相关的系统调用。
- `-e trace=desc` 跟踪所有文件描述符相关的系统调用。
- `-e trace=memory` 跟踪所有内存映射相关的系统调用。
- `-e abbrev=set` 缩写每个打印成员的大结构体。默认是`abbrev=all`，`-v`参数相当于`abbrev=none`。
- `-e verbose=set` 解引用指定集合系统调用的结构体。默认是`verbose=all`。
- `-e raw=set` 输出指定调用集体的原始信息，不解码参数。这个参数会使所有的参数都以十六进制进行打印。
  这对于不相信解码器或者想看参数实际的数字值非常有用。
- `-e signal=set` 跟踪指定的信号集。默认是`signal=all`。例如，`signal=!SIGIO`(或者`signal=!io`)
  指定不跟踪SIGIO信号。
- `read=set` 以十六进制和ASCII打印所有从set指定的文件描述符读到的数据。例如，
  查看从文件描述符3和5中输入的数据使用`-e read=3,5`。
- `-e write=set` 以十六进制和ASCII打印所有从set指定的文件描述符写的数据。例如，
  查看写入到文件描述符3和5的数据使用`-e write=3,5`。
- `-I interruptible` `strace`的时候可以被信号中断(例如按`^C`)。1: 没有信号被阻塞。
  2: 解码系统调用的时候，致命的信号被阻塞(默认)。3: 致命信号一直被阻塞(`-o FILE PROG`的时候默认)。
  4: 致命信号和SIGTSTP(`^Z`)都一直阻塞(对于输出到文件而禁止`^Z`终止进程时有用)。
- `-o filename` 输出到文件filename，而不是标准错误。如果指定`-ff`则输出到filename.pid。
  如果参数以`|`或者`!`开头，剩下的参数当成一个命令对待，所有的输出都通过管道传给它。
  这对于把调试输出管道传输到一个程序而不影响程序的重定义是非常方便的。
- `-O overhead` 设置跟踪系统调用的开销超时。
- `-p pid` 附加到指定的进程然后开始跟踪。任意时刻都可以使用`^c`来终止跟踪。`strace`
  从跟踪的进程中分离，让它们可以继续执行。多个`-p`可以指定跟踪多个进程。
- `-P path` 只跟踪访问path的系统调用。多个`-P`可以指定多个path。
- `-s strsize` 指定字符串最大的打印字符数，默认是32。文件名都会全部打印。
- `-S sortby` 指定`-c`统计的排序规则，支持的值有：`time`, `calls`, `name`, `notion`(默认是`time`)。
- `-u username` 指定的用户运行命令。这只对于root用户并且有正确的setuid或者setgit的程序有效。
- `-E var=val` 指定环境变量运行。
- `-E var` 从继承的环境变量是删除后再运行。


# 诊断
当command退出时，`strace`也以同样的状态退出。如果command被一个信号中断，`strace`
会以同这的信号中断自己。所以`strace`可以当成一个透明的适配器。

当使用`-p`，`strace`的退出状态是0，除非在跟踪的时候有一个非预期的错误产生。


