---
title: Golang rpc服务更优雅的error处理和打印日志
date: 2024-05-31T00:01:36+08:00
categories:
  - "编程语言"
tags:
  - "golang"
  - "error-handling"
keywords: golang,error
---

服务器代码中，错误处理占据了大部分的逻辑。特别是C族语言，喜欢使用错误码，而不是异常来处理错误。
错误码比异常的优势是，性能会更好一些。抛出异常的话，因为有异常栈的展开，性能开销会大很多。
在Golang中，有一个error的接口来处理错误。

咱们先看看error的定义
```go
// The error built-in interface type is the conventional interface for
// representing an error condition, with the nil value representing no error.
type error interface {
	Error() string
}
```

非常简单的接口。只有一个`Error`的方法。只有定义了`Error`接口，我们的类实现了`error`接口了，就能当成`error`使用了。

在工程中，rpc服务基本会使用错误码来做记录错误原因，用来做服务间的错误交互。在服务内的时候，可能会我们在底层的函数就知道是什么原因，而设置了错误码。接下来，我们会把这个错误码一层层返回，到最外层的rpc返回。

# 定义我们服务内的error交互

^081571

接下来，我们需要定义一个自定义的`CustomError`类，实现`error`接口。
```go
type CustomError struct {
	errno int32
	msg   string
}

func (e CustomError) Error() string {
	return fmt.Sprintf("errno:%d msg:%s", e.errno, e.msg)
}

func (e CustomError) Errno() int32 {
	return e.errno
}

func (e CustomError) Msg() string {
	return e.msg
}

func NewCustomError(errno int32, msg string) *CustomError {
	return &CustomError {
		errno: errno,
		msg: msg,
	}
}
```

有了这个这个类之后，所有使用`error`接口的地方，都可以用这个类的实现来进行返回了。

比如以下的函数调用
```go
const (
	errnoBar = 1001
	errnoFoo = 1002
)

func bar() error {
	return NewCustomError(errnoBar, "this is an error")
}

func foo() error {
	return bar()
}
```

基于以上，我们就可以在函数间调用使用错误了。


# 定义一个rpc交互的异常结构
为了让我们的错误及错误码通透给rpc的主调方。我们需要使用我们的应用协议定义我们自己的错误结果。下面使用protobuf为例，定义一个错误结构，以及一个rpc方法的请求响应协议。

```protobuf
message Error {
	int32 errno = 1;
	string msg  = 2;
}

message FooRequest {
	int32 hello = 1;
}

message FooResponse {
	Error error = 1;
}
```

这样我们出错的时候，就可以把错误码和错误信息填到`Error`结构里进行返回了。

# 协议的Error与CustomError的桥梁
在上两节，我们已经定义好服务内和服务间使用的错误结构了。但是，这两个结构需要能够配合使用。这两个错误的转换，应该存在于rpc接口处理的最后，返回之前，这时我们需要把`error`转成protobuf的`Error`

```go
const (
	errnoUnknown = 999999
)

func BuildError(err error) *Error { // 这个Error是protobuf生成的结构
    if err == nil {
	    return &Error {
		    Errno: 0,
		    Msg: "success",
	    }
    }
	switch serr := err.(type) {
	case *CustomError:
		return &Error {
			Errno: serr.Errno(),
			Msg: serr.Msg(),
		}
	default:
		return &Error {
			Errno: errnoUnknown,
			Msg: "unknown error",
		}
	}
}
```

基于以上，我们的服务内以及服务间的的错误就能互通了。

# 还存在哪些问题
以上处理可以满足我们的服务使用了。但是还存在一个比较大的问题，出错后，我们需要根据错误来进行排查问题。以上的方式虽然能传递错误，但是却不知道哪里出错了，当然这需要我们配合日志系统来使用，日志我们在最后聊。
为了方便我们追踪哪里出问题了，我们需要把调用栈打印的日志了。所以这一节，我们聊聊怎么更好的去处理我们的调用栈。

在这一节，我们需要使用[pkg/errors](github.com/pkg/errors)这一个包进行处理我们的错误，让我们的错误可以包含调用栈信息。

