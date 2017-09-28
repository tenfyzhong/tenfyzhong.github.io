---
title: vim宏的使用
categories:
  - vim
tags:
  - vim
date: 2017-09-27 14:37:20
keywords: vim,macro
---

本文介绍vim宏以及它的魔法。

<!-- more -->
# 宏是什么
vim的宏就是把一系列动作录制起来，然后可以进行播放可以执行同样动作的功能。  
它是vim中最具有魔法的操作了。可能会有人觉得`.`重复操作更具有魔法，但是`.`只能记
重复上一次命令，能做的事情有限，所以它最多就是最经常使用的命令而已，并没有魔法。

宏可以组合一堆复杂的动作，再来重复这些动作，这就是它的魔法。

录制存在寄存器`{0-9a-zA-Z"}`里。然后我就可以重播这个寄存器了。因为宏跟复制用的是同
样的宏存器，所以在宏的使用录制过程中，不能复制到跟宏一样的寄存器中。

先来一张gif感受一下魔法:
![](https://wx3.sinaimg.cn/mw690/69472223gy1fjyavakfcdg20hs0k0x6d.gif)

# 怎么用
宏的使用分两步，第1步录制，第2步播放。
## 录制宏
在normal模式下按`q`再接着一个寄存器然，比如要录制到寄存器`a`中，则按`qa`。
对于`[a-z]`，会直接覆盖写到对应的寄存器，对于`[A-Z]`则是原来寄存器上追加内容。
开始录制后，所有的动作都会记录下来，最后按`q`完成录制。录制过程中，动作跟没有
录制的一模一样。

## 播放宏
播放宏非常简单，按`@`加寄存器就可以了。比如录制到了`a`上，则播放就是`@a`。要注意
的是要移动到我们要播放的位置上，不然可能就产生不到我们想的要效果了。如果出现这种
情况，按`u`可以取消。如果要重播宏n将，则在`@`前按对应的数字就行了。比如要播放宏
10次，则输入`10@a`。

很多时候，我们录制的动作要在特定的行上动作，对于多次播放的宏，如果播放失败，则会
立即停止。

另外，我们在录制宏的时候，最好要录制与行位置无关的宏。就是说在一行内的任何位置
执行的结果都是一样的，不然的就无法录制对多行执行一样动作的宏了。后面会有例子说明。

# 通过例子来学习
我们来些直观的例子看一下这个玩意怎么玩。

## 一个简单的例子
例如有以下的内容
```
hello
world
```
我们要在删除每行的第2个字符，录制到a上。在normal模式下，输入以下的键`qa0lxq`。
录制完后，`hello`就变成了`hllo`了。

然后下移到`world`的行，按`@a`，则第2个字符就被删掉，变成了`wrld`了。

`qa0lxq`的讲解，`q`进入录制宏，`a`录制到a上，`0`移到一行的开头，`l`右移一位，`x`
删除当前的字符，`q`录制完成。

## 交换key/value
例如有以下的内容
```
"foo" = "bar"
"hello" = "world"
```
我们要把它们等号两边互换，就成
```
"foo" = "bar"
"world" = "hello"
```
录到a上的动作为: `qa0df"f"Pldf"0Pq`。
命令就不一一讲解了，就是`qa`后，找到双引号，删除放到右边，再把右边的删除放到左边，
再按`q`完成录制。

## 给枚举后面加上值
这个是出自我工作上的一个需求，有一个上百个成员的枚举，因为有人会在中间插入成员新
的成员，导致其后面的成员值都变了。在网络传输中，传的是成员的值，所以就出现问题了。
然后我要做的就是给每一个成员赋上它的值。
比如以下的例子:
```c
enum Cmd
{
    kOne,
    kTwo,
    kThree,
    kFour,
    kHaha,
    kHehe,
    kFirst,
    kSecond,
    kThird,
    k1,
    k2,
    k3,
};
```
需要对以上kOne赋0，kTwo赋1...  
由于这个例子比较复杂，而且也是非常能体现魔法的例子，下面录了一个视频说明：
<video src="https://blog-1254258176.cossh.myqcloud.com/vim-marco.mov" controls="controls" style="max-width: 100%; display: block; margin-left: auto; margin-right: auto;">
your browser does not support the video tag
</video>

## 给每行加上行号
这个例子介绍一下宏结合命令行编程的使用，给每行开头加上行号。
```
line one
line two
line three
line four
line five
```
<video src="https://blog-1254258176.cossh.myqcloud.com/vim-macro2.mov" controls="controls" style="max-width: 100%; display: block; margin-left: auto; margin-right: auto;">
your browser does not support the video tag
</video>

步骤如下：
1. 设置一个变量i = 0  `let i = 0`
2. 开始录制宏 `qa`
3. 回到开头，插入进入插入模式，然后插入i的值  `0i<c-r>=i<cr> <esc>`
4. 移到下一行 `j`
5. 播放`9@a`

