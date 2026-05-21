---
title: tcpdump 与 pcap-filter 使用手册
categories:
  - "网络技术"
tags:
  - "tcpdump"
  - "pcap-filter"
  - "packet-capture"
  - "reference"
date: 2017-10-24 18:48:09
keywords: man,tcpdump,pcap-filter,packet-capture,bpf
aliases:
  - /2017/10/24/man-tcpdump/
  - /2017/10/25/man-pcap-filter/
  - /posts/man-pcap-filter/
---

`tcpdump` 是最常用的命令行抓包工具，`pcap-filter` 是它使用的过滤表达式语法。实际排查网络问题时，两者总是一起出现：先决定在哪里抓包，再用过滤表达式把无关流量排除掉，最后根据协议输出或者 pcap 文件继续分析。

<!-- more -->

# 基本用法

最常见的命令形式如下：

```bash
tcpdump [options] [expression]
```

`options` 控制抓包接口、输出格式、保存文件等行为；`expression` 是过滤表达式，只让匹配的包进入输出或者 pcap 文件。

例如，只抓取 `eth0` 上访问 `10.0.0.10:3306` 的 TCP 包：

```bash
tcpdump -i eth0 -nn 'tcp and host 10.0.0.10 and port 3306'
```

常用习惯：

- 默认加 `-n` 或 `-nn`，避免 DNS 和端口名解析影响排查速度。
- 默认指定 `-i`，不要依赖 tcpdump 自动选择接口。
- 复杂过滤表达式使用单引号包起来，避免 `&`、`|`、`(`、`)` 被 shell 解释。
- 需要后续用 Wireshark 分析时，用 `-w` 保存原始包，不要只看文本输出。

# 抓包流程

`tcpdump` 会从指定网络接口读取包，经过 `pcap-filter` 编译出来的 BPF 过滤程序筛选后，再打印到终端或者写入文件。

读取网卡流量通常需要 root 权限；读取已经保存的 pcap 文件不需要 root 权限。

如果不指定 `-c`，`tcpdump` 会一直抓包，直到收到 `Ctrl-C`、`SIGINT` 或 `SIGTERM`。退出时会打印几个计数：

- `captured`：tcpdump 收到并处理的包数。
- `received by filter`：被过滤器接收的包数。
- `dropped by kernel`：内核因缓冲区不足等原因丢弃的包数。

如果 `dropped by kernel` 不为 0，说明抓包端已经丢包。可以尝试增大 `-B` 缓冲区、收窄过滤条件、降低输出量，或者直接使用 `-w` 写文件。

# 常用参数

## 接口与抓包数量

```bash
tcpdump -D
tcpdump -i eth0
tcpdump -i any
tcpdump -c 100 -i eth0
```

- `-D`：列出可抓包的接口。
- `-i <interface>`：指定接口。Linux 上可以使用 `any` 抓取所有接口，但 `any` 不适合需要精确链路层信息的场景。
- `-c <count>`：抓到指定数量的包后退出。
- `-p`：不把网卡切到混杂模式。
- `-I`：把支持的无线网卡切到 monitor mode。

## 名称解析与输出详细度

```bash
tcpdump -nn -i eth0
tcpdump -q -i eth0
tcpdump -vvv -i eth0
tcpdump -tttt -i eth0
```

- `-n`：不把地址解析成主机名。
- `-nn`：不解析主机名，也不把端口解析成服务名。
- `-q`：输出更少的协议信息。
- `-v`、`-vv`、`-vvv`：输出逐级增加的协议信息。
- `-t`：不打印时间戳。
- `-tt`：打印 Unix 时间戳。
- `-ttt`：打印当前行与上一行的时间差。
- `-tttt`：打印可读时间。
- `-ttttt`：打印当前行与第一行的时间差。

## 包内容展示

```bash
tcpdump -A -s 0 'tcp port 80'
tcpdump -X -s 0 'host 10.0.0.10'
tcpdump -e -i eth0 'arp or ip'
```

- `-A`：用 ASCII 打印包内容，适合查看明文 HTTP 等文本协议。
- `-x`：用十六进制打印包内容，不包含链路层头。
- `-xx`：用十六进制打印包内容，包含链路层头。
- `-X`：同时用十六进制和 ASCII 打印包内容，不包含链路层头。
- `-XX`：同时用十六进制和 ASCII 打印包内容，包含链路层头。
- `-e`：打印链路层头，例如 MAC 地址。
- `-s <snaplen>`：设置每个包截取长度。排查内容时通常使用 `-s 0`，表示尽量抓完整包。

