---
title: pcap-filter手册
categories:
  - man
tags:
  - pcap-filter
  - tcpdump
date: 2017-10-25 18:37:48
keywords: man,pcap-filter,tcpdump
toc: false
---

网络包过滤语法。`tcpdump`的expression。

<!-- more -->
# 描述
`pcap_compile()`是用来编译一个字符串到过滤程序的函数。这导致过滤程序可以决定哪些包可以提供给`pcap_loop()`, 
`pcap_dispatch()`, `pcap_next()`, `pcap_next_ex()`。

过滤表达式由一个或者更多的原语组成。原语由一个id(名字或者编号)组成，id可以有一个或者多个修饰符。
一共有三种不同的修饰符：
- **类型** 修饰符表示id是什么类型的。可能的类型有`host`, `net`, `port`, `portrange`。
  例如，`host foo`, `net 128.3`, `port 20`, `portrange 6000-6008`。如果没有类型修饰符，
  则假设是`host`。
- **方向** 修饰符指定了流的方向是到达id或者从id出发。可能的方向有`src`, `dst`, 
  `src or dst`, `src and dst`, `ra`, `ta`, `addr1`, `addr2`, `addr3`, `addr4`。
  例如，`src foo`, `dst net 128.3`, `src or dst port ftp-data`。如果没有方向修饰符，
  则假设是`src or dst`。`ra`, `ta`, `addr1`, `addr2`, `addr3`, `addr4`修饰符符只有对IEEE 802.11
  Wireless LAN link layers有效。对于一些链路层，例如SLIP和`cooked`使用`any`捕捉任意设备或者其他的设备类型，
  `inbound`和`outbound`修饰符可以指定希望的方向。
- **协议** 修饰符限定了匹配的特殊协议。可能的协议有：`ether`, `fddi`, `tr`, `wlan`, 
  `ip`, `ip6`, `arp`, `rarp`, `decnet`, `tcp`, `udp`。例如，`ether src foo`, `arp net 128.3`, 
  `tcp port 21`, `udp portrange 7000-7009`, `wlan addr2 0:2:3:4:5:6`。如果没有指定协议修饰符，
  则使用所有合法的组合。例如，`src foo`意味着`(ip or arp or rarp) src foo`，
  `net bar`意味着`(ip or arp or rarp) net bar`，`port 53`意味着`(tcp or udp) port 53`。

[`fddi`实际上是`ether`的别名。解析器相同的对待它们。FDDI头包含Ethernet-like源和目标地址，
经常也包含Ethernet-like包类型。所以你可以使用类型于Ethernet的域来过滤FDDI域。
FDDH头还包含其他的头，但是你不能明确地在过滤表达式中指定。

类似的，`tr`和`wlan`是`ether`的别名。上一节关于FDDI头的说明同样可以用于令牌环形网络和802.11 wireless LAN头。
对于802.11头，目标地址在DA域，源地址在SA域。]

除了上述之外，还有一些原始的关键字不使用以上的模式：`gateway`, `broadcast`, `less`, 
`greater`和一些算法表达式。这些都在下面描述。

更多复杂的过滤表达式使用`and`, `or`, `not`来组合原语。例如，`host foo and not port ftp and not port ftp-data`。
相同的修饰符可以忽略。例如，`tcp dst port ftp or ftp-data or domain`与
`tcp dst port ftp or tcp dst port ftp-data or tcp dst port domain`是完全一样的。

## 合法的原语
### `dst host <host>`
如果包的IPv4/v6目标域是`<host>`，可能是地址或者名字，则为true。

### `src host <host>`
如果包的IPv4/v6源域是`<host>`则为true。

### `host <host>`
如果包的IPv4/v6的源或者目标是`<host>`则为true。

以上任意的主机表达式可以在前面加上`ip`, `arp`, `rarp`, `ip6`的关键字。例如：
```
ip host <host>
```
等同于
```
ether proto \ip and host <host>
```
如果`<host>`包含多个IP地址，每个地址都会检查匹配。

### `ether dst <ehost>`
如果Ethernet目标地址是`<ehost>`则为true。`<ehost>`可以是`/etc/ethers`里的一个名字或者数字。

### `ether src <ehost>`
如果Ethernet源地址是`<ehost>`则为true。

