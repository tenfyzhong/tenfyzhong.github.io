---
title: nginx配置http basic认证
date: 2017-09-21 17:47:26
categories: 后台
tags: http,nginx
keywords: http,authentication,nginx
---

http basic认证允许我们对自己的web服务器做简单的认证。可以适当的防止别人浏览器我们
的页面。

<!-- more -->

# 为什么需要http basic认证
对于一些简单的web服务需要做简单的认证。比如:
- 有时我们的web服务很简单，没有账号体系。  
- 开源系统提供的web控制台，比如prometheus,consul等。  

因为基本的浏览器都支持http basic认证，非常方便用户使用。但是如果链路不安全的话，
会很容易就会被抓取到密码。所以只适合我们做一些基本的认证。

# http basic认证是什么
>在HTTP中，基本认证是一种用来允许Web浏览器或其他客户端程序在请求时提供用户名和口
>令形式的身份凭证的一种登录验证方式。
引用自维基百科。

配置了http basic验证的web服务，如果不带鉴权信息的请求，会直接返回401的错误码，并
且返回一个认证域。然后浏览器会弹出输入框，输入账号密码后，浏览器会把密码用base64
编码后，塞到http的头里，再去请求服务器。

浏览器只是对密码做base64编码，所以在链接不安全的情况下使用，被抓到包就很容易被解
到密码。要确保安全性的话，请使用ssl/tls链路。

# 启动http basic认证
## 生成账号密码
我们需要使用`htpasswd`这个工具生成账号密码。  
对于centos，安装httpd-tools
```sh
yum install httpd-tools
```
对于ubuntu安装apache2-utils
```sh
apt install apache2-utils
```
然后执行以下命令生成密码文件
```sh
htpasswd -c /etc/nginx/htpsswd tenfy
```
执行后会要求你输入密码，完了就完成了账号密码的生成。  

如果/etc/nginx/htpasswd已经存在，并且是想往里面去增加账号密码，则不要使用`-c`参
数，否则它重新创建一个文件，原来的记录会被刷掉。密码文件也可以放到其他路径下，只
要配置时配对即可。

## 配置nginx
我们需要在nginx的配置文件的location段增加以下的配置：
```nginx
auth_basic "Restricted";
auth_basic_user_file /etc/nginx/htpasswd;
```

以下是一个完整的例子：
```nginx
server {
    listen 9090;
    server_name prometheus;
    location / {
        proxy_pass http://prometheus;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_redirect off;
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/htpasswd;
    }
}
```
我使用nginx代理了prometheus的请求，然后屏蔽了prometheus默认的9090端口，使用nginx
进行转发，同样监听的也是9090端口。这样用户在浏览器上请求prometheus的9090时，就会
要求进行http basic认证，这样没有密码就看不到我们的数据了。


## 重新nginx服务
```sh
systemctl restart nginx
```


# 参考文章
- HTTP基本认证: https://zh.wikipedia.org/wiki/HTTP%E5%9F%BA%E6%9C%AC%E8%AE%A4%E8%AF%81
