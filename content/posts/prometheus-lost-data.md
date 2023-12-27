---
title: prometheus丢数据调试与处理
date: 2017-09-02 17:38:57
categories:
  - 后台
tags:
  - prometheus
  - 监控
---
influxdb数据旁路一份到prometheus后，prometheus的图有时延时很大，主要是在业务忙的
时候，闲的时候是可以处理到数据的。而influxdb的数据是可以正常显示的。而且这时牛逼
的google并帮不了忙，各种关键字去搜索都找不到相关的问题。


<!-- more -->


# 架构
![](http://ac-HSNl7zbI.clouddn.com/59gH7R0uXcjFT8TpJsAAMOOBHun5ONgIW2gfzByU.jpg)

# 调试过程
1. 先去prometheus的web控制台看图。初看这个图感觉是没有问题的，数据是连续的。
![prometheus_pic](http://ac-HSNl7zbI.clouddn.com/Ias3BNfPP47fGOB3MYGVfAyrQXFflLShxGVMONTG.jpg)
仔细看，其实直线那段是没有数据有。用grafana配到同一个prometheus来看一下grafana的
图长这样
![grafana_pic](http://ac-HSNl7zbI.clouddn.com/XaTYmLkeKmSM19VbOtmgn5PoA7dz61kXDhs4Thnj.jpg)
在grafana是可以明显看到中间是丢了一段时间的。而且prometheus的图却是连续的。最开始我没有看出来。

2. 把生产环境的docker部到自己的电脑，看控制台是没有问题的。所以猜想是生产环境的
数据量过大，prometheus没处理过来引起的。
上去生产环境抓包，
先找一下prometheus和influxdb_exporter的ip。
```bash
docker exec -it prometheus ip addr show
```
输出如下：
![](http://ac-HSNl7zbI.clouddn.com/DoM3j9rg8vysCIBkz3fvG1kNy7uOeYB0yaes2E7f.jpg)
prometheus用了eth0端口，ip:172.17.0.102

同样找出influxdb_exporter的ip:172.17.0.99

我们只抓这两台机器的包，免得其他的干扰：
```bash
tcpdump -i docker0 host 172.17.0.102 and 172.17.0.99
```
![](http://ac-HSNl7zbI.clouddn.com/Cf84G8kdkTc9ctNhhaQGzzACYBLs4C6FxeFgVxQf.jpg)

在13:32:28.162的时候prometheus发起握手，完了之后，发请求到influxdb_exporter拉数据  
在13:32:32.112的时候influxdb\_exporter发了数据包。然后prometheus接着就回了一下
rst的包了。后面influxdb\_exporter应该是还没收到prometheus的rst包，继续发第二段包。
所以这个包prometheus是没有收到的。

找到prometheus的配置：

> scrape_configs:  
>  - job_name: 'prometheus'  
>    scrape_interval: 5s  
>    static_configs:  
>      - targets:  
>         - "influxdb_exporter:9122"  

配置了5s去influxdb_exporter抓一次数据。而prometheus发rst包的时候，差不多在4s的时
间隔上。prometheus的5s配置包括了收包前后的处理和收包的过程，在13:32:32.112的时候
就回rst，以免雪崩。  
把配置改成10s，重新拉起服务。可以看数据正常了。  
![](http://ac-HSNl7zbI.clouddn.com/kS2CbBWltaxcrswhlWGut6lK5XwwmF7OBN7J8FBz.jpg)
