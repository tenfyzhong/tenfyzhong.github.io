---
title: Golang直接操作共享内存
date: 2017-09-02 16:58:51
categories: 
  - 后台
tags:
  - go
  - 编程语言
---
Golang不使用cgo，直接操作共享内存。

<!-- more -->

# 前言
故事起源于要搭一个高性能的日志中心。当然使用了elk这一套。但是，对于logstash来说，
它主要使用的是文件日志的方式了捕捉log。而写文件日志的话会非常慢。对于实时日志要
处理滚动的日志更是这样，每次检查是否需要流动日志，然后打开日志，然后写入，然后
关闭，当然这中间可以优化。这一切都是那么慢，发起了n个系统调用，硬盘寻道等。这时
候想到了用共享内存来通信。

# 共享内存的基本知识
要使用共享内存要执行以下几步：
1. 发起一个系统调用，让系统帮你生产一块内存，或者取得一块已经存在的内存来使用。
1. 把内存attach到当前进程，让当前进程可以使用。大家都知道，我们在进程中访问的是
   虚拟内存地址，系统会把它映射到物理内存中。如果没有这一步，第1步创建的内存就
   不能在当前进程访问。
1. 这时就可以对内存进程读写操作了。
1. 进程结束的时候要把上面attach的内存给释放。

# 系统调用的基础知识
什么是系统调用?  
> 系统调用（英语：system call），又称为系统呼叫，指运行在使用者空间的程序向操作
  系统内核请求需要更高权限运行的服务。系统调用提供用户程序与操作系统之间的接口。

以上引自维基百科。  

对于每个系统调用，都一个编号。内核收到编号后，就根据编号去找到对应的内核函数函数
来执行。然后返回给应用程序。  

系统调用是怎么发起的？以下以linux为例。  
1. 应用程序以系统调用号和对应的参数传给系统调用api
1. 系统调用api将系统调用号存到`eax`中，然后发起`0x80`的中断号进行中断
1. 内核中的中断处理函数根据系统调用号，调用对应的内核函数（系统调用）
1. 系统调用完成相应功能，将返回值存入 `eax`，返回到中断处理函数
1. 中断处理函数返回到 API 中
1. API 将 `eax` 返回给应用程序

以上就完成了系统调用。

# 在golang中使用共享内存
了解了系统调用之后，下面就开始使用了。第一步当然是去找golang有没有直接提供共享内
存的api了。几经折腾后，发现它并没有提供直接的api。而其他很多系统调用都提供了直接
的api。究其原因，我想应该是因为这句话吧：
> “不要通过共享内存来通信，而应该通过通信来共享内存”

