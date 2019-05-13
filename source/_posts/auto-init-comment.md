---
title: 自动初始化gitalk/gitment评论
categories:
  - misc
tags:
  - hexo
date: 2018-11-15 20:18:58
keywords: hexo,gitalk,gitment
---

发表新文章后，使用travis的ci功能进行自动初始化评论功能。
<!-- more -->
使用gitalk或者gitment做hexo静态博客的评论功能，有一个很烦的问题是每次发表后，
都需要去点一下初始化评论。

使用[hexo博客push到github的后自动部署到github pages](/2017/09/08/hexo-auto-deploy/)方法发表文章后，
我们同样可以使用travis的能力来进行自动初始化评论功能。

自动部署需要依赖`sitemap.yml`

# 部署
## step 0 生成token
到[github setting](https://github.com/settings/tokens)页面申请Personal access tokens，
点击上面的Generate new token后，跳进去后，填好描述信息，同时勾上下面的选项：
![generate token](http://wx1.sinaimg.cn/mw690/69472223gy1fjc8b1a9knj20hz0gp76s.jpg)
生成好把token复制出来，它只会显示一次。
![token](http://wx1.sinaimg.cn/mw690/69472223gy1fjc8b1sxmtj20l406d3ze.jpg)

## step 1 编译自动初始化评论的工具
下载自动初始化评论的工具
`wget https://github.com/tenfyzhong/autoissue/releases/download/v0.1.1/autoissue-linux-x86 -O autoissue`

把autoissue移动到自己的博客bin目录下。

## step 2 配置travis构建的配置
在自己的博客repo上执行
`travis encrypt AUTH_TOKEN=xxxxxxxxx --add`，它就会自动往`.travis.yml`上添加好这个环境变量。

travis的命令使用参照[Encryption keys](https://docs.travis-ci.com/user/encryption-keys/)

在`.travis.yml`配置的script上执行`autoissue`，完整的配置如下
```yml
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
- git config user.name "tenfyzhong"
- git config user.email "tenfyzhong@qq.com"
- sed -i "s/https:\/\/\(github\.com\/tenfyzhong\/tenfyzhong\.github\.io\.git\)/https:\/\/$ACCESS_TOKEN@\1/" _config.yml
script:
- hexo clean
- hexo g
- hexo d
- ./bin/autoissue
env:
  global:
    secure:  # 已经删除
```

## step 3 配置评论使用的repo
需要在博客的`_config.yml`上添加以下的配置，对应于gitalk或者gitment的配置
```yml
owner: tenfyzhong
comment_repo: tenfyzhong.github.io # 对应于repo配置
labels: ["comment"]
sitemap:
  path: sitemap.xml
```

修改完后就可以直接推一篇文章上去看效果了。


# 对于自动生成评论的规则
`autoissue`工具会去拉一页issue，把这页issue里最旧的文章做基准，从hexo生成的sitemap.xml中做对比，
对于存在于sitemap.xml中的文章，比基准文章新，而且又不存在这一页issue中，则进行创建。