## `pkg/errors` 的几个基本方法
我们来看看几个我们主要用的几个方法
### `WithStack`
```go
func WithStack(err error) error
```
把调用栈包到`error`里

### `wrap`和`wrapf`
```go
func Wrap(err error, message string) error
func Wrapf(err error, format string, args ...interface{}) error
```
这两个方法除了可以把调用栈包到`error`里，还能附加上一些自定义的信息。这两个方法基本是差不多的。只是`wrapf`可以像其他`printf`函数一样进行格式化信息。

另外，对于一个函数内的参数，可以通过`wrap`把它加到错误上，这样我们打印日志的时候会带出来，方便我们排查问题。

### `Cause`
`Cause`方法可以获取出最原始的`error`

## `pkg/errors`怎么使用
在[[Golang rpc服务更优雅的error处理#^081571]]这一章，我们已经能在服务内的函数间传递错误了。这一章节，我们来看看怎么调用栈给包上去。
### 包上调用栈
在上面一章，我们知道使用`pkg/errors`可以给`error`接口包上调用栈了。所以我们只要用对应的方法就行。在我们的工程中，我们碰到error，可能并不知道是要设置一个新的`CustomError`，还是直接把这个error抛出去。所以我们只需要在我们关心的错误地方设置`CustomError`，其他地方只要往包抛就行。为了让错误包含调用栈，我们只需要无脑的去用`pkg/errors`来`Wrap`或者`WithStack`就行。例如以下的例子
```go
const (
	errnoBar = 1001
	errnoFoo = 1002
)

func bar() error {
	err := NewCustomError(errnoBar, "this is an error")
	return errors.WithStack(err)
}

func foo() error {
	err := bar()
	return errors.Wrapf(err, "got an error when calling bar")
}

func hello() error {
	err := foo()
	return errors.Wrapf(err, "got an error when calling foo)
}
```

### 对`pkg/errors`包过的error设置到protobuf的`Error`结构
```go
const (
	errnoUnknown = 999999
)

func BuildError(err error) *Error { // 这个Error是protobuf生成的结构
    if err == nil {
	    return &Error {
		    Errno: 0,
		    Msg: "success",
	    }
    }
    // TODO Print error log
    err = errors.Cause(err)

	switch serr := err.(type) {
	case *CustomError:
		return &Error {
			Errno: serr.Errno(),
			Msg: serr.Msg(),
		}
	default:
		return &Error {
			Errno: errnoUnknown,
			Msg: "unknown error",
		}
	}
}
```
在我们需要构建`Error`的地方，只需要用`Cause`把原始的`error`提取出来，即可做我们的类型判断处理了。

# 错误日志
以上章节完成后，我们就能很好的传递错误，以及在错误中包含调用栈了。接下来，我们要看看错误日志的打印。
对于错误日志，我们应该本着一个原则`要么打印日志，要么返回错误，不要同时执行两个动作`。如果我们在拿到错误的地方都打印日志，那我们的日志系统会有非常多重复的日志，会影响我们排查问题。
所以，我们不应该在所有错误的地方都打印日志。当然，如果出错了，可能是非关键路径，不返回错误，这时候我们需要打印一个日志，以便在日志系统上体现方便排查。级别可以是`Error`或者`Warn`级别。
因为我们的错误包含了调用栈信息，所以我们只需要在最外层错误打印错误日志即可，在日志上我们可以根据栈信息来排查问题。
假如打印日志的函数声明如下：
```go
package log
func Error(format string, args ...interface)
```
那我们打印错误日志如下，需要使用`%+v`来格式化`err`
```go
log.Error("got some error, %+v", err)
```

比如我们上面定义的`Foo`rpc调用
```go
func Foo(ctx context.Context, req *FooRequest) *FooResponse {
	err := handle(ctx, req)
	if err != nil {
		log.Error("handle foo get some error, req:%+v, err:%+v", req, err)
	}
	resp := &FooResponse{
		Error: BuildError(err),
	}
}
```