golang不提供使用共享内存来通信。所以直接不提供了，折腾死你们，让你们用不了。  
于是乎，google一下解决方案，都是通过cgo来调c语言来实现的。stackoverflow的答案也
都是这样。  
回来再来看一下golang的[syscall](https://golang.org/pkg/syscall/)的文档。它提供了
`Syscall`函数。声明如下：
```go
func Syscall(trap, a1, a2, a3 uintptr) (r1, r2 uintptr, err Errno)
```
很显示trap是中断号，a1, a2, a3是系统调用相关的参数。  
对于中断号，在文档中可以看到，所有的系统都已经定义了常量了。而我们要用到的系统调
用有：  
`SYS_SHMGET `: 创建或者取得共享内存。    
`SYS_SHMAT `: 将共享内存attach到当前进程空间。  
`SYS_SHMDT `: 将共享内存从当前进程中deattach。  

具体这三个函数的使用，我们可以参考linux的`shmget`, `shmat`, `shmdt`函数。可以看
到这三个函数跟上面三个系统调用号的常量名字一样的。
以下是这三个函数的声明：
```c
int shmget(key_t key, size_t size, int shmflg);  
void *shmat(int shm_id, const void *shm_addr, int shmflg); 
int shmdt(const void *shmaddr);  
```
以下简单介绍一下这三个函数，具体可以直接去linux上man对应的文档。  
### `shmget`函数
`key`，这个参数的类型`key_y`其实只是一个数字类型。这个参数命名了这一块内存。不要
提供0值就行了，0值是private的，不能在进程间共享。  
`size`，提供了共享内存的大小。  
`shmflg`，权限标志，它的作用与open函数的mode参数一样。如果需要在内存不存在时创建
它，则需要指定`IPC_CREAT`。  
在golang的文档中可以看到，它并没定义`IPC_CREATE`的值。所以我们只能去找到它的值了。
在linux的man文档中，它也没有说明。于是乎，直接把linux的代码clone下来进行了grep
(我用ag，速度非常快的文档查找工具)。从结果中找到了`IPC_CREATE`是一个宏，它的值定
义成了`00001000`。一个8进制的数字。低三位都是0，因为低三位是用来标志权限位的。  

下面我们直接来发起这个系统调用看一下效果，把调用c的参数一一对应到a1, a2, a3中：
```go
shmid, _, err := syscall.Syscall(syscall.SYS_SHMGET, 2, 4, IpcCreate|0600)
```
`Syscall`函数返回了两个值和一个error字段。而c的`shmget`只返回了一个int值，因为这
个函数把结果错误和结果都通过返回值来承载了，如果是小于0的，则是错误，这时对应到
go中应该是err的值，没有错误的时候，我们只需要一个返回值，第二个返回值会一直是0。
第一个返回值就是给`shmat`调用的第一个参数。  

### `shmat`函数
`shm_id`, 这是`shmget`返回id，以标志了要attach的是这一块内存  
`shm_addr`，这个标志需要把它attach到的内存地址，通常填0，让系统去选择地址来attach  
`shmflg`，这个可以值`SHM_RDONLY`表示只读，其他值为可以读写，我们直接传0就好。  

```go
shmaddr, _, err := syscall.Syscall(syscall.SYS_SHMAT, shmid, 0, 0)
```
c函数返回了进程空间地址，这个调用也是只返回了一个值，所我们只接收第一个值。在c中，
如果调用失败，会返回`-1`。在go中，我们只要直接处理err的值就好了。  

### `shmdt`函数
`shmaddr`, 这个参数表示deattach的地址值，是从`shmat`中返回的。
我们在go中直接用defer来调用就好了：
```go
defer syscall.Syscall(syscall.SYS_SHMDT, shmaddr, 0, 0)
```

以下是这个blog用到的代码，可以直接从[gist][]里去下载：
```go
// @file main.go
// @brief
// @author tenfyzhong
// @email tenfyzhong@qq.com
// @created 2017-06-26 17:54:34
package main

import (
	"flag"
	"fmt"
	"os"
	"syscall"
	"time"
	"unsafe"
)

const (
	// IpcCreate create if key is nonexistent
	IpcCreate = 00001000
)

var mode = flag.Int("mode", 0, "0:write 1:read")

func main() {
	flag.Parse()
	shmid, _, err := syscall.Syscall(syscall.SYS_SHMGET, 2, 4, IpcCreate|0600)
	if int(shmid) == -1 {
		fmt.Printf("syscall error, err: %v\n", err)
		os.Exit(-1)
	}
	fmt.Printf("shmid: %v\n", shmid)

	shmaddr, _, err := syscall.Syscall(syscall.SYS_SHMAT, shmid, 0, 0)
	if int(shmaddr) == -1 {
		fmt.Printf("syscall error, err: %v\n", err)
		os.Exit(-2)
	}
	fmt.Printf("shmaddr: %v\n", shmaddr)

	defer syscall.Syscall(syscall.SYS_SHMDT, shmaddr, 0, 0)

	if *mode == 0 {
		fmt.Println("write mode")
		i := 0
		for {
			fmt.Printf("%d\n", i)
			*(*int)(unsafe.Pointer(uintptr(shmaddr))) = i
			i++
			time.Sleep(1 * time.Second)
		}
	} else {
		fmt.Println("read mode")
		for {
			fmt.Println(*(*int)(unsafe.Pointer(uintptr(shmaddr))))
			time.Sleep(1 * time.Second)
		}
	}
}
```

运行一下这个代码块看一下结果：
![](https://tenfy.cn/picture/ipcs-m.jpg)
用ipcs可以看到共享已经成功创建。

对于共享内存的操作，大家还可以看一下`shmctl`这个系统调用的使用。

[gist]: https://gist.github.com/tenfyzhong/767b4a1ed59cc7ead2d446df9fb78e5f