### `ether host <ehost>`
如果Ethernet源地址或者目标是址是`<ehost>`则为true。

### `gateway <host>`
如果包使用`<host>`作为一个网关则为true。例如，Ethernet的源或者目标地址是`<host>`，
但是IP源和目标都不是`<host>`。`<host>`必须是一个名字，必须同时可以被机器的
host-name-to-IP-address解析机制(host name file, DNS, NIS等)和
host-name-to-Ethernet-address解析机制(`/etc/ethers`等)解释。一个等价的表达式是：
```
ether host <ehost> and not host <host>
```
这个语法在启动IPv6的机器上不能工作。

### `dst net <net>`
如果包中IPv4/v6的目标地址的网络号是`<net>`则为true。`<net>`可能是一个名字(`/etc/networks`等)，
或者一个网络号。一个IPv4的网络号可以写成四段点分制(例如`192.168.1.0`)，三段点分制(例如`192.168.1`)，
两段点分制(例如`172.16`)或者一个单独的数字(例如`10`)。四段点分制的掩码为`255.255.255.255`
(意味着是一个主机地址)，三段点分制的掩码为`255.255.255.0`，二段点分制的掩码为`255.255.0.0`，
单独数字的掩码为`255.0.0.0`。一个IPv6的网络号必须完整写出，掩码为`ff:ff:ff:ff:ff:ff:ff:ff`，
所以IPv6的网络匹配真实的主机，一个网络匹配需要一个网络掩码长度。

### `src net <net>`
如果包中IPv4/v6的源地址的网络号是`<net>`则为true。

### `net <net>`
如果包中的源或者目标地址的网络号是`<net>`则为true。

### `net <net> mask <netmask>`
如果IPv4地址使用`<netmask>`的掩码匹配`<net>`网络号则为true。可以使用`src`和`dst`修饰符。
这个请求对IPv6无效。

### `net <net>/<len>`
如果IPv4/v6使用`<len>`宽度的掩码匹配`<net>`网络号则为true。可以使用`src`和`dst`修饰符。

### `dst port <port>`
如果包是`ip/tcp`, `ip/udp`, `ip6/tcp`, `ip6/udp`并且目标端口为`<port>`则为true。
`<port>`可以是一个数字或者`/etc/services`中定义的名字。如果使用名字，则端口名和协议都会被检查。
如果使用数字或者模糊的名字，则只检查端口(例如，`dst port 513`会打印tcp/login和udp/who的通信，
`port domain`会打印tcp/domain和udp/domain的通信)。

### `src port <port>`
如果包的源端口为`<port>`则为true。

### `port <port>`
如果包的源端口或者目标端口为`<port>`则为true。

### `dst portrange <port1>-<port2>`
如果包是`ip/tcp`, `ip/udp`, `ip6/tcp`, `ip6/udp`并且目标端口在`<port1>`和`<port2>`之间则为true。

### `src portrange <port1>-<port2>`
如果包的源端口在`<port1>`和`<port2>`之间则为true。

### `portrange <port1>-<port2>`
如果源端口或者目标端口在`<port1>`和`<port2>`之间则为true。

任意以上的端口或者范围端口表达式前都可以跟`tcp`, `udp`关键字，例如：
```
tcp src port <port>
```
只匹配tcp的`<port>`端口的包。

### `less <length>`
如果包长度小于等于`<length>`则为true。等价于：
```
len <= <length>
```

### `greater <length>`
如果包长度大于等于`<length>`则为true。等价于：
```
len >= <length>
```

### `ip proto <protocol>`
如果是`<protocol>`协议的IPv4包则为true。`<protocol>`可以是一个数字或者以下的名字
`icmp`, `icmp6`, `igmp`, `igrp`, `pim`, `ah`, `esp`, `vrrp`, `udp`, `tcp`。
注意`tcp`, `udp`, `icmp`也是关键字，所以需要使用反斜杠转义。

### `ip6 proto <protocol>`
如果是`<protocol>`协议的IPv6包则为true。

### `proto <protocol>`
如果是`<protocol>`协议的IPv4/v6包则为true。

### `tcp, udp, icmp`
`proto <protocol>`的缩写。

