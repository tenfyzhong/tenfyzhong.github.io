---
title: tcpdump手册
categories:
  - man
tags:
  - tcpdump
date: 2017-10-24 18:48:09
keywords: man,tcpdump
---

`tcpdump`dump网络包。

<!-- more -->
# 概要
```bash
tcpdump [ -AbdDefhHIJKlLnNOpqRStuUvxX ] 
        [ -B buffer_size ] [ -c count ]
        [ -C file_size ] [ -G rotate_seconds ] 
        [ -F file ] [ -i interface ] 
        [ -j tstamp_type ] [ -m module ] 
        [ -M secret ] [ -P in|out|inout ]
        [ -r file ] [ -V file ] [ -s snaplen ] 
        [ -T type ] [ -w file ] [ -W filecount ]
        [ -E spi@ipaddr algo:secret,...  ]
        [ -y datalinktype ] [ -z postrotate-command ] 
        [ -Z user ]
        [ expression ]
```


# 描述
`tcpdump`打印网络接口上匹配expression网络包的描述内容。另外它可以使用`-w`参数，
将包数据保存到文件中，以便后期分析，后期可以使用`-r`参数读文件中取包数据。
它还可以使用`-V`参数，让它从多个文件中读取。所有情况下，`tcpdump`只处理匹配expression的包。

如果不使用`-c`参数，它会一直捕捉包，一直到收到`SIGINT`或者`SIGTERM`信号。
如果使用`-c`参数，它会捕捉包到收到`SIGINT`或者`SIGTERM`信号，或者收到指定数量的包。

当`tcpdump`完成捕捉包，它会报告以下的计数：
`captured`包数(`tcpdump`收到和处理的包)。  
`received by filter`包数。  
`dropped by kernel`包数(丢弃的包，由于buffer空间不够引起)。  

对于支持`SIGINFO`信号的平台，比如大多数的BSD(包括mac osx)和Digital/Tru64 UNIX，
它收到`SIGINFO`信号时会报告这些计数，然后继续捕捉包。

从网络设备上读取包需要root权限，从文件上读取不需要。


# 参数
- `-A` 使用ASCII打印每一个包(不打印link level header)。方便捕捉web网页。
- `-b` 使用ASDOT符号打印BGP包的AS数字，而不使用ASPLAIN符号。
- `-B` 设置操作系统的捕捉buffer大小为buffer_size，KB单位。
- `-c` 收到count个包后退出。
- `-C` 写入一个raw包到文件之前，先检查当前文件大小是否已经超过file_size，如果已经超过，  
  则关闭当前的文件，打开一个新的。每个文件包后加一个数字以区分。file_size的单位是1000000bytes。
- `-d` 使用人类可读的方式打印compiled packet-matching code到标准输出，然后退出。
- `-dd` 使用c语言片段的方式打印packet-matching code。
- `-ddd` 使用十进制数字的方式打印packet-matching code。
- `-D` 打印可以用`tcpdump`捕捉的网络接口。对于每一个网络接口，包含一个数字和一个接口名字，
  还可能包括一个文件描述。捕捉的时候可以使用`-i`来指定特定的接口。  
  这对于那些没有命令来显示接口的操作非常有用(例如windows，缺少`ifconfig -a`的unix)。
  数字对于windows 2000及以后的系统非常有用，因为它的网络接口名字非常复杂。  
  `-D`参数不支持`libpcap`缺少`pcap_findalldevs()`函数的系统。
- `-e` 每行打印link-level header。这个可以用来打印mac地址。
- `-E` 对于addr的地址包含spi的Security Parameter Index，使用`spi@ipaddr algo:secret`来解密Ipsec ESP包。  
  多个可以使用逗号或者换行分隔。  
  algo可以是:`des-cbc`, `3des-cbc`, `blowfish-cbc`, `cast128-cbc`, `none`。
  默认是`des-cbc`。解密包需要tcpdump的编译启动cryptography。  
  secret是ASCII形式的ESP密钥key。如果以`0x`开头，则使用十六进制。  
