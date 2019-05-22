---
title: hexo博客push到github的后自动部署到github pages
date: 2017-09-08 11:10:36
categories: misc
tags: hexo
keywords: hexo
---

博文写好完，每次除了要把它push到存储博文的仓库，还要执行`hexo d`才能部署到github 
pages。人都是懒惰的，多执行一个命令都懒。不信的话，按以下设置好后，就再也不想执行
`hexo d`了。

<!-- more -->

需要自动能自动部署，就要push完毕后，能被监听到，并且执行一系列部署命令。travis
正好可以做这样的动作。

准备好了就开始吧。

## step 0 生成token
到[github setting](https://github.com/settings/tokens)页面申请Personal access tokens，
点击上面的Generate new token后，跳进去后，填好描述信息，同时勾上下面的选项：
![generate token](https://tenfy.cn/picture/generate-github-token.jpg)
生成好把token复制出来，它只会显示一次。
![token](https://tenfy.cn/picture/copy-github-token.jpg)

## step 1 配置travis
登录[travis](https://travis-ci.org/)，然后用github登录后，找到你的存储博文工程点
开。比如我的是：`tenfyzhong.github.io`，我把博文存在source分支，部署的静态页面放
在master分支，这样就可以把它们放在一起了。
![turn on](https://tenfy.cn/picture/enable-travis.jpg)

然后点旁边的启轮进入设置页面，可以把pull request的building给关了。如果你跟我一样
把博文跟静态页面放在同一个工程，则需要把`Build only if .travis.yml is present`打
开。不然一提交，就会给master部署，然后又会触发一次失败的构建。

在Environment Variables下面的输入框里添加一个环境变量，Name填`ACCESS_TOKEN`，
Value填上面申请到的token。
![travis setting](https://tenfy.cn/picture/set-access-token.jpg)

## step 2 配置travis构建的配置
```yaml
language: node_js
cache:
   directories:
   - node_modules

install:
  - nvm install 8.4.0
  - nvm use 8.4.0
  - node --version
  - npm install -g npm@5.3.0
  - npm install -g hexo-cli
  - npm install

before_script:
  - git submodule update --init --recursive
  - sed -i "s/https:\/\/\(github\.com\/tenfyzhong\/tenfyzhong\.github\.io\.git\)/https:\/\/$ACCESS_TOKEN@\1/" _config.yml

script:
  - hexo clean
  - hexo g
  - hexo d
```
在博文的根目录新建一个.travis.yml文件，添加以上的内容。要把上面第16行的tenfyzhong
改成你的名字。这一行的意思就是把你的_config.yml里面deploy里的部署链接加上上面申请
到的token。这样在travis的主机上push到你的工程时就不用密码了。

完了之后，把.travis.yml添加到版本库里，然后push，就可以上[travis](https://travis-ci.org)
上看结果了。