## 文件读写与轮转

```bash
tcpdump -i eth0 -s 0 -w capture.pcap 'host 10.0.0.10'
tcpdump -nn -r capture.pcap
tcpdump -i eth0 -s 0 -C 100 -W 10 -w capture.pcap
tcpdump -i eth0 -s 0 -G 60 -w 'capture-%Y%m%d-%H%M%S.pcap'
```

- `-w <file>`：把原始包写入 pcap 文件。
- `-r <file>`：从 pcap 文件读取并解析。
- `-C <size>`：写文件达到指定大小后轮转，单位是 1,000,000 字节。
- `-W <count>`：配合 `-C` 限制轮转文件数量，超过后覆盖旧文件；配合 `-G` 时达到数量后退出。
- `-G <seconds>`：按时间轮转文件，文件名通常配合 `strftime` 格式。
- `-z <command>`：轮转后执行命令处理旧文件，例如压缩。
- `-U`：写文件时使用包级缓冲，便于边抓边读。

## 过滤器调试

```bash
tcpdump -d 'tcp port 443'
tcpdump -dd 'tcp port 443'
tcpdump -ddd 'tcp port 443'
tcpdump -F filter.txt
```

- `-d`：以可读形式打印编译后的过滤程序。
- `-dd`：以 C 代码片段形式打印过滤程序。
- `-ddd`：以十进制数字形式打印过滤程序。
- `-F <file>`：从文件读取过滤表达式。

# 常用抓包命令

抓取某个主机的所有流量：

```bash
tcpdump -nn -i eth0 'host 10.0.0.10'
```

抓取源或者目标端口是 443 的 TCP 包：

```bash
tcpdump -nn -i eth0 'tcp port 443'
```

只抓取目标端口是 3306 的包：

```bash
tcpdump -nn -i eth0 'dst port 3306'
```

抓取两个主机之间的通信：

```bash
tcpdump -nn -i eth0 'host 10.0.0.10 and host 10.0.0.20'
```

抓取某个网段，但排除 SSH：

```bash
tcpdump -nn -i eth0 'net 10.0.0.0/24 and not port 22'
```

抓取 DNS 请求和响应：

```bash
tcpdump -nn -i eth0 'udp port 53 or tcp port 53'
```

抓取 ARP 包：

```bash
tcpdump -nn -e -i eth0 'arp'
```

抓取 ICMP 包，但排除普通 ping 请求和响应：

```bash
tcpdump -nn -i eth0 'icmp[icmptype] != icmp-echo and icmp[icmptype] != icmp-echoreply'
```

抓取 TCP 建连和断连包：

```bash
tcpdump -nn -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0'
```

抓取 80 端口上带有 payload 的 IPv4 TCP 包，排除 SYN、FIN、纯 ACK：

```bash
tcpdump -nn -i eth0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'
```

# pcap-filter 过滤语法

过滤表达式由一个或多个原语组成。原语可以带三类修饰符：类型、方向、协议。

## 类型修饰符

类型修饰符说明目标值是什么：

- `host`：主机地址。
- `net`：网络地址。
- `port`：端口。
- `portrange`：端口范围。

示例：

```bash
host 10.0.0.10
net 10.0.0.0/24
port 443
portrange 8000-8999
```

如果省略类型，默认按 `host` 处理。

## 方向修饰符

方向修饰符说明流量方向：

- `src`：源地址或源端口。
- `dst`：目标地址或目标端口。
- `src or dst`：源或目标，默认值。
- `src and dst`：源和目标都匹配。
- `inbound`、`outbound`：部分链路层支持的入站、出站方向。

示例：

```bash
src host 10.0.0.10
dst net 10.0.0.0/24
src or dst port 443
```

IEEE 802.11 还支持 `ra`、`ta`、`addr1`、`addr2`、`addr3`、`addr4` 等地址方向。

## 协议修饰符

协议修饰符限制匹配的协议：

- 链路层：`ether`、`fddi`、`tr`、`wlan`。
- 网络层：`ip`、`ip6`、`arp`、`rarp`。
- 传输层：`tcp`、`udp`、`icmp`。

示例：