- `-f` 打印`foreign` IPv4地址，而不使用名字符号。  
- `-F` 从file中读取过滤表达式。命令行中的表达式会被忽略。
- `-G` 如果指定，每rotate_seconds秒就滚动`-w`指定的写入文件。每个`-w`指定的文件应该有`strftime`定义的时间格式，
  如果不指定，则新文件会覆盖掉旧文件。  
  如果结合`-c`参数使用，则会使用`file<count>`的格式。
- `-h` 输出帮助信息。
- `-H` 尝试检测802.11s网络头。
- `-i` 监听interface接口。如果没指定，`tcpdump`会搜索系统中编号最少的接口(不包括回环地址)。  
  对于linux 2.2及以后的系统，可以使用`any`来指定捕捉所有的接口。对于promiscuous模式不适用。  
  如果支持`-D`参数，可以使用接口数字来进行指定。
- `-I` 将接口放到monitor mode。这只有部分操作的wifi接口有效。  
  对于monitor mode，网络适配器可能会从网络中分离，所以不能使用这个适配器的无线网络。
  这可以防止网络服务器访问文件，或者解释主机名和地址，在monitor mode下捕捉，
  不会连接到另一个适配器的网络。  
  这个参数会影响`-L`参数的输出。如果`-I`参数没指定，只有链路层不在monitor mode的才会被显示。
  如果指定`-I`指定，只有链路层在monitor mode的才会被显示。
- `-j` 设置捕捉的时间戳类型为tstamp_type。支持的类型在`pcap-tstamp-type(7)`的手册里。
  并不是所有的类型对任意的接口都支持。
- `-J` 列出接口支持的时间戳类型。如果接口不支持设置时间戳类型，则不会显示。
- `-K` 不要尝试效验IP, TCP, UDP的效验和。这对于硬件上计算效验和非常有用。否则，
  所有的流出tcp效验和都会被标记成错误的。
- `-l` 使标准输出为行buffered。对于查看数据非常有用。比如：`tcpdump -l | tee dat`。  
  注意，在windows下，行buffered意味着没有buffer，所以WinDump会每个字符的打印，如果指定了`-l`。  
  `-U`的行为类似于`-l`，但是它是包buffered的。所以收完每个名后进行打印。
- `-L` 列出接口中知道的data link types，然后退出。data link types基于不同的模式，
  例如在一些平台下，wifi接口在非monitor mode下可能支持一组data link types，
  在monitor mode下支持另外一组data link types。
- `-m` 从module文件加加载SMI MIB模块的定义。这个参数可以多次使用来加载多个MIB模块。
- `-M` 使用secret做为一个共享的密钥来效验tcp段的数字。
- `-n` 不要转换地址到名字。
- `-N` 不要显示域名。例如显示`nic`，而不是`nic.ddn.mil`。
- `-O` 不要支持packet-matching code优化器。
- `-p` 不要把接口放到promiscuous mode。
- `-P` 指定发送/接收方向来捕捉包。支持的值为`in`, `out`, `inout`。不是所有的平台都支持。
- `-q` 安静模式输出，打印更少的协议信息。
- `-R` 假定ESP/AH包基本旧的规范(RFC1825到RFC1829)。如果指定这个参数，`tcpdump`不打印预防重播域。
  因为ESP/AH规范没有协议版本字段，`tcpdump`不能推导出ESP/AH的协议版本。
- `-r` 从file中读取包(使用`-w`参数创建的)。如果file是`-`，则从标准输入中读取。
- `-S` 使用绝对TCP sequence number替换相对TCP sequence number。
- `-s` 指定每个捕捉包的包长，默认值是65535bytes。snap为0设置为默认值65535，向后兼容老版本的`tcpdump`。
- `-T` 强制expression使用指定的type进行解释。当前支持的类型: `aodv` (Ad-hoc On-demand Distance Vector protocol),
  `cnfp` (Cisco NetFlow protocol), `lmp` (Link Management Protocol), `pgm`(Pragmatic General Multicast),
  `pgm_zmtp1` (ZMTP/1.0 inside PGM/EPGM), `radius` (RADIUS), `rpc` (Remote Procedure Call), 
  `rtp` (Real-Time Applications protocol), `rtcp` (Real-Time Applications control protocol), 
  `snmp` (Simple Network Management Protocol), `tftp` (Trivial File Transfer Protocol),
  `vat` (Visual Audio Tool), `wb` (distributed White Board), `zmtp1` (ZeroMQ Message Transport Protocol 1.0),
  `vxlan` (Virtual eXtensible Local Area NetworkA)。  
