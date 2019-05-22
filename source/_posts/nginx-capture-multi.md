---
title: nginx旁路
date: 2017-09-22 17:50:16
categories: 后台
tags: nginx
keywords: nginx
---

旁路的目的是为了把请求复制一份发到另外的服务上去。这样就可以不影响主流程的情况下
处理额外的逻辑了。最简单的方式就是让nginx把请求发出去，这样我们只要改配置就行了，
而不用改代码。相对于开发，测试回归的成本往往要高很多。

<!-- more -->

# 技术方案
1. nginx收到请求后，把请求发到主流程的服务A上去
1. 同步把请求旁路发到服务B上去
1. 等待A和B回包
1. 响应客户端

标准的nginx是不支持旁路的，我们用[lua-nginx-module][]模块，通过lua来控制多发多收。

正常的流程应该是这样的
![](https://tenfy.cn/picture/nginx-capture-single.jpg)
1. nginx收到请求
1. nginx把请求发到server A
1. nginx收到server A的回包
1. nginx回包给客户端

加上旁路后，流程变成了这样
![](https://tenfy.cn/picture/nginx-capture-multi.jpg)
1. nginx收到请求
1. nginx把请求发给server A
1. nginx把请求发给server B
1. nginx收到server A的回包
1. nginx收到server B的回包
1. nginx回包给客户端
对于A和B的回包，我们并不能决定顺序，因为server B的处理和网络比server A的快，所以
B可能会先回包。这是一种比较理想的情况。所谓旁路，它就不应该影响我们的正常业务流
程。所以，最理想的情况应该是对于server B，只发不收，收到A的回包后，我们就直接回
包给客户端。但是nginx并不支持这样的处理。

# 测试
以下是配置
```nginx
events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;

    upstream route0 {
        server route0:8080;
    }
    upstream route1 {
        server route1:8080;
    }
    server {
        listen       8080;
        server_name  localhost;

        location /route0{
            rewrite ^/route0(.*)$ $1 break;
            proxy_pass http://route0;
        }
        location /route1{
            proxy_connect_timeout 100ms; 
            proxy_read_timeout 100ms; 
            proxy_send_timeout 100ms;
            rewrite ^/route1(.*)$ $1 break;
            proxy_pass http://route1;
        }
        location / {
            content_by_lua '
                local route0, route1, action
                action = ngx.var.request_method

                if action == "POST" then
                    ngx.req.read_body()
                        local data = ngx.req.get_body_data()
                        arry = {method = ngx.HTTP_POST, body = data}
                else
                    arry = {method = ngx.HTTP_GET}
                end

                route0, route1 = ngx.location.capture_multi {
                    { "/route0" .. ngx.var.request_uri, arry},
                    { "/route1" .. ngx.var.request_uri, arry},
                }

                ngx.status = route0.status
                ngx.say(route0.body)
                    ';
        }
    }
}
```

我们监听8080的端口，然后代理转发到route0:8080和route1:8080上去，然后route0和
route1的回包。

对于route1的旁路，我们限制了proxy_connect_timeout, proxy_read_timeout, 
proxy_send_timeout的超时都为100ms，这样即使旁路的处理非常慢，也不会对我们主流程
产生较大的影响。


另外用go写了一个hello world的http server，配置了旁路，链接：https://github.com/tenfyzhong/nginx-capture-multi



[lua-nginx-module]: https://github.com/openresty/lua-nginx-module
