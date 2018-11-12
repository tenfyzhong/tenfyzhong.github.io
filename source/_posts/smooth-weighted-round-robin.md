---
title: nginx平滑的基于权重轮询算法分析
categories:
  - 后台
tags:
  - 负载均衡
date: 2018-11-12 19:54:47
keywords:
---

nginx使用的平滑权重轮询算法介绍以及原理分析。
<!-- more -->
# 轮询调度
轮询调度非常简单，就是每次选择下一个节点进行调度。比如`{a, b, c}`三个节点，第一次选择a，
第二次选择b，第三次选择c，接下来又从头开始。

这样的算法有一个问题，在负载均衡中，每台机器的性能是不一样的，对于16核的机器跟4核的机器，
使用一样的调度次数，这样对于16核的机器的负载就会很低。这时，就引出了基于权重的轮询算法。

基于权重的轮询调度是在基本的轮询调度上，给每个节点加上权重，这样对于权重大的节点，
其被调度的次数会更多。比如a, b, c三台机器的负载能力分别是4:2:1，则可以给它们分配的权限为4, 2, 1。
这样轮询完一次后，a被调用4次，b被调用2次，c被调用1次。

对于普通的基于权重的轮询算法，可能会产生以下的调度顺序`{a, a, a, a, b, b, c}`。  

这样的调度顺序其实并不友好，它会一下子把大压力压到同一台机器上，这样会产生一个机器一下子很忙的情况。
于是乎，就有了平滑的基于权重的轮询算法。

所谓平滑就是调度不会集中压在同一台权重比较高的机器上。这样对所有机器都更加公平。
比如，对于`{a:5, b:1, c:1}`，产生`{a, a, b, a, c, a, a}`的调度序列就比`{c, b, a, a, a, a, a}`
更加平滑。