- `-t` 不要对每一行都打印时间戳。
- `-tt` 对每一行打印非格式化的时间戳。
- `-ttt` 打印当前行与上一行的时间差。
- `-tttt` 打印格式化的时间。
- `-ttttt` 打印当前行与第一行的时间差。
- `-u` 打印没解码的NFS处理。
- `-U` 如果没指定`-w`参数，使用包缓存。
- `-v` 解析和打印的时候，提供更多的信息。例如：连接时间，标识，总长度，IP参数等。
- `-vv` 输出更多信息。比如添加NFS回复包。
- `-vvv` 输出更多信息。
- `-V` 从file中读取一个文件名列表。如果file为`-`，则从标准输入中读取。
- `-w` 把raw信息写入到file文件，而不是进行输出。后续可以使用`-r`来读取。如果file为`-`，则写到标准输出。  
  输出会被缓存，所以从文件中读可能会读不到内容，使用`-U`参数来强制使用包缓存。  
  写到文件的MIME类型为`application/vnd.tcpdump.pcap`。建议使用`.pcap`做文件后缀。  
- `-W` 结合`-C`一起使用。这个参数限制文件个数。超过会rotating进行覆盖写。另外，
  它可以增加文件名增加足够的开头0。  
  结合`-G`一起使用，会限制文件的个数，当达到上限时会退出，退出码为0。
- `-x` 解析和打印的时候，额外打印每个包的头，以十六进制打印内存(不打印链路层的头)。
  最小的snaplen bytes会被打印。
- `-xx` 解析和打印的时候，以十六进制额外打印每个包的头和内容，包括链路层的头。
- `-X` 解析和打印的时候，以十六进制和ASCII打印每个包的头和内容，不打印链路层头。
- `-XX` 解析和打印的时候，以十六进制和ASCII打印每个包的头和内容，包括链路层头。
- `-y` 捕捉包时设置使用的数据链路类型。
- `-z` 结合`-C`和`-G`一起使用，它使`tcpdump`以`command file`的格式运行，file是保存
  rotation关闭后的文件。例如：使用`-z gzip`或者`-z bizp2`会使用gzip或者bzip2压缩
  每一个保存的文件。  
  `tcpdump`会并行运行命令来捕捉，使用最低的优先级别以不打断捕捉包。  
- `-Z` 如果以root运行`tcpdump`，切换到指定的用户。

- `expression` 选择需要打印的包。如果没有expression，则所有的包都会被打印。否则，
  只有expression为true的包才会被打印。  
  对于expression的请求，查看`pcap-filter(7)`。  
  expression的参数可以是单个shell参数，也可以是多个shell参数。一般expression包括shell元字符，
  例如反斜杠来转换协议名，可以通过单引号包住以免shell进行转换。多个参数会以空格连接起来。


# 例子
打印所有到达或者离开sundown主机的包：
```bash
tcpdump host sundown
```

打印holios与hot或者ace通信的包：
```bash
tcpdump host helios and \( hot or ace \)
```

打印除了helios的所有与ace通信的ip包：
```bash
tcpdump ip host ace and not helios
```

打印所有本与秘Berkeley主机的包：
```bash
tcpdump net ucb-ether
```

打印所有经过snup的ftp通信包，使用单括号包住以免括号被shell解释：
```bash
tcpdump 'gateway snup and (port ftp or ftp-data)'
```

打印所在不是本机发出，也不到达本机的包
```bash
tcpdump ip and not net localnet
```

打印非本机的开始和结束包(SYN和FIN包)：
```bash
tcpdump 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0 and not src and dst net localnet'
```