### `ip6 protochain <protocol>`
如果是IPv6的包，并且协议头包含`<protocol>`在它的协议头链中，则为true。例如：
```
ip6 protochain 6
```
匹配任意IPv6包含有TCP协议头在协议头链中。这个包可能包含，例如，鉴权头，路由头，
hop-by-hop选项头等。

### `ip protochain <protocol>`
等价于`ip6 protochain <protocol>`，但是是IPv4。

### `protochain <protocol>`
等价于`ip protochain <protocol> or ip6 protochain <protocol>`。

### `ether broadcast`
如果是Ethernet广播包则为true。`ether`关键字是可选的。

### `ip broadcast`
如果是一个IPv4广播包则为true。它检查所有0和所有1的广播会话，也查询子网掩码。

### `ether multicast`
如果是一个Ethernet广播包则为true。`ether`关键字是可选的。这是`ehter[0] & 1 != 0`的简写。

### `ip multicast`
如果是一个IPv4广播包则为true。

### `ip6 multicast`
如果是一个IPv6广播包则为true。

### `ether proto <protocol>`
如果包是ether的`<protocol>`协议则为true。`<protocol>`可以是一个数字或者
`ip`, `ip6`, `arp`, `rarp`, `atalk`, `aarp`, `decnet`, `sca`, `lat`, `mopdl`, 
`moprc`, `iso`, `stp`, `ipx`, `netbeui`。这些修饰符都是关键闻，需要使用反斜杠转义。

### `ip`, `ip6`, `arp`, `rarp`, `atalk`, `aarp`, `decnet`, `iso`, `stp`, `ipx`, `netbeui`
```
ether proto <protocol>
```
的缩写。`<protocol>`是以上的一个值。

### `lat`, `moprc`, `mopdl`
```
ether proto <protocol>
```
的缩写。`<protocol>`是以上的一个值。并不是所有使用pcap的程序都能解析这些协议。

### `decnet src <host>`
如果DECNET源地址是`<host>`则为true。`<host>`可能是一个`10.123`类型的址或者一个DECNET主机名。

### `decnet dst <host>`
如果DECNET的目标地址是`<host>`则为true。

### `decnet host <host>`
如果DECNET的源或者目标地址是`<host>`则为true。

### `ifname <interface>`
如果是通过指定的接口进来的包则为true。

### `on <interface>`
与`ifname`同义。

### `rnr <num>`
如果包匹配PF rule number则为true。

### `rulenum <num>`
与`rnr`同义。

### `reason <code>`
如果包匹配PF reason code则为true。已知的code有: `match`, `badoffset`, `fragment`, 
`short`, `normalize`, `memory`。

### `rset <name>`
如果包匹配PF ruleset name则为true。

### `ruleset <name>`
与`rset`同义。

### `srnr <num>`
如果包匹配PF rule number则为true。

### `subrulenum <num>`
与`srnr`同义。

### `action <act>`
如果PF使用一个特殊的action则为true。已经的action: `pass`, `block`, `nat`, `rdr`, `binat`, `scrub`。

### `wlan ra <ehost>`
如果IEEE 802.11 RA是`<ehost>`则为true。RA域会在所有的帧中使用，除了管理帧。

### `wlan ta <ehost>`
如果IEEE 802.11 TA是`<ehost>`则为true。TA域会在所有的帧中使用，除了管理贴、CTS(Clear To Send)和
ACK控制帧。

### `wlan addr1 <ehost>`
如果第一个IEEE 802.11地址是`<ehost>`则为true。

### `wlan addr2 <ehost>`
如果第二个IEEE 802.11地址(如果存在)是`<ehost>`则为true。第二个地址域会有所有的帧中使用，
除了CTS(Clear To Send)和ACK控制帧。

### `wlan addr3 <ehost>`
如果第三个IEEE 802.11地址(如果存在)是`<ehost>`则为true。第三个地址域会在管理帧和数据帧中使用，
控制帧中没有。

### `wlan addr4 <ehost>`
如果第四个IEEE 802.11地址(如果存在)是`<ehost>`则为true。第四个地址域只有WDS(Wireless Distribution System)帧使用。

### `type <wlan_type>`
如果IEEE 802.11帧类型匹配`<wlan_type>`则为true。合法的`<wlan_type>`有：`mgt`, `ctl`, `data`。