```bash
ether src 00:11:22:33:44:55
arp host 10.0.0.10
tcp port 443
udp portrange 6000-7000
```

如果省略协议，`pcap-filter` 会使用合法组合。例如：

- `src 10.0.0.10` 等价于 `(ip or arp or rarp) src 10.0.0.10`。
- `port 53` 等价于 `(tcp or udp) port 53`。

## 逻辑运算

可以使用逻辑运算组合多个原语：

- 非：`not` 或 `!`。
- 与：`and` 或 `&&`。
- 或：`or` 或 `||`。

示例：

```bash
host 10.0.0.10 and not port 22
tcp and (port 80 or port 443)
tcp and not (src net 10.0.0.0/24 and dst net 10.0.0.0/24)
```

非运算优先级最高；与、或优先级相同，并且从左到右结合。复杂表达式建议显式加括号。

相同修饰符可以省略。例如：

```bash
tcp dst port ftp or ftp-data or domain
```

等价于：

```bash
tcp dst port ftp or tcp dst port ftp-data or tcp dst port domain
```

# 常用过滤原语

## 主机、网络、端口

```bash
dst host 10.0.0.10
src host 10.0.0.10
host 10.0.0.10

dst net 10.0.0.0/24
src net 10.0.0.0/24
net 10.0.0.0/24

dst port 443
src port 443
port 443

dst portrange 8000-8999
src portrange 8000-8999
portrange 8000-8999
```

端口表达式可以加 `tcp` 或 `udp` 限定：

```bash
tcp dst port 443
udp src port 53
```

## 长度、广播与多播

```bash
less 128
greater 1500
ether broadcast
ether multicast
ip broadcast
ip multicast
ip6 multicast
```

- `less <length>` 等价于 `len <= <length>`。
- `greater <length>` 等价于 `len >= <length>`。
- `ether multicast` 等价于 `ether[0] & 1 != 0`。

## 协议匹配

```bash
ip
ip6
arp
rarp
tcp
udp
icmp
ip proto \tcp
ip6 proto \udp
proto \icmp
```

`tcp`、`udp`、`icmp` 既是协议名，也是关键字。写在 `proto` 后面时需要转义：

```bash
ip proto \tcp
```

## VLAN、MPLS 与 PPPoE

```bash
vlan
vlan 100
mpls
mpls 200
pppoed
pppoes
pppoes 1234
```

- `vlan [vlan_id]`：匹配 IEEE 802.1Q VLAN 包。
- `mpls [label_num]`：匹配 MPLS 包。
- `pppoed`：匹配 PPP-over-Ethernet Discovery 包。
- `pppoes [session_id]`：匹配 PPP-over-Ethernet Session 包。

# 字节偏移与位运算

`pcap-filter` 支持按协议头偏移访问包内容：

```bash
<proto>[<offset>:<size>]
```

- `<proto>` 可以是 `ether`、`ip`、`ip6`、`tcp`、`udp`、`icmp` 等。
- `<offset>` 是相对该协议头起始位置的字节偏移。
- `<size>` 可以是 `1`、`2`、`4`，省略时默认是 `1`。

示例：

```bash
ether[0] & 1 != 0
ip[0] & 0xf != 5
ip[6:2] & 0x1fff = 0
```

含义分别是：

- 匹配以太网广播或多播包。
- 匹配包含 IPv4 options 的包。
- 匹配未分片的 IPv4 包，或者分片包的第一个分片。

算术表达式支持 `+`、`-`、`*`、`/`、`&`、`|`、`<<`、`>>`，关系运算支持 `>`、`<`、`>=`、`<=`、`=`、`!=`。所有比较都按无符号数处理。

## TCP flags 示例

TCP 头中的控制位位于第 13 字节：

```text
CWR|ECE|URG|ACK|PSH|RST|SYN|FIN
```

只匹配单独设置 SYN 的包：

```bash
tcpdump -nn -i eth0 'tcp[13] == 2'
```

匹配所有设置了 SYN 的包，不关心 ACK 或其他位：

```bash
tcpdump -nn -i eth0 'tcp[13] & 2 == 2'
```

更可读的写法是使用内置字段名：

```bash
tcpdump -nn -i eth0 'tcp[tcpflags] & tcp-syn != 0'
```

常用 TCP flag 名称：

- `tcp-fin`
- `tcp-syn`
- `tcp-rst`
- `tcp-push`
- `tcp-ack`
- `tcp-urg`

