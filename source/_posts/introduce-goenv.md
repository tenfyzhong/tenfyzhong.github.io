---
title: tenfyzhong/goenv库介绍
categories:
  - 后台
tags:
  - golang
date: 2017-10-17 18:57:26
keywords: go,golang,goenv,env
---

[goenv](https://github.com/tenfyzhong/goenv)库将环境变量的值设置到一个结构体里，
以方便使用。类似于encoding/json解析到结构体。

<!-- more -->

# 背景
为了简化docker的发布，把配置从配置文件里抽取出来，设置到环境变量里。然后发布docker
容器的时候就不需要再带一个配置文件了。

# 文档
goenv的使用非常简单，首先定义一个结构体，结构体里需要解析环境变时的字段，则使用
golang的tag机制，加上`` `env:"name"` ``的tag，再调用`Unmarshal`函数就可以直接解
析到结构体里了。

以下是一个例子：
```go
import "fmt"
import "github.com/tenfyzhong/goenv"

type Number struct {
	zero   int    `env:"zero"`
	One    int    `env:"one"`
	Two    int    `env:"two"`
	Three  bool   `env:"three"`
	Four   string `env:"four"`
	Five   string
	Six    *int8   `env:"six"`
	Sevent uint    `env:"sevent"`
	Eight  float32 `env:"eight"`
	Nine   bool    `env:"nine"`
	Ten    *bool   `env:"ten"`
}

func main() {
    n = &Number{}
    err := goenv.Unmarshal(n)
    if err == nil {
        fmt.Println(n)
    }
}
```

因为环境变量是扁平化的，所以只支持单级别的配置。目前支持以下的数据类型：
`bool, string, int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64, float32, float64`。

对于`bool`类型，如果环境变量没设，则为false，其他值都为true。

# 例子
```go
import "fmt"
import "github.com/tenfyzhong/goenv"

type Number struct {
	zero   int    `env:"zero"`
	One    int    `env:"one"`
	Two    int    `env:"two"`
	Three  bool   `env:"three"`
	Four   string `env:"four"`
	Five   string
	Six    *int8   `env:"six"`
	Sevent uint    `env:"sevent"`
	Eight  float32 `env:"eight"`
	Nine   bool    `env:"nine"`
	Ten    *bool   `env:"ten"`
}

func main() {
    n = &Number{}
    err := goenv.Unmarshal(n)
    if err == nil {
        fmt.Println(n)
    }
}
```
