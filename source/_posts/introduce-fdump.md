---
title: fdump tcp抓包框架
categories:
  - 网络
tags:
  - 后台
  - 网络
date: 2019-06-25 13:21:30
keywords: 后台,网络,tcpdump
---

fdump是一个创建抓二进制包解析程序的框架。  
对于自定义的二进制通信协议，在调试的时候会很困难。无论tcpdump还是wireshark抓到包都不能直接看到里面的内容。

fdump做的事情就是抓包，并且把内容给到调用函数进行解析并返回一个可以阅读的对象，
fdump把它做展示。  
<!-- more -->
# 简介
fdump的仓库地址：https://github.com/tenfyzhong/fdump

fdump的面板由三部分构造，左边为抓到的每一个包，称之为简介面板。右边为包的详细显示内容，
称之为详情面板。下边为状态栏。

以下图采自fdump中的tcp的程序的例子:   
https://github.com/tenfyzhong/fdump/tree/master/_examples/tcp  
![fdump-example-tcp](https://tenfy.cn/picture/fdump-example-tcp.png)

fdump支持以下的特性：
- tui展示所有的抓包记录
- 对抓到的包记录进行重放
- 保存记录到文件
- 从文件中加载记录
- 支持tcp
- 支持udp

使用fdump创建抓包程序非常简单，只要以下几步：
1. 创建一个函数用于解析二进制包，原型为：`func(gopacket.Flow, gopacket.Flow, []byte) (bodies []interface{}, n int, err error)`
2. 创建一个函数用于展示简介信息，这个函数的返回值会在简介面板上进行展示，原型为：`func(record *Record) []string`
3. 创建一个函数用于展示详情信息，这个函数的返回值会以字节串形式在详情面板展示，原型为：`DetailFunc func(record *Record) string`
4. (可选)创建重放时的hook函数，这个函数可以对重放的流程做一些处理。


程序进行起来后，有一堆可用的快捷键，详细见：https://github.com/tenfyzhong/fdump#key

# 状态说明
在状态栏的左边，有四个字母。
- F:代表frozen状态，在简介面板按f触发和解除
- D:代表进行详情面板，在简介面板按回车键进入，按q退回到简介面板
- S:代表暂停抓包状态，按s触发和解除
- M:代表多选状态，当前状态在简介面板中选择多个包进行删除、保存等操作

# 例子
```go
func decode(net, transport gopacket.Flow, buf []byte) (bodies []interface{}, n int, err error) {
	if len(buf) < 4 {
		err = fdump.ErrPkgNoEnough
		return
	}
	pkgLen := binary.BigEndian.Uint32(buf)
	if uint32(len(buf)) < pkgLen {
		err = fdump.ErrPkgNoEnough
		return
	}
	str := string(buf[4:pkgLen])
	bodies = append(bodies, str)
	n = pkgLen
	return
}

func brief(record *fdump.Record) []string {
	if record == nil || len(record.Bodies) == 0 {
		return nil
	}
	str, ok := record.Bodies[0].(string)
	if !ok {
		return nil
	}
	return []string{str[:10]}
}

func detail(record *fdump.Record) string {
	str, ok := record.Bodies[0].(string)
	if !ok {
		return ""
	}
	return str
}

func postSend(conn net.Conn, record *fdump.Record) error {
	lenBuf := make([]byte, 4)
	lenLen := 0
	for lenLen < 4 {
		err := conn.SetReadDeadline(time.Now().Add(1*time.Second))
		if err != nil {
			return err
		}
		n, err := conn.Read(headBuf[lenLen:])
		if err != nil {
			return err
		}
		lenLen += n
	}

	bodyLen := binary.BigEndian.Uint32(lenBuf) - 4
	body := make([]byte, bodyLen)
	curLen := 0
	for curLen < int(bodyLen) {
		err := conn.SetReadDeadline(time.Now().Add(t*time.Second))
		if err != nil {
			return err
		}
		n, err := conn.Read(body[curlen:])
		if err != nil {
			return err
		}
		curlen += n
	}
	return nil
}

func main() {
	logging.SetLevel(logging.INFO, "")
	fdump.Init()
	replayHook := &fdump.ReplayHook{
		PostSend: postSend,
	}
	briefAttributes := []*fdump.BriefColumnAttribute{&fdump.BriefColumnAttribute{
			Title: "Head10",
			MaxWidth: 10,
		},
	}

	a := fdump.NewApp(decode, brief, detail, replayHook, briefAttributes)
	a.Run()
}
```

这个例子程序非常简单，创建了一个decode函数用于解析包，brief函数用于返回简介面板的字段，
detail函数用于返回详情页显示的内容。postSend用于在重放时，发包后的操作。
在`NewApp`函数中，分别传入以上的几个函数。最后，传入一个简介面板的头的字段。