打印所有通过80端口的IPv4 HTTP包，也就是说只打印数据包，不打印SYN、FIN、ACK-only包。
```bash
tcpdump 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'
```

打印所以发送经过snup大于576 bytes的包：
```bash
tcpdump 'gateway snup and ip[2:2] > 576'
```

打印IP广播或者多播包，并且不经过Ethernet广播或者多播：
```bash
tcpdump 'ether[0] & 1 = 0 and ip[16] >= 224'
```

打印所有的非echo请求响应ICMP包，也就是说非ping包：
```bash
tcpdump 'icmp[icmptype] != icmp-echo and icmp[icmptype] != icmp-echoreply'
```


# 输出格式
tcpdump的输出是基于协议的。以下给出了大多数的格式描述和例子。

## Link Level Headers
如果指定`-e`参数，链路层的头会被打印。在以太网上，源和目标的地址、协议、包长度会被打印。

在FDDI网络上，`-e`参数会导致`tcpdump`打印`frame control`域，源和目标的地址和包长度。
`frame control`域管理后续包的解释。正常的包(例如包括IP数据报)是`async`包，优先级别在0到7之间，
例如`async4`。这些包假设包括802.2 Logical Link control(LLC)包，LLC头会被打印，如果它不是一个ISO包或者SNAP包。

在令牌环形网络上，`-e`参数打印`access contrl`和`frame control`域，源和目标的地址和包长度。
就像在FDDI网络，包假设包含LLC包。基于`-e`参数是否指定，源路由信息会打印在源路由包上。

在802.11网络上，`-e`选项打印`frame control`域。所有在802.11头上的地址，包长。
就像FDDI网络，包假设包含LLC包。

在SLIP链路上，方向标识(`I`表示入包，`O`表示出包)，包类型，压缩信息会被打印。
包类型会优先打印，类型括号`ip`, `utcp`和`ctcp`。没有进一步的连接信息能被打印了。
对于TCP包，连接标识符会接着类型打印。如果包是压缩的，它的编码头会被打印。
一个特殊的案例打印成`*S+n`和`*SA+n`，n是sequence num变化的量(或者sequence num和ack)。
如果不是特殊的案例，0或者更多的变化会被打印。一个变化由U(urgent pointer), 
W(window), A(ack), S(secuence num), I(packet ID)标识，接着一个差值(+n或者-n)，
或者一个新值(=n)。最后，所有的数据和压缩包头长度会被打印。

例如，下面一行出包压缩的TCP包，包含一个隐藏的标识符，ack的变化为6，sequence number是49，
packet ID为6，包括3字节的内容和6字节的压缩头。
```
0 ctcp * A+6 S+49 I+6 3 (6)
```

## ARP/RARP Packets
Arp/rarp输出请求类型和它的参数。这里有一个在rtsg上使用`rlogin`请求到csam的例子：
```
arp who-has csam tell rtsg
arp reply csam is-at CSAM
```
第一行是rtsg发送arp包到互联网地址上询问谁有csam的址。csam回复了它的互联网地址。

下面是使用`-n`打印ip的过程，`tcpdump -n`:
```
arp who-has 128.3.254.6 tell 128.3.254.68
arp reply 128.3.254.6 is-at 02:07:01:00:01:c4
```

如果使用`-e`参数，`tcpdump -e`:
```
RTSG Boardcast 0806 64: arp who-has csam tell rtsg
CSAM RTSG 0806 64: arp reply csam is-at CSAM
```

## TCP Packets
tcp协议行的基本格式如下：
```
src > dst: flags data-seqno ack window urgent options
```
src和dst是源和目标的ip地址和端口。flags是以下的组合`S`(SYN), `F`(FIN), `P`(PUSH), 
`R`(RST), `U`(URG), `W`(ECN CWR), `E`(ECHO-Echo), `.`(ACK)，或者空表示没有flags。
data-seqno描述了这个包中包含数据哪部分数据。ack是另一个方向的下一个期望数据的seqno。
window是窗口大小，表示另一方的接收buffer空间大小。urg指示这个包的数据是urgent的。
options是tcp参数(例如：`<mss 1024>`)。