### `type <wlan_type> subtype <wlan_subtype>`

如果IEEE 802.11帧类型匹配`<wlan_type>`并且帧子类型匹匹配`<wlan_subtype>`则为true。

如果`<wlan_type>`是`mgt`，则可用的`<wlan_subtype>`有：`assoc-req`, `assoc-resp`, 
`reassoc-req`, `reassoc-resp`, `probe-req`, `probe-resp`, `beacon`, `atim`, 
`dissassoc`, `auth`, `deauth`。

如果`<wlan_type>`是`ctl`，则可用的`<wlan_subtype>`有：`ps-poll`, `rts`, `cts`, 
`ack`, `cf-end`, `cf-end-ack`。

如果`<wlan_type>`是`data`，则可用的`<wlan_subtype>`有：`data`, `data-cf-ack`, 
`data-cf-poll`, `data-cf-ack-poll`, `null`, `cf-ack`, `cf-poll`, `cf-ack-poll`, 
`qos-data`, `qos-data-cf-ack`, `qos-data-cf-poll`, `qps-data-cf-ack-poll`, `qos`,
`qos-cf-poll`, `qos-cf-ack-poll`。

### `subtype <wlan_subtype>`
如果IEEE 802.11帧的subtype匹配`<wlan_subtype>`，并且帧拥有这个`<wlan_subtype>`则为true。

### `dir <dir>`
如果IEEE 802.11帧方向匹配`<dir>`则为true。可用的方向有：`nods`, `tods`, `fromds`, 
`dstods`, 或者是一个数字的值。

### `vlan [vlan_id]`
如果是IEEE 802.1Q VLAN包则为true。如果指定`[vlan_id]`，则需要包拥有的`vlan_id`才为true。

### `mpls [label_num]`
如果是MPLS包则为true。如果指定`[label_num]`，只有包拥有`label_num`的时候才为true。

### `pppoed`
如果是一个PPP-over-Ethernet Discovery包(Ethernet type 0x8863)则为true。

### `pppoes [session_id]`
如果是PPP-over-Ethernet Session包(Ethernet type 0x8864)则为ture。如果指定`session_id`，
只有包拥有`session_id`时才为true。

### `iso proto <protocol>`
如果是一个拥有`<protocol>`协议的OSI包才为true。`<protocol>`可以是一个数字或者`clnp`, `esis`, `isis`。

### `clnp`, `esis`, `isis`
```
iso proto <protocol>
```
的简写。`<protocol>`是以上的一个值。

### `l1`, `l2`, `iih`, `lsp`, `snp`, `csnp`, `psnp`
IS-IS PDU类型的简写。

### `vpi <n>`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要一个虚拟的路径标识符`<n>`。

### `vci <n>`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要一个虚拟的频道标识符`<n>`。

### `lane`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要是ATM LANE包。

### `llc`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要是LLC-encapsulated包。

### `oamf4s`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要是OAM F4 flow cell(VPI=0 & VCI=3)段。

### `oamf4e`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要是end-to-end OAM F4 flow cell(VPI=0 & VCI=4)段。

### `oamf4`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要是end-to-end OAM F4 flow cell(VPI=0 & (VCI=3 | VCI=4))段。

### `oam`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要是end-to-end OAM F4 flow cell(VPI=0 & (VCI=3 | VCI=4))段。

### `metac`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要meta signaling circuit(VPI=0 & VCI=1)。

### `bcc`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要broadcast signaling circuit(VPI=0 & VCI=2)。

### `sc`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要signaling circuit(VPI=0 & VCI=5)。

### `ilmic`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要ILMI circuit(VPI=0 & VCI=16)。

### `connectmsg`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要signaling circuit和Q.2931 Setup, 
Call Proceeding, Connect, Connect Ack, Release, Release Done message。

### `metaconnect`
如果是一个ATM包则为true。对于Solaris上的SunATM，需要signaling circuit和Q.2931 Setup, 
Call Proceeding, Connect, Connect Ack, Release, Release Done message。

