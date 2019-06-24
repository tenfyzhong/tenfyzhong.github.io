---
title: 一致性模型
categories:
  - 数据库
tags:
  - 数据库
  - 后台
date: 2019-06-20 10:28:43
keywords: 数据库,后台,一致性
---

本文介绍存储中的三种一致性模型。
<!-- more -->
# 含义
一致性的基本含义是读操作一定会返回最新定稿的结果

# 模型
## 严格一致性
有时也叫做顺序一致性，是最严格的一致要求。它要求所有读操作总是返回最新的写结果。
在一个单处理器的机器里，不会有任何问题，因为无论如何操作都会逐一顺序进行。但是，
当系统颁在位置分散的多个数据中心的时候，就变理不那么可靠。要达到严格一致性，
需要某种全局锁机制来给每个操作加上一个时间戳，不论数据位于何处，用户位于何处，
也不论得到响应需要访问多少服务，而且这些服务可以是分散的。

## 因果一致性
这种一致性模式比严格一致性稍弱。这种模型消除了幻想中的需要同步一切操作的单一的全局锁。
避免了无法承受的瓶颈。因果一致性不依赖于时间戳。它使用更为语义化的方法，
尝试去判断事件的原因，并按照因果关系来达到一致。这意味着潜在相关的写操作必须被顺序读出。
如果两个彼此无关的不同操作同时写同一个域，那么这些写操作可以被推断出并不是因果相关的。
而如果一个操作紧接着一个进行，这可能是因果相关的了。因果一致性要求，相关的写操作必须被顺序读出。

## 弱一致性(最终一致性)
最终一致性从字面上解释就是更新最终传播到整个分布式系统的每个角落。但这需要一定的时间。
最终，所有副本都会是一致的。