src, dst, flags会一直出现。其他的域基于包中的tcp协议头适当出现。

以下是一个从rtsg rlogin到csam的一部分数据：
```
rtsg.1023 > csam.login: S 768512:768512(0) win 4096 <mss 1024>
csam.login > rtsg.1023: S 947648:947648(0) ack 768513 win 4096 <mss 1024>
rtsg.1023 > csam.login: . ack 1 win 4096
rtsg.1023 > csam.login: P 1:2(1) ack 1 win 4096
csam.login > rtsg.1023: . ack 2 win 4096
rtsg.1023 > csam.login: P 2:21(19) ack 1 win 4096
csam.login > rtsg.1023: P 1:2(1) ack 21 win 4077
csam.login > rtsg.1023: P 2:3(1) ack 21 win 4077 urg 1
csam.login > rtsg.1023: P 3:4(1) ack 21 win 4077 urg 1
```
第一行表示rtsg的1023端口发送一个包到csam和login端口。`S`表示设置了SYN。这个包的seqno是768512，
不包含数据(`first:last(nbytes)`符号表示seqno从first到last，不包含last，包含nbytes的数据)。
不包含ack标识，窗口大小为4096字节，max-segment-size参数为1024字节。

casm回复了一个类似的包给rtsg，同时包含了ack标识。然后rtsg ack了csam的syn包，
`.`表示设置了ack，这个包不包含数据，所以没有seqno。注意，这里的seqno是一个小数(1)。
第一次会话的时候，它会打印seqno，然后在以后的会话中，则使用与第一次会话的相对seqno。
`-S`可以指定为强制所有的会话都使用原始的seqno。

在第6行，rtsg发送了19字节的数据(第2字节到第20字节)。这个包设置了PUSH标识。
在第7行，csam回复表示已经收到rtsg到21字节(不包含)的数据。csam同时发送了1字节的数据到rtsg。
在第8、9行，csam发送了2字节的urgent数据到rtsg。

如果快照足够小的，那么`tcpdump`不能捕捉一个完整的tcp包头，它尽可能多的解释头，
然后报告一个`[|tcp]`来指示剩下的数据不能够被解释。如果头中包含一个伪参数(有一个长度要么太小，要么超出了头的末端)，
`tcpdump`会报告`[bad opt]`，然后不再解释接正愁的参数，因为它不知道从哪里开始了。
如果指定了头的长度，但是IP数据报的长度不够，`tcpdump`会报告`[bad hdr length]`。

## 使用特定的标识来捕捉tcp包
tcp头中包含8位的控制位。
```
CWR|ECE|URG|ACK|PSH|RST|SYN|FIN
```

假设我们需要观察TCP的连接建议过程。回忆一下tcp的3次握手过程，连接过程中包含的标识如下：
1. 客户端发送SYN
1. 服务器响应SYN和ACK
1. 客户端响应ACK

现在我们只想捕捉只设置了SYN的包(第1步)。我们需要一个正确的expression。

回忆一下不包含参数的tcp包头：
```
 0                            15                              31
-----------------------------------------------------------------
|          source port          |       destination port        |
-----------------------------------------------------------------
|                        sequence number                        |
-----------------------------------------------------------------
|                     acknowledgment number                     |
-----------------------------------------------------------------
|  HL   | rsvd  |C|E|U|A|P|R|S|F|        window size            |
-----------------------------------------------------------------
|         TCP checksum          |       urgent pointer          |
-----------------------------------------------------------------
```

tcp头一般包含20字节的数据，除非包含了tcp参数。图中的第一包包含了0~3字节，第二行包含了4~7字节。

TCP控制位在第13字节：
```
 0             7|             15|             23|             31
----------------|---------------|---------------|----------------
|  HL   | rsvd  |C|E|U|A|P|R|S|F|        window size            |
----------------|---------------|---------------|----------------
|               |  13th octet   |               |               |
```

