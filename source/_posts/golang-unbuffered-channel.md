---
title: golang channel有没buffer的区别
date: 2017-09-20 17:40:57
categories: 后台
tags:
  - golang
keywords: golang,chan
---

初学golang的很多人对buffer大小为0和1的channel都不了解。

下面通过`make(chan bool)`和`make(chan bool, 1)`的例子说明它们的区别。
<!-- more -->

# 说明
引用官方channel的介绍
> If the capacity is zero or absent, the channel is unbuffered and communication 
> succeeds only when both a sender and receiver are ready. Otherwise, the 
> channel is buffered and communication succeeds without blocking if the buffer 
> is not full (sends) or not empty (receives). 

其实官网说得很明白。如果`make`时，容量传0或者不传的话，即创建一个没有buffer的
channel，它们只有发送方和接收方都准备好了，才能通信成功。不然，只要buffer不满就
可以立即发送，或者不空就可以立即接收。

# 例子
## 1 没有buffer，只有发送端
我们通过例子来看一下
```go
func chan0SendOnly() {
	c0 := make(chan bool)
	log.Println("c0, sending")
	c0 <- true
	log.Println("c0, send success")
}

func main() {
	go chan0SendOnly()
	time.Sleep(1 * time.Second)
}
```
创建一个没有buffer的chan，然后在发送一个true到chan里，发送前后打一个log。main函
数调用，然后sleep 1秒，让子goroutine有运行的机会。

运行结果如下：
![chan0][]
可以看到只有sending的日志，success的没有输出。因为没有准备好的channel接收端，所
所就一直阻塞在`c0<-true`上了。一直到main退出，它就退出了。

## 2 没有buffer，同时有发送和接收端
再来看一下同时开启send和receive的情况
```go
func chan1SendRecv() {
	c1 := make(chan bool)
	go func() {
		log.Println("c1, sending")
		c1 <- true
		log.Println("c1, send success")
	}()
	go func() {
		log.Println("c1, receiving")
		time.Sleep(2 * time.Second)  // sleep 2 second
		<-c1
		log.Println("c1, recv success")
	}()
}
func main() {
	go chan1SendRecv()
	time.Sleep(3 * time.Second)
}
```
这个例子我们同时启动了两个goroutine，一个用于发送，一个用于接收，但是我们在接收
之前先sleep了2秒。

运行结果：
![chan1][]
可以看到，sending和receiving都同时打出来了，因为两个goroutine的并行执行，所以两
个打出来的顺序不确定，所以可能你的运行结果是先打了sending。过了两秒后，两个success
才同时打出来。看回我们的代码，在接收的goroutine中，我们并没有sleep，而是直接就发
送了，只是在接收的goroutine中sleep了2秒。

所以可以很明显的感觉到，只有receiver也准备好了，sender才会执行，不然就阻塞在那里
了。

## 3 有buffer，只有发送端
我们来看一下buffer大小为1的channer的情况。
首先看一下只有发送的例子
```go
func chan2SendOnly() {
	c2 := make(chan bool, 1)
	log.Println("c2, sending")
	c2 <- true
	log.Println("c2, send success")
}
func main() {
	go chan2SendOnly()
	time.Sleep(1 * time.Second)
}
```
这个例子跟第1个差不多，只是我们传大小为1。

运行结果：
![chan2][]

可以看到这个跟第一个的比对，这个例子success的log也打出来了。说明了这个channel并
不会阻塞，只在有容量，它立马就发送成功了。


## 4 有buffer，同时有发送和接收端
再来看一下buffer容量为1，同时发送和接收的例子:
```go
func chan3SendRecv() {
	c3 := make(chan bool, 1)
	go func() {
		log.Println("c3, sending")
		c3 <- true
		log.Println("c3, send success")
	}()
	go func() {
		log.Println("c3, receiving")
		time.Sleep(2 * time.Second)  // sleep 2 second
		<-c3
		log.Println("c3, recv success")
	}()
}
func main() {
	go chan3SendRecv()
	time.Sleep(3 * time.Second)
}
```
这个例子跟第2个例子也很像，只是传了buffer大小为1。

运行结果：
![chan3][]
再看一下这个的输出，sending和send success同时输出了，receiving也是同时输出了。
我们在receive里sleep了2秒，所以2秒后才recv success。

再次证明了，只要buffer不满，sending就立马成功了。


# 对比
下面进行对比一下：

| chan0SendOnly        | chan1SendRecv                                        | chan2SendOnly            | chan3SendRecv                                    |
|----------------------|------------------------------------------------------|--------------------------|--------------------------------------------------|
| ![chan0][]           | ![chan1][]                                           | ![chan2][]               | ![chan3][]                                       |
| 没buffer的发送，失败 | 没buffer的发送接收，成功，但是发送要等待接收端准备好 | 有buffer的发送，立即成功 | 有buffer的发送接收成功，发送不用等待接收端准备好 |

*以上图片点击即可放大*

例子代码传送门[gist](https://gist.github.com/tenfyzhong/0fc5819f4885d4a8877659ca24361f09)

[chan0]: https://tenfy.cn/picture/golang-unbuffered-channel0.jpg
[chan1]: https://tenfy.cn/picture/golang-unbuffered-channel1.jpg
[chan2]: https://tenfy.cn/picture/golang-unbuffered-channel2.jpg
[chan3]: https://tenfy.cn/picture/golang-unbuffered-channel3.jpg