# nginx平滑的基于权重轮询算法
nginx平滑的基于权重轮询算法其实很简单。[算法原文](https://github.com/phusion/nginx/commit/27e94984486058d73157038f7950a0a36ecc6e35)
描述为：
> Algorithm is as follows: on each peer selection we increase current_weight
> of each eligible peer by its weight, select peer with greatest current_weight
> and reduce its current_weight by total number of weight points distributed
> among peers.

算法执行2步，选择出1个当前节点。  
1. 每个节点，用它们的当前值加上它们自己的权重。
2. 选择当前值最大的节点为选中节点，并把它的当前值减去所有节点的权重总和。

例如`{a:5, b:1, c:1}`三个节点。一开始我们初始化三个节点的当前值为`{0, 0, 0}`。
选择过程如下表：  

| 轮数 | 选择前的当前权重 | 选择节点 | 选择后的当前权重 |
|------|------------------|----------|------------------|
| 1    | {5, 1, 1}        | a        | {-2, 1, 1}       |
| 2    | {3, 2, 2}        | a        | {-4, 2, 2}       |
| 3    | {1, 3, 3}        | b        | {1, -4, 3}       |
| 4    | {6, -3, 4}       | a        | {-1, -3, 4}      |
| 5    | {4, -2, 5}       | c        | {4, -2, -2}      |
| 6    | {9, -1, -1}      | a        | {2, -1, -1}      |
| 7    | {7, 0, 0}        | a        | {0, 0, 0}        |

我们可以发现，a, b, c选择的次数符合5:1:1，而且权重大的不会被连接选择。7轮选择后，
当前值又回到{0, 0, 0}，以上操作可以一直循环，一样符合平滑和基于权重。

# 一个go版本实现
```go
type Node struct {
    Name    string
    Current int
    Weight  int
}

func SmoothWrr(nodes []*Node) (best *Node) {
    if len(nodes) == 0 {
        return
    }
    total := 0
    for _, node := range nodes {
        if node == nil {
            continue
        }
        total += node.Weight
        node.Current += node.Weight
        if best == nil || node.Current > best.Current {
            best = node
        }
    }
    if best == nil {
        return
    }
    best.Current -= total
    return
}

func example() {
    nodes := []*Node{
        &Node{"a", 0, 5},
        &Node{"b", 0, 1},
        &Node{"c", 0, 1},
    }

    for i := 0; i < 7; i++ {
        best := SmoothWrr(nodes)
        if best != nil {
            fmt.Println(best.Name)
        }
    }
}
```

# 证明权重合理性
**以下证明主要由[安大神](https://github.com/bigbuger)证明得出**  
假如有n个结点，记第i个结点的权重是x<sub>i</sub>。  
设总权重为S=x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>n</sub>  
选择分两步
1. 为每个节点加上它的权重值  
2. 选择最大的节点减去总的权重值  

n个节点的初始化值为[0, 0, ..., 0]，数组长度为n，值都为0。  
第一轮选择的第1步执行后，数组的值为[x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>n</sub>]。  
假设第1步后，最大的节点为j，则第j个节点减去S。  
所以第2步的数组为[x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>j</sub>-S, ..., x<sub>n</sub>]。
执行完第2步后，数组的和为  
x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>j</sub>-S + ... + x<sub>n</sub> =>  
x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>n</sub> - S = S - S = 0。

由此可见，每轮选择，第1步操作都是数组的总和加上S，第2步总和再减去S，所以每轮选择完后的数组总和都为0.


假设总共执行S轮选择，记第i个结点选择m<sub>i</sub>次。第i个结点的当前权重为w<sub>i</sub>。
假设节点j在第t轮(t &lt; S)之前，已经被选择了x<sub>j</sub>次，记此时第j个结点的当前权重为w<sub>j</sub>=t\*x<sub>j</sub>-x<sub>j</sub>\*S=(t-S)\*x<sub>j</sub>&lt;0，
因为t恒小于S，所以w<sub>j</sub>&lt;0。  

前面假设总共执行S轮选择，则剩下S-t轮，上面的公式w<sub>j</sub>=(t-S)\*x<sub>j</sub>+(S-t)\*x=0。
所以在剩下的选择中，w<sub>j</sub>永远小于等于0，由于上面已经证明任何一轮选择后，
数组总和都为0，则必定存在一个节点k使得w<sub>k</sub>&gt;0，永远不会再选中x<sub>j</sub>。

由此可以得出，第i个结点最多被选中x<sub>i</sub>次，即m<sub>i</sub>&lt;=x<sub>i</sub>。  
因为S=m<sub>1</sub>+m<sub>2</sub>+...+m<sub>n</sub>且S=x<sub>1</sub> + x<sub>2</sub> + ... + x<sub>n</sub>。
所以，可以得出m<sub>i</sub>==x<sub>i</sub>。


# 证明平滑性
证明平滑性，只要证明不要一直都是连续选择那一个节点即可。

跟上面一样，假设总权重为S，假如某个节点x<sub>i</sub>连续选择了t(t&lt;x<sub>i</sub>)次，只要存在下一次选择的不是x<sub>i</sub>，即可证明是平滑的。  

假设t=x<sub>i</sub>-1，此是第i个结点的当前权重为w<sub>i</sub>=t\*x<sub>i</sub>-t\*S=(x<sub>i</sub>-1)\*x<sub>i</sub>-(x<sub>i</sub>-1)\*S。  
证明下一轮的第1步执行完的值w<sub>i</sub>+x<sub>i</sub>不是最大的即可。  
w<sub>i</sub>+x<sub>i</sub>=>  
(x<sub>i</sub>-1)\*x<sub>i</sub>-(x<sub>i</sub>-1)\*S+x<sub>i</sub>=>  
x<sub>i</sub><sup>2</sup>-x<sub>i</sub>\*S+S=>  
(x<sub>i</sub>-1)\*(x<sub>i</sub>-S)+x<sub>i</sub>  

因为x<sub>i</sub>恒小于S，所以x<sub>i</sub>-S&lt;=-1。
所以上面：  
(x<sub>i</sub>-1)\*(x<sub>i</sub>-S)+x<sub>i</sub> &lt;= (x<sub>i</sub>-1)\*-1+x<sub>i</sub> = -x<sub>i</sub>+1+x<sub>i</sub>=1。  
所以，第t轮后，再执行完第1步的值w<sub>i</sub>+x<sub>i</sub>&lt;=1。  
如果这t轮刚好是最开始的t轮，则必定存在另一个结点j的值为x<sub>j</sub>\*t，所以有w<sub>i</sub>+x<sub>i</sub>&lt;=1&lt;1\*t&lt;x<sub>j</sub>\*t。  
所以下一轮肯定不会选中x。  