我们直接看第13字节：
```
                |               |
                |---------------|
                |C|E|U|A|P|R|S|F|
                |---------------|
                |7   5   3     0|

```
从右到左标上位置0到7。

回忆一下我们需要只设SYN位的包。tcp头的第13字节如下：
```
                |C|E|U|A|P|R|S|F|
                |---------------|
                |0 0 0 0 0 0 1 0|
                |---------------|
                |7 6 5 4 3 2 1 0|
```
我们需要SYN位设为1。

第13字节的位在网络序中的二进制数为：
```
00000010
```
它对应的十进制值为2。

因为我们只要SYN设置了的包，在tcp头中的第13字节的值在网络序中为2。可以写成以下的表达式：
```
tcp[13] == 2
```

我们把这个表达式添加到`tcpdump`的过滤条件中：
```bash
tcpdump -i xl0 tcp[13] == 2
```

假设我们需要捕捉SYN包，但是不关心是否有ACK或者其他位被置上。我们先看一下同时有SYN-ACK位的第13字节：
```
|C|E|U|A|P|R|S|F|
|---------------|
|0 0 0 1 0 0 1 0|
|---------------|
|7 6 5 4 3 2 1 0|
```
第1跟第4位被置上，其二进制的值为
```
00010010
```
对应的十进制为18。

我们不能简单的使用`tcp[13] == 18`来进行过滤。因为我们要的不是只匹配SYN-ACK包，
而是设了SYN的包，而不关心其他位。

我们需要使用位与操作，来保留出SYN位是否为1，我们把需要的位与第13字节与，再判断是否存在SYN位：
```
     00010010 SYN-ACK              00000010 SYN
AND  00000010 (we want SYN)   AND  00000010 (we want SYN)
     --------                      --------
=    00000010                 =    00000010

```
因此对应的表达式为：
```
tcp[13] & 2 == 2
```

对应的`tcpdump`命令为：
```bash
tcpdump -i xl0 'tcp[13] & 2 == 2'
```

一些位移和域可以使用名字替换数字位，例如`tcp[13]`可以使用`tcp[tcpflags]`替换。
以下的tcp域值可以使用： `tcp-fin`, `tcp-syn`, `tcp-rst`, `tcp-push`, `tcp-act`, `tcp-urg`。

例如：
```bash
tcpdump -i xl0 'tcp[tcpflags] & tcp-push != 0'
```
注意要使用单引号防止`&`被shell解释。

## UDP包
udp包格式如下：
```
actinide.who > broadcast.who: udp 84
```
主机actinide的who端口给广播的who端口发送84字节的用户数据。

一些UDP服务名可以被识别而打印更高级别的协议信息。

## UDP域名服务请求
域名服务器请求格式如下：
```
src > dst: id op? flag qtype qclass name (len)
h2opolo.1538 > helios.domain: 3+ A? ucbvax.berkeley.edu. (37)
```
主机h2opolo请求helios的domain服务，要求返回一个(qtype=A)的ucbvax.berkeley.edu的地址。
查询id是3，`+`表示递归查询。请求长度为37，不包括UDP包头和IP包头。查询操作是标准的`Query`，
所以op域被忽略了。否则会在3和`+`之前插入op。类似的qclass也是标准的的`C_IN`，所以被忽略了，
其他的会打印在A之后。

一些小异常是结果存在额外的域附加在中括号里：如果一个查询包含一个答案，鉴权记录或者附加章节，
ancount, nscount, arcount会打印成`[na]`, `[nn]`, `[nau]`，n是个数。如果一些响应位被置上
(AA, RA, rcode)或者其他必需是0的位被置上，会打印`[b2&3=x]`，`x`是一个16进制数。

## UDP域名服务响应
域名服务器响应格式如下：
```
src >dst: id op rcode flags a/n/au type class data (len)
helios.domain > h2opolo.1538: 3 3/3/7 A 128.32.137.3 (273)
helios.domain > h2opolo.1537: 2 NXDomain* 0/1/0 (97)
```
在第一个例子中，helios响应h2opolo查询id为3的请求，包含3个答案记录，3个域名服务记录，
7个附加记录。第一个答案记录是A类型地址，它的值为128.32.137.3。整个响应包的大小为273字节，
不包括UDP包头和IP包头。op(Query)和响应码(NoError)被忽略了。

