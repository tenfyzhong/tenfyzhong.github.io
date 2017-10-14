---
title: nc手册
categories:
  - man
tags:
  - man
  - netcat
date: 2017-10-14 19:10:24
keywords: man,netcat
---

`nc`一个用于监听或者发送tcp/udp包的工具。另外它还可以进行端口扫描。  
这里介绍的`nc`工具功能以linux版为准，其他unix,sun主机的参数不一定完全兼容。  

<!-- more -->
# 概要
```
nc [-46bCDdhklnrStUuvZz] [-I length] [-i interval] [-O length] [-P proxy_username] 
   [-p source_port] [-q seconds] [-s source] [-T toskeyword] [-V rtable] [-w timeout]
   [-X proxy_protocol] [-x proxy_address[:port]] [destination] [port]
```

# 描述
`nc`(或者`netcat`)工具是一个用于发起tcp, udp, UNIX-domain socket通信的工具。
它可以打开tcp连接，发送udp包，监听任意的tcp/udp端口，扫描端口，它不但可以处理IPv4，
还可以处理IPv6。相比于`telnet`，`nc`接口更加人性化，它可以把错误信息发送到标准错误，
而不是标准输出。

参数如下：
- `-4` 强制只使用IPv4。
- `-6` 强制只使用Ipv6。
- `-b` 允许广播。
- `-C` 行结束符发送CRLF。
- `-D` 开启socket上的debug。
- `-d` 不要试图从标准输入读取。
- `-h` 打印帮助信息。
- `-I length` 指定tcp接收buffer的长度。
- `-i interval` 指定发送和接收的间隔时间。同时它也影响多个端口间的连接时间。
- `-k` 当前连接完成后，强制继续监听其他的连接。如果它不跟`-l`一起使用，会产生错误。
- `-l` 指定进行监听连接，而不是连接到其他主机上。它不能结合`-p`, `-s`, `-z`参数一起使用，
  否则会产生错误。另外，它会忽略`-w`指定的超时。
- `-n` 不做dns解析和回环地址解析，所以不能使用主机名进行连接。
- `-O length` 指定tcp发送buffer的长度。
- `-P proxy_username` 指定代理服务器鉴权的用户名，如果不指定用户名，则不需要鉴权。
  代理鉴权只支持HTTP CONNECT代码。
- `-q seconds` 从标准输入接收到EOF后，等待特定的秒数后再退出。如果seconds是一个负数，则一直等待不退出。
- `-r` 指定源、目标端口随机选择，而不是从一个范围中顺序选择或者系统分配。
- `-S` 启动RFC 2385 TCP MD5签名参数。
- `-s source` 指定IP的端口去发送网络包。对于UNIX-domain socket，创建一个本地临时文件来接收数据包。
  结合`-l`参数使用会产生错误。
- `-T toskeyword` 切换IPv4 TOS的值。toskeyword可以是以下的值：`critical`, `inetcontrol`,
  `lowcost`, `lowdelay`, `netcontrol`, `throughput`, `reliability`，或者是DiffServ Code: 
  `ef`, `af11` ... `af43`, `cs0` ... `cs7`，或者是一个十六进制或者十进制数。
- `-t` 使`nc`使用RFC 854请求，而不需要RFC 854响应。这使得`nc`响应`telnel`连接。
- `-U` 指定使用UNIX-domain socket。
- `-u` 指定使用UDP替换默认的TCP。对于UNIX-domain socket，使用数据报socket替换流socket。
  如果使用UNIX-domain socket，会在`/tmp`下创建一个临时socket，除非使用`-s`参数。
- `-V rtable` 设置路由表。默认值是0。
- `-v` 使`nc`输出更多的详细的输出。
- `-w timeout` 连接等待timeout才能进行established状态。`-l`参数下，`-w`参数不产生效果。
  也就是说`nc`会一直监听，无论是否有`-w`参数。默认值是没有超时。
- `-X proxy_protocol` 使用指定的代理协议。支持的协议有有"4"(SOCKS v.4)，
  "5"(SOCKS v.5)和"conneect"(HTTPS proxy)。如果没指定，默认使用SOCKS v.5。
- `-x proxy_address[:port]` 指定代理的地址和端口。如果没指定端口，则使用公认的端口。
  SOCKS使用1080，HTTPS使用3128。
- `-Z` DCCP模式。
- `-z` `nc`只扫描监听守候程序，而不发送数据。结合`-l`参数使用会产生错误。


destination可以是一个数字IP地址或者一个符号域名(除非使用`-n`参数)。一般情况下，
destination必须指定，除非指定`-l`参数(使用本地地址)。对于UNIX-domain socket，
destination是必须的，指定了连接的socket或者监听的socket。

port可以是一个单独的数字或者一个范围的端口。范围端口格式为nn-mm。一般情况下，目标
端口必须指定，除非指定`-U`参数。

