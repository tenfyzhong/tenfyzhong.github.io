---
title: python2与python3踩坑(持续更新...)
categories:
  - 后台
tags:
  - python
date: 2017-09-25 13:24:34
keywords: python2,python3
---

python2与python3踩坑(持续更新...)

<!-- more -->

### unittest.assertListEqual
对于自定义类比较，python3需要实现`__eq__`方法。  

参考：
- [The key differences between Python 2.7.x and Python 3.x with examples](http://sebastianraschka.com/Articles/2014_python_2_3_key_diff.html)
- [What’s New In Python 3.0](https://docs.python.org/3/whatsnew/3.0.html)