在第二个例子中，helios响应h2opolo查询 id为2的请求，返回一个non-existent domain(NXDomain)的响应码，
而没有答案，一个域名服务，没有授权记录。`*`表示授权答案被置上。

另外可能出现的字符有`-`(recursion avaliable，RA, not set), `|`(truncated message, TC, set)。
如果问题节不包含一个，则`[nq]`会被打印。

## SMB/CIFS decoding
`tcpdump`当前包含SMB/CIFS/NBT解码在UDP/137, UDP/138, TCP/139。一些原始的IPX和NetBEUI SMB数据解码也支持。

默认使用一个最小的解码，可以`-v`可以得到更多详细的解码信息。注意，`-v`会使一个单个的SMB包显示一页或者更多，
所以确保在需要更多信息的时候才使用`-v`。

可以SMB包的格式和种个域的意思可以查看www.cifs.org。

## NFS请求和响应
Sun NFS(Network File System)请求响应打印如下：
```
src.xid > dst.nfs: len op args
src.nfs > dst.xid: reply stat len op results
sushi.6709 > wrl.nfs: 112 readlink fh 21,24/10.73165
wrl.nfs > sushi.6709: reply ok 40 readlink "../var"
sushi.201b > wrl.nfs:
   144 lookup fh 9,74/4096.6878 "xcolors"
wrl.nfs > sushi.201b:
   reply ok 128 lookup fh 9,74/4134.3150
```
在第一行，主机sushi发送一个id为6709的事务到主机wrl(源主机后面的数字是事务id而不是端口)。
请求包大小为112 bytes，不包括udp头和ip头。这个操作是执行`readlink`操作，操作文件操作符(fh) `21,24/10.73165119`
(如果够幸运，就像这个例子，文件操作符可以解释成一个最大，最小设备数字对，跟着一个inode数字和生成数字)。
wrl回复了ok，内容为链接。

在第三行，sushi咨询`lookup`文件`9,74/4096.6878`的`xcolors`。打印内容是基于操作类型的。
输出格式会意图自我说明的，如果结合NFS协议规范使用。

如果指定`-v`参数，额外的信息会被打印，例如：
```
sushi.1372a > wrl.nfs:
   148 read fh 21,11/12.195 8192 bytes @ 24576
wrl.nfs > sushi.1372a:
   reply ok 1472 read REG 100664 ids 417/0 sz 29388
```
(`-v`同时也会打印IP头的TTL, ID, length, fragmentation fields，这个例子中忽略了)。
在第一行，sushi请求wrl读取文件`21,11/12.195`24576位置的8192字节数据。wrl回复ok，
第二行显示的包是第一个包的回复，因此长度是1472字节(另外的字节会接着后续的包片段，
但是这些片段不包含NFS和UDP头，所以可能不会被打印，基于过滤规则)。因为指定了`-v`，
一些文件属性会被打印：文件类型(`REG`，常规文件)，文件权限位(8进制)，uid, gid, 文件大小。

如果`-v`参数多次指定，更多的信息会被打印。

NFS回复包不会显式的识别RPC操作。tcpdump保持跟踪`recent`操作和通过事件id匹配它们的回复。
如果一个回复不匹配紧跟着的请求，它可以不会被解释。

## AFS请求和响应
AFS(Andrew File System)请求响应打印如下：
```
src.sport > dst.dport: rx packet-type
src.sport > dst.dport: rx packet-type service call call-name args
src.sport > dst.dport: rx packet-type service reply call-name args
elvis.7001 > pike.afsfs:
   rx data fs call rename old fid 536876964/1/1 ".newsrc.new"
   new fid 536876964/1/1 ".newsrc"
pike.afsfs > elvis.7001: rx data fs reply rename
```
在第一行，主机elvis发送一个RX包给pike。这是一个RX数据包，发送到fs(fileserver)服务，
它开始于一个RPC调用。RPC的名字为rename，包含一个旧的目录文件id`536876964/1/1`和一个旧文件名`.newsrc.new`，
新目录文件id`536876964/1/1`和新文件名为`.newsrc`。主机pike响应一个rename请求的RPC回复。

