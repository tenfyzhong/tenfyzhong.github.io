---
title: 编写fish-shell自定义补全
date: 2024-05-05T15:50:08+08:00
categories:
  - shell
tags:
  - shell
  - fish
keywords: shell,fish
---

fish shell的补全是最简单明了的，一个`complete`命令就能编写补全。
官方文档参考：
- [Writing your own completions](https://fishshell.com/docs/current/completions.html)
- [complete - edit command-specific tab-completions Synopsis](https://fishshell.com/docs/current/cmds/complete.html)

第1个文档说明怎么写补全，第二个文档说明`complete`命令的用法。

fish的补全，只需要用`complete`命令，一行行的把需要补全的选项声明出来即可。

补全声明放到与程序同名的fish文件中。最后把这个文件放到`$fish_complete_path`环境变量下的任意路径即可。

对于fish shell，我们可以以写插件的形式来编写我们的脚本和补全，最后用插件管理器安装即可。  
如使用[fisher](https://github.com/jorgebucaran/fisher)，我们建好Github工程，然后把补全放到`completions`目录下，上传到Github上后。再使用`fisher install username/repo`命令安装即可。fisher会把补全文件拷贝到`~/.config/fish/completions`目录。


# 例子dashdog说明
下面以[dashdog](https://github.com/tenfyzhong/dashdog/blob/main/cmd/dashdog/completions/dashdog.fish)这一个程序为例
```fish
complete -c dashdog -f
complete -c dashdog -r -F -s c -l config -d 'the config file to load'
complete -c dashdog -r -f -l log -a 'debug info warn error off' -d 'log level, the log will print to stdout'
complete -c dashdog -r -F -l path -d 'the path to generate docset'
complete -c dashdog -r -f -l name -d 'the name of the docset'
complete -c dashdog -r -f -l url -d 'the source url of the docset'
complete -c dashdog -r -f -l cfbundle -d 'the bundle of the root page'
complete -c dashdog -r -f -l path-regex -d 'the sub path which match the `pattern` will be able to generate'
complete -c dashdog -r -f -l bundle-pattern -d 'a `pattern` to match the path of the sub module name'
complete -c dashdog -r -f -l bundle-replace -d 'a `replace-pattern` to replace the path which matched by --bundle-pattern flag'
complete -c dashdog -s h -l help -d 'show help'
complete -c dashdog -s v -l version -d 'print the version'
```

`-c`参数说明是对dashdog这一个程序进行实例  
`-f`参数说明这个程序后面不以文件路径作为补全  
`-r`表示这个选项后，需要添加一个参数，`-F`表示这个参数添加的是文件路径的参数  
`-s`和`-l`表示的是知选项和长选项  
`-d`是这个补全选项的描述  

# 例子gg说明
上面的例子的实例都是选项。再用[gg](https://github.com/tenfyzhong/gg/blob/main/completions/gg.fish)来说明一下，这个例子说明了有子命令的情况。

```
complete -c gg -f
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a 'ls' -d 'list local version'
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a 'ls-remote' -d 'list remote version'
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a 'install' -d 'install specified version'
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a 'remove' -d 'remove specified version'
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a 'use' -d 'print the specified version environment'
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a '-h' -d 'show help message'
complete -c gg -f -n '! __fish_seen_subcommand_from ls ls-remote install remove use -h --help' -a '--help' -d 'show help message'
complete -c gg -f -n '__fish_seen_subcommand_from ls' -s h -l help -d 'show help message'
complete -c gg -f -n '__fish_seen_subcommand_from ls-remote' -s f -l force -d 'force to update cache'
complete -c gg -f -n '__fish_seen_subcommand_from ls-remote' -s h -l help -d 'show help message'
complete -c gg -f -n '__fish_seen_subcommand_from install' -s h -l help -d 'show help message'
complete -c gg -f -k -n '__fish_seen_subcommand_from install' -a "(__gg-ls-remote)"
complete -c gg -f -n '__fish_seen_subcommand_from remove' -s h -l help -d 'show help message'
complete -c gg -f -k -n '__fish_seen_subcommand_from remove' -a "(__gg-ls)"
complete -c gg -f -n '__fish_seen_subcommand_from use' -s b -l bash -d 'print the bash environment'
complete -c gg -f -n '__fish_seen_subcommand_from use' -s z -l zsh -d 'print the zsh environment'
complete -c gg -f -n '__fish_seen_subcommand_from use' -s f -l fish -d 'print the fish environment'
complete -c gg -f -n '__fish_seen_subcommand_from use' -s h -l help -d 'show help message'
complete -c gg -f -k -n '__fish_seen_subcommand_from use' -a "(__gg-ls)"
```

这个例子比较复杂的点在于子命令的处理。第2~8行，都使用了`-n`，并且还有`! __fish_seen_subcommand_from`。  
`-n`表示需要符合后面的条件才应用这一条规则，后面的参数就是条件。  
`__fish_seen_subcommand_from`是fish的一个自带函数，用来表示当前命令行的输入内容是否包含它的参数。`!`表示取非。fish自带了一堆函数，可以用来做补全，可以通过查看环境变量`$fish_function_path`来查看函数的路径，以及有哪些函数。  
第2~8行表示，没有对应的子合集或者没有`-h`,`--help`参数，则声明子命令。这样我们就可以把我们所有的子命令都声明出来了。  
第9行之后，还是使用了`-n`和`__fish_seen_subcommand_from`条件，不过这次没有取非，这样可以对对应的子命令的选项进行场景。一个子命令，还可以用多行场景。比如最后5行都是对use子命令的声明，其他的选项都是一样的。  
另外，最后一行还有一个`-a`选项，该选项列举补全列表，可以空格分配。