例如，匹配带有 PUSH 标志的 TCP 包：

```bash
tcpdump -nn -i eth0 'tcp[tcpflags] & tcp-push != 0'
```

# 输出格式

`tcpdump` 的文本输出按协议解释，不同协议格式不同。排查时最常见的是链路层、ARP、TCP、DNS 和 IP 分片。

## 链路层头

指定 `-e` 后，输出会包含链路层头。例如以太网包会打印源 MAC、目标 MAC、EtherType 和包长度。

```bash
tcpdump -nn -e -i eth0 'arp or ip'
```

这适合排查 ARP、MAC 地址漂移、错误网关等问题。

## ARP

ARP 输出会显示请求或响应：

```text
arp who-has 192.168.1.10 tell 192.168.1.1
arp reply 192.168.1.10 is-at 00:11:22:33:44:55
```

第一行表示 `192.168.1.1` 正在询问谁拥有 `192.168.1.10`；第二行表示对应主机回复了自己的 MAC 地址。

## TCP

TCP 输出的基本格式：

```text
src > dst: flags data-seqno ack window urgent options
```

- `src`、`dst`：源和目标地址、端口。
- `flags`：TCP 标志位。
- `data-seqno`：本包携带的数据序列范围。
- `ack`：对端期望收到的下一个序列号。
- `window`：接收窗口大小。
- `urgent`：紧急指针。
- `options`：TCP options，例如 MSS。

TCP flag 常见显示：

- `S`：SYN。
- `F`：FIN。
- `P`：PUSH。
- `R`：RST。
- `U`：URG。
- `W`：ECN CWR。
- `E`：ECE。
- `.`：ACK。

例如：

```text
10.0.0.1.53000 > 10.0.0.2.443: S 1000:1000(0) win 64240 <mss 1460>
10.0.0.2.443 > 10.0.0.1.53000: S 2000:2000(0) ack 1001 win 65160 <mss 1460>
10.0.0.1.53000 > 10.0.0.2.443: . ack 1 win 502
```

默认情况下，tcpdump 会在每条连接里显示相对 sequence number；需要原始 sequence number 时使用 `-S`。

如果 snaplen 太小，tcpdump 可能无法解释完整协议头，会出现类似 `[|tcp]`、`[bad opt]`、`[bad hdr length]` 的提示。排查内容时优先使用 `-s 0`。

## DNS

DNS 查询示例：

```text
10.0.0.10.53000 > 10.0.0.53.53: 1234+ A? example.com. (29)
```

这里 `1234` 是查询 ID，`+` 表示递归查询，`A?` 表示查询 A 记录。

DNS 响应示例：

```text
10.0.0.53.53 > 10.0.0.10.53000: 1234 1/0/0 A 93.184.216.34 (45)
```

`1/0/0` 分别表示 answer、authority、additional 记录数量。

## IP 分片

IP 分片输出类似：

```text
(frag 595a:328@0+)
(frag 595a:204@328)
```

- `595a`：分片 ID。
- `328`、`204`：当前分片大小，不包含 IP 头。
- `@0`、`@328`：分片在原始数据报中的偏移。
- `+`：后面还有更多分片；没有 `+` 表示最后一个分片。

只有第一个分片包含上层协议头，后续分片通常只会显示源、目标地址和分片信息。

# 排查建议

先确认抓包位置。客户端、服务端、网关、容器宿主机看到的包可能完全不同，尤其是 NAT、负载均衡和 overlay 网络场景。

优先保存 pcap：

```bash
tcpdump -i eth0 -nn -s 0 -w issue.pcap 'host 10.0.0.10'
```

保存 pcap 后再用 `tcpdump -r` 或 Wireshark 反复分析，比直接在终端刷输出更可靠。

控制过滤范围。先从 `host`、`port`、`proto` 这类稳定条件开始，再逐步加入 TCP flags、payload 长度、字节偏移等复杂条件。

避免名称解析干扰。排查 DNS、连接耗时、丢包时，默认使用 `-nn`，否则 tcpdump 自己的解析请求可能污染抓包结果。

关注丢包计数。退出时如果看到 `dropped by kernel`，当前抓包结果不能代表完整流量，需要降低输出成本或者扩大抓包缓冲区。

# 相关文章

- [libpcap入门教程](/posts/libpcap-tutorial/)
