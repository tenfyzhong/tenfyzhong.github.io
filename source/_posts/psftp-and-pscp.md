---
title: psftp,pscp自动与服务器进行sftp,scp通信python库
date: 2017-09-04 20:32:34
categories:
  - 后台
tags:
  - python
keywords: python,psftp,pscp,pexpect,pssh
---

懒是程序猿的本性。一切重复的东西，程序猿都可以写成脚本来让它自己运行。很多时候程
序猿要写脚本去连到服务器上去执行些命令，其中还包含上传文件到服务器或者从服务器上
下载文件下来。

<!-- more -->

Python很适合用于做后台和运维等。于是乎，很多自动化脚本都用了python来写。对于要进
交互的自动化脚本，python有一个很强大的包pexpect。它可以捕捉输出，匹配输出之后，发
送交互内容过去。比如ssh连接到某台服务器，执行一系列命令后退出。那么这时候，ssh连
进行输入密码，连上去之后，输入一条命令，等待执行完，输入另一条命令，等待执行完，如
此重复。

但是，捕捉输出是非常烦的事情，比如ssh的连接，有可能会提醒输入密码，也有可能会提醒
你把服务器地址保存到known_hosts里面等。每次写脚本时都要做这些重复的工作，于是程序
猿又发挥了他懒的天性，于是乎又有了pxssh，基于pexpect，完成了登录，捕捉命令行的
PROMPT捕捉等。

对于要与服务器进行文件上传下载，要用到scp或者sftp了。对于这两个程序，跟ssh是同一
系统的程序，命令过程基本完全一致。但是却没有这两个程序的封装。于是乎，就有了psftp
和pscp。

pxssh是pexpect库自带的，而psftp和pscp是我自己写的，为了是跟pxssh一样的目的，不要
让那些登录的烦着猿。

# [pscp][]
首先简介简单的pscp。pscp基本scp程序，scp非常简单，类似于cp，它把文件copy到服务器，
或者从服务器copy到本地，然后它就结束了。所以pscp命令也非常简单，它只要完成自动
登录，然后捕捉结束就行了。所以它的核心只有两个函数和一个构造函数：
```python
def __init__(
        self,
        timeout=60,
        maxread=100,
        searchwindowsize=None,
        logfile=None,
        cwd=None,
        env=None,
        ignore_sighup=True,
        echo=True,
        options={},
        encoding=None,
        codec_errors='strict')

# 上传到服务器
def to_server(
            self,
            src,
            dst,
            server,
            username,
            password='',
            terminal_type='ansi',
            timeout=10,
            port=None,
            ssh_key=None,
            quiet=True,
            check_local_ip=True)

# 从服务器下载
def from_server(
            self,
            src,
            dst,
            server,
            username,
            password='',
            terminal_type='ansi',
            timeout=10,
            port=None,
            ssh_key=None,
            quiet=True,
            check_local_ip=True)
```

大部分参数都是默认参数来的。下面是一个例子：
```python
import pscp
import getpass
s = pscp.pscp()
src = raw_input('src: ')
dst = raw_input('dst: ')
hostname = raw_input('hostname: ')
username = raw_input('username: ')
password = getpass.getpass('password: ')
try:
    s.to_server(src, dst, hostname, username, password)
except:
    pass
```


# [psftp][]
psftp比pscp多了一些命令，可以进行交互，在*nix上可以用`man sftp`可以看到它有的命令。
对于写脚本进行自动化，主要用到以下的一些命令:  
- `get` 下载到本地
- `put` 上传到服务器
- `cd` cd到服务器上的目录
- `lcd` cd本地的目录

这个定义了命令一样名字的函数，并进行了捕捉PROMPT，所以只有简单的像命令一样使用就
可以了。比如：
```python
import psftp
import getpass
try:
    s = psftp.psftp()
    hostname = raw_input('hostname: ')
    username = raw_input('username: ')
    password = getpass.getpass('password: ')
    s.login(hostname, username, password)
    print s.pwd()
    print s.lpwd()
    print s.lls()
    print s.ls()
    s.put('./hello.txt')
    print s.ls()
except:
    pass
```


具体文档可以clone repo下来用浏览器打开docs下的文档文件。


[pscp]: https://github.com/tenfyzhong/pscp
[psftp]: https://github.com/tenfyzhong/psftp
