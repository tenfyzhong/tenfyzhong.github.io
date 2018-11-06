---
title: 分支预测错误处罚
categories:
  - 操作系统
tags:
  - 操作系统
date: 2018-11-06 21:45:10
keywords: 操作系统,性能
---

一个错误的分支预测，会导致20～40个时钟周期的浪费。
<!-- more -->

最精密的分支预测硬件也只能有大约50%的正确率。分支行为很容易预测时，每次调用函数需要大约13个时钟周期，
而分支行为是随机模式时，每次调用需要大约35个时钟周期。因此可以推断出分支预测的处罚大约是44个时钟周期。

# 预测错误处罚的计算  
假设预测错误的概率是p，如果没有预测错误，执行代码的时间是T<sub>OK</sub>，而预测错误的处罚是T<sub>MP</sub>。
那么，作为p的一个函数，执行代码的平均时间是T<sub>avg</sub>(p)=(1-p)T<sub>OK</sub>+p(T<sub>OK</sub>+T<sub>MP</sub>)。
如果已知T<sub>OK</sub>和T<sub>ran</sub>(当p=0.5时的平均时间)，代入等式，我们有
T<sub>ran</sub>=T<sub>avg</sub>(0.5)=T<sub>OK</sub>+0.5T<sub>MP</sub>，
所以有T<sub>MP</sub>=2(T<sub>ran</sub>-T<sub>OK</sub>)。因此，已知T<sub>OK</sub>=13和T<sub>ran</sub>=35，我们有
T<sub>MP</sub>=44。
