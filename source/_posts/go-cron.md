---
title: golang定时任务cron
date: 2017-09-15 20:36:38
categories: 后台
tags: go
keywords: 
  - go
  - cron
---

做后台经常会要写一些定时任务，让它定时执行。一般我们都会使用unix/linux自带cron
来做这个工作。但是cron有时并不是那么友好。比如：  
1. 时间粒度大，最小的粒度是分钟级的，而且你不能确保在一分钟内的第几秒执行任务。
1. 每次任务都是开启新一个进程，开销大。
1. 如果任务没有执行时，我们不好做监控。
1. 不好锁定资源，因为每次都是一个新进程，但是有时我们的任务不能多个实例同时进行。

对于golang，我们可以使用[cron][]来完成任务，而且可以解决以上的问题。

<!-- more -->
# unix/linux的cron
## cron的用法
cron的使用非常简单，它对每个用户都维护了一个任务列表，存在每个用户的crontab中。
使用`crontab -l`就可以当查看用户的任务列表。使用`crontab -e`可以编辑用户的任务。

执行`crontab -e`后，编辑器会打开当前用户的任务文件，每行是一个定时任务。每行的
内容由5个时间域和一个命令域组成。每个域都是用空格分隔，但是最后的命令域内部可以
存在空格。比如：`* * * * * rm -f /var/hello/*.log`，这个定时任务是每分钟去删除
`/var/hello`目录下的所有log文件。

## crontab里的域介绍
crontab每行的内容如下：  
`minute hour day_of_month month day_of_week command`  
minute为分钟，值范围为[0, 59]  
hour为小时，值范围为[0, 23]  
day_of_month为每月的第几天，值范围为[0, 31]  
month为月份，值范围为[1, 12]  
day_of_week为星期几，值范围为[0, 7]，其中0和7都代表星期日  
command为任务的命令  
要注意命令的用到的所有路径都不能是相对路径，不然系统会找不到。除了内建命令，
命令也必须使用绝对路径，因为cron执行的时候并不会去加载你的PATH。  

时间域里可以用`*`来代表所有的值，也可以用`*/n`(其中n为一个数字)来表示每n个时间
单位执行一次。如果是minute域，则表示每n分钟执行一次，如果是hour域表示每n个小时
执行一次。以此类推。
如果对应的域指定一个特定的数字，则表示在特定的这个时间值执行，多个时间值可以用
逗号分隔开，也可以用`-`来表示连接一个起始和结束的时间，比如：  
`*/5 1,2 1-6 * * rm -f /var/hello/*.log`  
这个任务表示每月的1到6号，1点和2点，每5分钟去删除一次`/var/hello/`下的log文件。  

## cron的不足
在文章开头的简介已经说明了cron的不足。  
但是它可以给我们非常方便的安排一些简单的任务。


# golang的cron包
## 简介
对于要进行精确控制的任务，我们可以使用golang的[cron][]包来完成。因为需要编码来完
完成任务，所以我们可以在代码里做更多的控制，比如监控任务的执行，对资源加锁以避免
任务的多个实例同时执行。另外它还可以运行秒级的时间粒度。  

先来上一个简单的例子：
```go
package main

import (
    "fmt"
    "os"
    "os/signal"
    "sync"
    "time"

    "github.com/robfig/cron"
)

var jobMutex = &sync.Mutex{}

func main() {
    c := cron.New()
    c.AddFunc("* * * * * *", func() {
        jobMutex.Lock()
        defer jobMutex.Unlock()
        fmt.Println("hello world")
        time.Sleep(3 * time.Second)
        fmt.Println("finish")
    })

    c.Start()

    sigChan := make(chan os.Signal)
    signal.Notify(sigChan, os.Interrupt)
    <-sigChan

    c.Stop()
}
```
这个例子每秒钟执行一次任务函数，然后输出`hello world`，完了之后输出`finish`。
可以看AddFunc的第一个参数传了6个`*`号，这6个星号都是时间域，它比系统的cron多了一
个秒域，其中第1个域就是秒域，其他用法跟系统的cron一样。第二个参数是一个func对象，
每次任务触发时，都会调用这个函数。而在这个例子中，首先先去获取了锁，在函数结束
后再释放锁，这样就可以确保了只有一个任务的实例在运行。

## 使用方法
golang的这个cron包使用非常简单，只要`New`一个`Cron`对象后，然后调用`AddFunc`添加
任务，最后执行`Start`就可以执行了。

整个过程我们要关心的就是`AddFunc`了，因为它才是我们添加任务的入口。它的声明如下：
```go
func (c *Cron) AddFunc(spec string, cmd func()) error
```
第一个参数是像系统的crontab里一致的时间域，只是多了一个秒域，每二个参数是要很执
行的任务函数。
对于6个时间域的组成如下：  

| Field name   | Mandatory? | Allowed values  | Allowed special characters |
|--------------|------------|-----------------|----------------------------|
| Seconds      | Yes        | 0-59            | * / , -                    |
| Minutes      | Yes        | 0-59            | * / , -                    |
| Hours        | Yes        | 0-23            | * / , -                    |
| Day of month | Yes        | 1-31            | * / , - ?                  |
| Month        | Yes        | 1-12 or JAN-DEC | * / , -                    |
| Day of week  | Yes        | 0-6 or SUN-SAT  | * / , - ?                  |

对于`Day of month`和`Day of week`可以填`?`表示留空，与`*`号的效果一致。

另外对于包里还预定义了以下的时间可以直接填到spec参数

| Entry                  | Description                                | Equivalent To |
|------------------------|--------------------------------------------|---------------|
| @yearly (or @annually) | Run once a year, midnight, Jan. 1st        | 0 0 0 1 1 *   |
| @monthly               | Run once a month, midnight, first of month | 0 0 0 1 * *   |
| @weekly                | Run once a week, midnight on Sunday        | 0 0 0 * * 0   |
| @daily (or @midnight)  | Run once a day, midnight                   | 0 0 0 * * *   |
| @hourly                | Run once an hour, beginning of hour        | 0 0 * * * *   |

上面简介的例子就已经是整个cron包的使用方法了，只要把时间和任务函数改掉就好了。


[cron]: https://github.com/robfig/cron
