---
title: comm-用于做文件比较
date: 2024-05-30T11:41:05+08:00
categories:
  - "工具"
tags:
  - "comm"
  - "cli"
  - "tools"
keywords: 工具,comm
---
# comm工具
comm工具的主要用途是用来做文件的差集、交集。
工作中，对账是一个频繁的工作项。基本上几十行的数据，人眼就看不过来了。所以使用工具是我们最好的方案。
comm可以为我们很方便的对两个文件做差集、交集。所以我们只要把数据洗成一样的格式后，就可以用comm进行对比了。

comm处理的文件必须先排好序，所以我们得先用sort工具对文件排好序。

comm帮忙信息如下：
```
Usage: comm [OPTION]... FILE1 FILE2
Compare sorted files FILE1 and FILE2 line by line.

When FILE1 or FILE2 (not both) is -, read standard input.

With no options, produce three-column output.  Column one contains
lines unique to FILE1, column two contains lines unique to FILE2,
and column three contains lines common to both files.

  -1                      suppress column 1 (lines unique to FILE1)
  -2                      suppress column 2 (lines unique to FILE2)
  -3                      suppress column 3 (lines that appear in both files)

      --check-order       check that the input is correctly sorted, even
                            if all input lines are pairable
      --nocheck-order     do not check that the input is correctly sorted
      --output-delimiter=STR  separate columns with STR
      --total             output a summary
  -z, --zero-terminated   line delimiter is NUL, not newline
      --help        display this help and exit
      --version     output version information and exit

Note, comparisons honor the rules specified by 'LC_COLLATE'.

Examples:
  comm -12 file1 file2  Print only lines present in both file1 and file2.
  comm -3 file1 file2  Print lines in file1 not in file2, and vice versa.

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Full documentation <https://www.gnu.org/software/coreutils/comm>
or available locally via: info '(coreutils) comm invocation'

```

# 输出说明
不带选项的comm命令，会打印三列内容。以`\t`来缩进，用于区分列。
- 第1列为只出现在第1个文件的行
- 第2列为只出现在第2个文件的行
- 第3列为同时出现在两个文件的行


# 选项说明
我们主要使用以下三个选项
- `-1` 抑制第1列，即不打印只出现在第1个文件的行
- `-2` 抑制第2列，即不打印只出现在第2个文件的行
- `-3` 抑制第3列，即不打印第1、2个文件交集的行

基于这三个选项组合，就可以做出差集交集的用法。

## file1-file2的差集
说明需要用只出现在第1个文件的行。我们只要抑制第2、3列即可。
例如如下
```bash
comm -23 file1 file2
comm -13 file2 file1
```

## file1-file2和file2-file1的差集
这样我们只需要取现只出现在第1个文件的行或者只出现在第2个文件的行。我们只要抑制第3列好可
```bash
comm -3 file1 file2
```

## file1&file2的交集
这个其实只需要打印第3列即可。我们需要抑制第1、2列
```bash
comm -12 file1 file2
```

# 安装

comm命令包含在coreutils这个包
在mac下，需要安装
```bash
brew install coreutils
```