# 客户端/服务器模型
使用`nc`可以非常方便的建立一个基本的客户端/服务器模型。在一个终端上开始`nc`监听一个特殊的端口进行监听。例如：
```bash
nc -l 1234
```

现在`nc`监听在1234端口上等待连接。在另一个终端或者另一个机器上，连接到刚刚监听的机器和端口上：
```bash
nc 127.0.0.1 1234
```
现在两个端口已经连接了连接，任意在第二个终端的输入都会显示在第一个终端上，反过来也一样。
连接建立后，`nc`就不关心哪一端是服务器，哪一端是客户端了。可以通过EOF(`^D`)来结束连接。


`netcat`没有`-c`和`-e`参数，但是连接建立后可以使用文件描述符重定向来执行命令。
打一个端口让任何人连接并执行任意的命令是非常危险的，必须小心使用。以下是使用方法，
在服务端：
```bash
rm -rf /tmp/f; mkfifo /tmp/f
cat /tmp/f | /bin/sh -i 2>&1 | nc -l 127.0.0.1 1234 > /tmp/f
```
在客户端：
```bash
nc host.example.com 1234
$ #(shell prompt from host.example.com)
```

执行之后，创建了一个`/tmp/f`的fifo管道，并且`nc`在服务器端监听127.0.0.1的1234端口。
客户端连接后，服务器端执行命令后，把输出和提示符返回给客户端。

当连接结束后，`nc`也会退出。使用`-k`可以保持继续监听。最后不要忘记删除`/tmp/f`文件。

# 数据传输
在上一节的基础上做些扩展，就可以建立一个数据传输模型。一端的任意输入都会在另一端输出，
输入输出可以简单的通过文件重定义进行转发。

使用`uc`在一端监听并且捕捉输出到文件：
```bash
nc -l 1234 > filename.out
```

在另一个机器上，连接到监听的进程，通过文件重定向进行输入：
```bash
nc host.example.com 1234 < filename.in
```

文件传输后，连接会自动关闭。

# 发送给服务器
有时直接发送数据给服务器比交互模式更有用。它可以用来帮助调试，可以通过客户端发送
请求来查看响应了什么数据。比如用来获取一个网站的主页：
```bash
printf "GET / HTTP/1.0\r\n\r\n" | nc host.example.com 80
```

另外它还可以使用sed等工具来获取返回的头。 

只要知道了服务器需要知道的包格式，就可以构造包来请求服务器。另一个例子，
可以使用以下的命令来发送一个邮件到SMTP服务器：
```bash
nc [-C] localhost 25 << EOF
HELO host.example.com
MAIL FROM:<user@host.example.com>
RCPT TO:<user2@host.example.com>
DATA
Body of email.
.
QUIT
EOF
```

# 端口扫描
知道目标机器上打开的端口及其运行的服务有时非常有用。`-z`参数可以检查打开的端口，
而不是建立一个连接。通常，结合`-v`参数可以非常有用的把详细输出到标准错误。

例如：  
>`nc -zv host.example.com 20-30`
>Connection to host.example.com 22 port [tcp/ssh] succeeded!
>Connection to host.example.com 25 port [tcp/smtp] succeeded!

这里指定了扫描20到30端口，它以增长的顺序进行搜索。

也可以指定特定的端口进行扫描。  
> `nc -zv host.example.com 80 20 22`
> nc: connect to host.example.com 80 (tcp) failed: Connection refused
> nc: connect to host.example.com 20 (tcp) failed: Connection refused
> Connection to host.example.com port [tcp/ssh] succeeded!

扫描的顺序为给出的顺序。

另外，有时知道哪个服务器其其哪个版本在运行也是非常有用的。这些信息通常包含在欢迎信息上。
为了取得这些信息，需要先建连接，取得欢迎信息后断开连接。可以通过`-w`指定超时或者使用`QUIT`命令。  
> `echo "QUIT"` | nc host.example.com 20-30
> SSH-1.99-OpenSSH_3.6.1p2
> Protocol mismatch.
> 220 host.example IMS SMTP Receiver Version 0.84 Ready

# 例子
打开一个TCP连接，连接到host.example.com的42端口，使用本地的31337端口，并用设置5秒超时：
```bash
nc -p 31337 -w 5 host.example.com 42
```

打开一个UDP连接，接连到host.example.com的53端口：
```bash
nc -u host.example.com 53
```

打开一个TCP连接，连接到host.example.com的42端口，使用本地的10.1.2.3 IP的接口：
```bash
nc -s 10.1.2.3 host.example.com 42
```

创建和监听UNIX-domain流socket:
```bash
nc -lU /var/tmp/dsocket
```

连接到host.example.com的42端口，通过HTTP代理10.2.3.4, 8080端口：
```bash
nc -x10.2.3.4:8080 -Xconnect host.example.com 42
```

同上一个例子，但是使用"ruser"的用户名：
```bash
nc -x10.2.3.4:8080 -Xconnect -Pruser host.example.com 42
```


