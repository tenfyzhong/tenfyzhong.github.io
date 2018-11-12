---
title: nginx平滑权重轮询算法分析
categories:
  - null
tags:
  - null
date: 2018-11-12 19:54:47
keywords:
---


<!-- more -->
# 证明权重合理
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