### `<expr> <relop> <expr>`
关系表达式为真是为true。`<relop>`是`>`, `<`, `>=`, `<=`, `=`, `!=`中的一个。
`<expr>`是一个算术表达式，由十进制常量组成(标准C语言语法)，普通的两目操作符
`[+, -, *, /, &, |, <<, >>]`，一个长度运算符，特殊的包访问器。所有的比较都是无符号的，
例如0x80000000和0xffffffff都`>`0。要访问包内的内容，使用以下的语法：
```
<proto> [<expr> : <size>]
```
`<proto>`是以下中的一个`ether`, `fddi`, `tr`, `wlan`, `ppp`, `slip`, `link`, `ip`, 
`arp`, `rarp`, `tcp`, `udp`, `icmp`, `ip6`, `radio`和表示协议层的下标运算。
(`ether`, `fddi`, `wlan`, `tr`, `ppp`, `slip`, `link`表明是链路层)。注意，`tcp`, `udp`
和其他上层协议只对IPv4有效，IPv6无效。字节位移相对于表示的协议层，它通过`<expr>`指定。
`<size>`是可选的表示需要的字节数。它可以是1, 2, 4或者默认的1。length关键字`len`给出包的长度。

例如，`ether[0] & 1 != 0`捕捉所有的广播包。`ip[0] & 0xf != 5`捕捉所有包含IPv4选项的包。
`ip[6:2] & 0x1fff = 0`捕捉unfragmented IPv4数据报和frag zero of fragmented IPv4数据报。
这个检查隐式作用于`tcp`和`udp`下标操作。例如`tcp[0]`永远意味着tcp包着的第一个字节。

一些位移和域值可以使用名字替换数字。以下合法的的协议头域位移：`icmptype`(ICMP type field), 
`icmpcode`(ICMP code field), `tcpflags` (TCP flags field)。

`icmptype`可用的值有：`icmp-echoreply`, `icmp-unreach`, `icmp-sourcequench`, 
`icmp-redirect`, `icmp-echo`, `icmp-routeradvert`, `icmp-routersolicit`, `icmp-timxceed`, 
`icmp-paramprob`, `icmp-tstamp`, `icmp-tstampreply`, `icmp-ireq`, `icmp-ireqreply`, 
`icmp-maskreq`, `icmp-maskreply`。

`tcpflags`可用的值有：`tcp-fin`, `tcp-syn`, `tcp-rst`, `tcp-push`, `tcp-ack`, `tcp-urg`。

原语可以结合使用:
使用括号括起来一组原语和操作符，在shell上括号必转义。

非(`!`或者`not`)。  
与(`&&`或者`and`)。  
或(`||`或者`or`)。  

非具有最高优先级。与或具有相同的优先级，从左到右的结合方向。

如果一个标识符没有指定关键字，则假设为最近的关键字。例如：
```
not host vs and ace
```
是以下的缩写
```
not host vs and host ace
```
不要跟以下搞混
```
not (host vs or ace)
```

# 例子
选择所有到达或者离开sundown主机的包
```
host sundown
```

选择主机helios与hot或者ace通信的包
```
host helios and \(hot or ade \)
```

选择所有在ace和非helios的ip包
```
ip host ade and not helios
```

选择所有的本地主机和主机在Berkeley的通信包
```
net ucb-ether
```

选择所有经过网络snup的tcp通信包
```
gateway snup and (port ftp or ftp-data)
```

选择源或者目标不到本地主机的通信
```
ip and not net localnet
```

选择开始和结束包(SYN和FIN包)，不涉及本地主机的会话
```
tcp[tcpflags] & (tcp-syn|tcp-fin) != 0 and not src and dst net localnet
```

选择所有80端口的HTTP IPv4包。也就是说只打印包含数据的包，不包含SYN，FIN，ACK-only的包。
```
tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)
```

选择所有发送经过snup大于576 bytes的包
```
gateway sunp and ip[2:2] > 576
```

选择IP广播或者多播包，并且不经过Ethernet广播或者多播
```
ether[0] & 1 = 0 and ip[16] >= 224
```

选择所有的非echo请求响应ICMP包，也就是说非ping包：
```
icmp[icmptype] != icmp-echo and icmp[icmptype] != icmp-echoreply
```

# 相关文章
- [tcpdump手册](/2017/10/24/man-tcpdump/)
