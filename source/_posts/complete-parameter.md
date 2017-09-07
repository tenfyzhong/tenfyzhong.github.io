---
title: complete_parameter
date: 2017-09-02 12:18:51
categories: vim
tags: 
  - vim
  - plugin
---

YouCompleteMe给vim做补全非常方便，但是补全出函数后，却不会补全上参数。这是一个
辅助YouCompleteMe、deoplete、neocomplete补全插件进行补全参数的插件。

<!-- more -->

# 前言
YouCompleteMe给vim做补全非常方便，但是补全出函数后，却不会补全上参数。这是一个
辅助YouCompleteMe、deoplete、neocomplete补全插件进行补全参数的插件。从此函数补
全完后，再也不用跳去看声明参数要怎么填了。  
插件链接：[tenfyzhong/CompleteParameter.vim](https://github.com/tenfyzhong/CompleteParameter.vim)

# 只有补全引擎的vim
*注：以下所有的例子都以YouCompleteMe为例子，使用deoplete、neocomplete也是一样的。
并且以golang为例子，当然目前已经支持了多种语言，详细请看github上的README*  
字不重要，看下图：  
![](https://ws3.sinaimg.cn/large/006tNc79ly1fh44miqsf3g30hs0dcakz.gif)
ycm呼起了补全菜单，选中补全列表中的一项后，按左括号开始填参数。对于大的函数，
这时候就蒙圈了，忘了要填什么参数了。就只有跳到函数声明或者文档上去看参数，而且
经常是看了第一个，回来填好后，再去看第二个，如此循环。

# 参数补全闪亮登场
继续看图：  
![](https://ws2.sinaimg.cn/large/006tNc79ly1fh44mlv3nbg30hs0dch2f.gif)
还是ycm呼起了补全菜单，选中补全列表中的一项后，按左括号，形参的名字已经补全上来了，
并且这时使用选择模式选中了第一个参数，直接输入内容，当前选中的内容就会被删除，
而插入输入的内容。第一个参数填完后，按`<m-n>`(默认跳转到下一个参数的映射键)，
就跳到第二个参数，并且又进入了选择模式。修改完后，就可以继续按`<m-n>`跳到下一个
参数(如果没有下一个参数了，则会跳到右括号之后，并且进行插入模式)。  
当跳到下一个参数后发现上一个参数输错了，这时还可以通过`<m-p>`来跳回到上一个参数，
并且选择了它，又可以进行修改了。  
有时候调用函数，已经有了跟形参一样名字的变量了，这时候补全完之后，因为插入的形参
名字和变量名字一样，这时候就不用修改了。直接按`<m-n>`跳到下一个位置即可。  

## 已经支持的语言(截止到2017年7月1日)
- c
- c++
- golang
- python
- erlang
- javascript
- typescript
- rust