在一般情况下，所有的AFS RPC都会被解包成RPC调用名字。大多的AFS RPC参数会被解释。

格式是自我描述的。

如果`-v`给定两次，确认包和头文件会被打印，例如RX调用ID，调用号码，sequence number，
serial number，RX包的flag。

如果`-v`给定两次，额外的信息会被打印，例如RX调用ID，serial number，RX包的flag。
RX的ack包同时打印MTU信息。

如果`-v`给定三次，安全索引和服务器id会被打印。

abort包会打印错误代码。

AFS回复包不会显式的识别RPC操作。tcpdump保持跟踪`recent`操作和通过事件id匹配它们的回复。
如果一个回复不匹配紧跟着的请求，它可以不会被解释。

## KIP AppleTalk (DDP in UDP)
封装成UDP的AppleTalk DDP包会解释成DDP包来打印(也就是说所有的UDP包头信息都会被丢弃)。
文件`/etc/atalk.names`会翻译AppleTalk网络和节点编号。文件格式如下：
```
number    name

1.254          ether
16.1      icsd-net
1.254.110 ace
```
头两个给了AppleTalk网络的名字。第三行给了一个特定主机的名字(主机与网络的区分通过第三个8进制数，
一个网络必须包含两个8进制数，一个主机必须包含三个8进制数)。数字和名字必须以空格隔开。
`/etc/atalk.names`可以包含空行和注释(以`#`开头的行)。

AppleTalk地址打印如下：
```
net.host.port

144.1.209.2 > icsd-net.112.220
office.2 > icsd-net.112.220
jssmag.149.235 > icsd-net.2
```
(如果不存在`/etc/atalk.names`文件，或者不包含AppleTalk主机/网络的数字，地址会打印成数字格式)。
在第一个例子中，NBP(DDP port 2)在网络144.1，节点209上发送到任意监听220端口的icsd网络112节点。
第二行是一样的，除了源结点的名字被识别为office。第三行jssmag结点149节点的235端口发送一个广播到icsd-net NBP端口。

NBP(name binding protocol)和ATP(AppleTalk transaction protocol)包有它们的内容解释器。
其他协议只是打印协议名(或者数字，如果没有注册到协议名)和包大小。

NBP包打印格式如下：
```
icsd-net.112.220 > jssmag.2: nbp-lkup 190: "=:LaserWriter@*"
jssmag.209.2 > icsd-net.112.220: nbp-reply 190: "RM1140:LaserWriter@*" 250
techpit.2 > icsd-net.112.220: nbp-reply 190: "techpit:LaserWriter@*" 186
```

## IP片段
IP片段打印如下：
```
(frag id:size@offset+)
(frag id:size@offset)
```
第一种格式说明有更多的的数据片段。第二种说明是最后一个数据片段。

`id`是片段id。`size`是片段(字节单位)，不包含IP着。`offset`是片段在原始数据报的位移。

每个片段都会打印片段信息。第一个片段包含高层协议头和frag信息，在协议信息之后。
第一个片段之后不再包含高层协议头，frag信息打印在源和目标地址之后。例如，
这里是从arizona.edu到lbl-rtsg.arpa的ftp包片段：
```
arizona.ftp-data > rtsg.1170: . 1024:1332(308) ack 1 win 4096 (frag 595a:328@0+)
arizona > rtsg: (frag 595a:204@328)
rtsg.1170 > arizona.ftp-data: . ack 1536 win 2560
```
这里有以下的信息需要注意：第一，第二行的地址不包含端口号。因为tcp协议信息都在第一个片段。
第二，第一行的tcd sequence信息打印了308字节的用户数据，实际上是512字节(第一个片段包含308字节，
第二个片段包含204字节)。

