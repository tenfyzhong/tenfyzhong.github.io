---
title: github pages从cloudflare迁移到verycloud
categories:
  - misc
tags:
  - github pages
date: 2017-11-13 18:51:49
keywords: github pages
---

cloudflare在国内没有站点，导致在国内访问非常非常地慢。经过多个国内的cdn分发比较，
最后使用的verycloud的访问非常的理想。于是把它迁移到了verycloud。
<!-- more -->
# 为什么需要第三方cdn分发
github自带了cdn分发，但是对于自定义域名不支持https。所以改了自定义域名后，直连github的话，
就会变成http的了。其实对于静态博客来说，http并没有什么问题，但是放在大陆就不一样了。
有时你会发现访问自己的博客，会出来各种奇奇怪怪的广告，这些广告都不是你自己插入的。
自己能发现还好，要是自己没发现，别人看到，就会觉得非常low。这些都是网络供应商的功劳，
劫持穿插于各种页面中。

于是乎，解决的方案有两种，一是处理运营商的劫持，这种方案比较麻烦，要改代码处理。
另一种，使用https，简单粗暴。

我选择了改用https。在经过各种google后，有很多使用cloudflare的方案。我也就跟着弄了起来，
很快就把它改好了。很开心，各种广告没有了。


# 使用cloudflare引入的另一个问题
改完cloudflare后，发现访问特别地慢。因为cloudflare在境内没有站点，除了香港有一个站点外，
其他的都要翻洋过海去到美国。而并不是所有的请求都会落在香港的站点上，据说只有中国移动的会落到香港，
具体没求证。反正就是非常的慢。以下是使用cloudflare的测速图:
![cloudflare](https://wx4.sinaimg.cn/mw690/69472223gy1flg72in2hhj20qa0e4taq.jpg)


# 转移到境内的cdn上来
为了解决大陆访问慢的问题，只能转移到大陆的cdn上来了。经过一翻google后，发现有几个cdn可以选择的。
1. 百度云加速。免费的百度云加速有50G/天的流量，但是不支持https。
1. 魔门云。体验版有10G/月的免费流量，支持https，不需要备案。
1. verycloud。50G/月的免费流量，支持https，需要备案。

基于以上，直接放弃了百度云加速。

## 第一次迁移
因为魔门云不需要备案，就直接上了魔门云了。因为之前配置在cloudflare的时候，
要把域名的namespace改到cloudflare，改回来和配置好，最长需要72小时才能全球生效，
于是等了72小时。最后发现，比cloudflare还要慢，看了一下所有的请求都转到奥地利去了。
并不像有些人说的请求会落到香港。

于是问了一下客服，他说免费用户都落到国外去了。

而且最近，它还取消了免费体验版。

于是又暂时迁回了cloudflare。

## 第二次迁移
接下来只要试一下verycloud了。但是使用verycloud需要备案，于是乎，就走了一条长长的备案之路。
整个流程下来，花了10天左右。备案完后，再过两天，才能在备案系统上查到备案信息，才能在verycloud上配置。
先来一个迁移后的效果图：
![verycloud](https://wx2.sinaimg.cn/mw690/69472223gy1flg72jbmt5j20p10dtdhu.jpg)

全国的访问，大部都绿了。看了一下测试的访问站点，基本国内每个省都有站点。但是国外访问却变得非常慢了，
他们需要翻洋过海到我们大陆来了。鉴于境外的ISP没有那么网络供应商没有那么无耻，他们没有劫持的问题。
于时配置了双路解析，让境外直接http请求github的cdn，境内https访问verycloud的cdn。
完了之后，可以看到境外的访问由5s降到了1s以下。

# verycloud配置过程
verycloud注册完之后，需要进行实名，手持身份证啥的上传后，一天之后就会审核过。

等审核过后，配置流程如下：

## 新增证书
verycloud不像cloudflare一样会给你发证书，需要自己去搞证书。我在腾讯云上买的域名，
它直接给了我一个证书。直接就可以拿来用了，过期后再上去申请就好。

在云分发的管理页面，点击证书管理，然后点击`新增`。流程如下：
![verycloud0](https://wx3.sinaimg.cn/mw690/69472223gy1flg8aq74f9j20x80iadit.jpg)

## 新增分发频道
点击频道管理，新增：
![verycloud1](https://wx3.sinaimg.cn/mw690/69472223gy1flg8ar6obrj210b0iujux.jpg)

频道里填域名，然后它会自动填充ICP。加速类型为`云分发`。源站类型选ip，然后添加github的ip:
`192.30.252.153`,`192.30.252.154`。点击下一步。

![verycloud2](https://wx2.sinaimg.cn/mw690/69472223gy1flg8arx9qyj20nn0gtmyx.jpg)
选择静态页面的项然后直接下一步。

![verycloud3](https://wx2.sinaimg.cn/mw690/69472223gy1flg8asj0cnj20nr0gvmyq.jpg)
这里启动SSL加速，选择http回源，开启强制https访问，ssl证书选择上面新增的证书。点击创建。

等待审核后，点击管理页面的域名，可以看到它配置了一个cname的地址，如下：
![verycloud4](https://wx3.sinaimg.cn/mw690/69472223gy1flg8atero7j21200ki41e.jpg)

复制后，然后到你的域名管理端配置以下的记录：
![verycloud5](https://wx1.sinaimg.cn/mw690/69472223gy1flg8au2xn4j215v04lmxu.jpg)
使用双路解析，默认使用CNAME访问verycloud，增加两个国外的A记录访问`192.30.252.153`,
`192.30.252.154`。

以上就已经完成了所有配置。
