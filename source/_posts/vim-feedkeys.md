---
title: vim函数feedkeys使用说明
date: 2017-09-02 17:42:23
categories:
tags:
---

很多人在使用feedkeys函数的时候会得取不预期的输出，怎么折腾也搞不明白为什么会得到
这样的结果。这篇文章来给大家解疑一下。

<!-- more -->

# feedkeys函数文档
```
feedkeys({string} [, {mode}])				*feedkeys()*
		Characters in {string} are queued for processing as if they
		come from a mapping or were typed by the user.
		By default the string is added to the end of the typeahead
		buffer, thus if a mapping is still being executed the
		characters come after them.  Use the 'i' flag to insert before
		other characters, they will be executed next, before any
		characters from a mapping.
		The function does not wait for processing of keys contained in
		{string}.
		To include special keys into {string}, use double-quotes
		and "\..." notation |expr-quote|. For example,
		feedkeys("\<CR>") simulates pressing of the <Enter> key. But
		feedkeys('\<CR>') pushes 5 characters.
		If {mode} is absent, keys are remapped.
		{mode} is a String, which can contain these character flags:
		'm'	Remap keys. This is default.
		'n'	Do not remap keys.
		't'	Handle keys as if typed; otherwise they are handled as
			if coming from a mapping.  This matters for undo,
			opening folds, etc.
		'i'	Insert the string instead of appending (see above).
		'x'	Execute commands until typeahead is empty.  This is
			similar to using ":normal!".  You can call feedkeys()
			several times without 'x' and then one time with 'x'
			(possibly with an empty {string}) to execute all the
			typeahead.  Note that when Vim ends in Insert mode it
			will behave as if <Esc> is typed, to avoid getting
			stuck, waiting for a character to be typed before the
			script continues.
		'!'	When used with 'x' will not end Insert mode. Can be
			used in a test when a timer is set to exit Insert mode
			a little later.  Useful for testing CursorHoldI.

		Return value is always 0.
```
说明文档说了这个函数的使用方式，但是对于大部分人，只理解了一部分，帮而会产生很多
不解的行为。这个函数会把参数中的`{string}`当前是用户输入的。默认的，它会把string
的内容放到预输入的buffer(下面直接引用说明文档中的typeahead buffer)中。  
对于不解行为，主要都是由这个typeahead buffer产生了。这个typeahead buffer并不是我
们所熟悉的vim与文档内容关联的buffer，下面会对它进行详细的说明。很多人认为，只要
一调用feedkeys，它就立刻产生作用。例如下面这个例子：  
```viml
function! Test1() 
    call feedkeys("a123\<ESC>", "n")
    call feedkeys("a456\<ESC>", "n")
endfunction
```
这个例子很明显，调用`Test1`后，会在当前的buffer(这个是大家所熟悉的与文档内容相关
的buffer，下面对于只出现buffer的都说的是这个buffer，而对于预输入buffer会使用
typeahead buffer)。  

我们再来看一个例子：  
```viml
function! Test2()
    normal! a123
    call feedkeys("a456\<ESC>", "n")
    normal! a789
endfunction
```
大家先猜想一下这个例子的输出。很多人理所当然地以为这个会输出`123456789`。然而，
它输出的却是`123789456`。`456`被移到后面去了。为什么会这样？下面来说一下typeahead
buffer。


# typeahead buffer
vim维护了一个typeahead buffer来用存放用户预输入的内容。然后vim从typeahead buffer
中取数据当成是用户输入数据进行处理。在用户没有输入，也没有函数执行的时候，这个时
候就会执行typeahead buffer里面的内容了。  
那么这个typeahead buffer的内容是怎么插进去的呢？  
- `normal`命令
- `@r`寄存器
- `abbreviate`的内容
- `feedkeys()`函数

所有插入到typeahead buffer的内容都调用了这个函数来进行插入(neovim源码)
```c
/*
   * insert a string in position 'offset' in the typeahead buffer (for "@r"
   * and ":normal" command, vgetorpeek() and check_termcode())
   *
   * If noremap is REMAP_YES, new string can be mapped again.
   * If noremap is REMAP_NONE, new string cannot be mapped again.
   * If noremap is REMAP_SKIP, fist char of new string cannot be mapped again,
   * but abbreviations are allowed.
   * If noremap is REMAP_SCRIPT, new string cannot be mapped again, except for
   *          script-local mappings.
   * If noremap is > 0, that many characters of the new string cannot be mapped.
   *
   * If nottyped is TRUE, the string does not return KeyTyped (don't use when
   * offset is non-zero!).
   *
   * If silent is true, cmd_silent is set when the characters are obtained.
   *
   * return FAIL for failure, OK otherwise
   */
int ins_typebuf(char_u *str, int noremap, int offset, int nottyped, bool silent)
```
将str插入到typeahead buffer中，插入的位置是offset。noremap由feedkeys中的`n`选项
控制。nottyped由feedkeys中的`t`选项控制。


## 以`normal`的方式说明typeahead buffer插入内容
去nvim中找取`normal`的源码  
```c
/*
* Execute normal mode command "cmd".
* "remap" can be REMAP_NONE or REMAP_YES.
*/
void exec_normal_cmd(char_u *cmd, int remap, bool silent)
{
  // Stuff the argument into the typeahead buffer.
  ins_typebuf(cmd, remap, 0, true, silent);
  exec_normal(false);
}

/// Execute normal_cmd() until there is no typeahead left.
///
/// @param was_typed whether or not something was typed
void exec_normal(bool was_typed)
{
  oparg_T oa;

  clear_oparg(&oa);
  finish_op = false;
  while ((!stuff_empty()
          || ((was_typed || !typebuf_typed())
              && typebuf.tb_len > 0))
         && !got_int) {
    update_topline_cursor();
    normal_cmd(&oa, true);      // execute a Normal mode cmd
  }
}
```
对于normal插入的内容，会插入到typeahead buffer的开头，并会立马就执行，一直到非
normal或者mapping。  
所以对于`Test2`的例子，它遇到`normal`会插入到typeahead buffer的开头，然后执行。
然后`feedkeys`插入新的内容到typeahead buffer，这时`typebuf_typed`是TRUE的。
然后又插入normal的`789`，当9插入完后，`typebuf_typed`又变成TRUE了。所以`feedkeys`
的内容会一直等到函数执行完等待用户输入内容的时候，才会进行执行。所以最后就出现了
`123789456`的结果了。


# `feedkeys`的选项`i`的作用
默认情况下，`feedkeys`所内容加到typeahead buffer的后面。当加上`i`这个选项的时候，
它会传0给`ins_typebuf`的`offset`字段。这时候就插在了开头。来个例子看一下效果。  
```viml
function! Test3()
    call feedkeys("a123\<ESC>", "n")
    call feedkeys("a456\<ESC>", "n")
    normal a789
endfunction
```
这个例子，没有`i`选项，毫无疑问这个的输出是`789123456`。  
下面这个例子加了`i`选项：  
```viml
function! Test4()
    call feedkeys("a123\<ESC>", "n")
    call feedkeys("a456\<ESC>", "in")
    normal a789
endfunction
```
这个的`456`插入到了123前面了。所以这个的输出是`789456123`
