---
title: 给dash生成doc文档
date: 2024-05-03T11:57:04+08:00
categories:
  - "工具"
tags:
  - "dash"
  - "dashdog"
  - "docset"
  - "tutorial"
keywords: 工具,dash,dashdog
---

本文介绍[dash](https://kapeli.com/dash)如何生成文档以及文档生成工具dashdog的使用。

<!-- more -->

# dash文档生成指引
官方提供了文档的生成指引方式[Docset Generation Guide](https://kapeli.com/docsets#dashDocset)，但是在使用的过程发发现官方指引已经落后了，使用了dash 7下载了一个go的三方文档，并且去看了一下SQLite里的数据。
发现里面的格式跟文档提供的不一样。

这一章，主要基于我在研发dashdog工具的时候，基于dash 7下载的文档进行分析总结出来的文档生成指引。

以下为每一步的指引，部分引用原官方指引文档。

## 1.创建docset目录
首先创建docset目录，以`<docset name>.docset`为文档根目录。dash导入的时候，也是导入的这个目录。

```bash
mkdir -p <docset name>.docset/Contents/Resources/Documents/
```

## 2.下载html和资源
把html以及html里引用的资源都下载我们上面创建的目录下。
```
<docset name>.docset/Contents/Resources/Documents/
```

以该目录做为根目录，对资源文件进行组织。

比如`https://https://pkg.go.dev/github.com/pkg/errors`下载到`<docset name>.docset/Contents/Resources/Documents`目录下。

修改html文件里的href和src的路径，改以基于当前文件的相对路径。如果没有下载下来的资源，可以保留原有的url，但是这样的跳到对应的线上去，而不是本地资源。

## 3.创建Info.plist文件
下载[Info.plist](https://kapeli.com/resources/Info.plist)模板，修改里面对应的内容。

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>{{.CFBundleIdentifier}}</string>
	<key>CFBundleName</key>
	<string>{{.CFBundleName}}</string>
	<key>DocSetPlatformFamily</key>
	<string>{{.DocSetPlatformFamily}}</string>
	<key>dashIndexFilePath</key>
	<string>{{.DashIndexFilePath}}</string>
	<key>isDashDocset</key>
	<true/>
	<key>isJavaScriptEnabled</key>
	<true />
	<key>DashDocSetDefaultFTSEnabled</key>
	<true/>
</dict>
</plist>
```

官方的文档内容不全，但是在官方的指引上有其他的项，可以添加上去。以上是我实现的过程中使用的所以内容。

1. `CFBundleIdentifier`用于搜索关键字，于go来说是`godoc`
2. `CFBundleName`是包名，在dash上显示
3. `DocSetPlatformFamily`于go来说也是`godoc`
4. `dashIndexFilePath`主html文件的路径
5. `isJavaScriptEnabled`是否允许js脚本
6. `DashDocSetDefaultFTSEnabled`是否开启全文索引

## 4.创建SQLite表和索引
dash使用SQLite来存储锚点和关键字的数据，搜索的时候可以进行跳到对应的锚点。SQLite的表和索引如下：
```sql
CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);
CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);
```

SQLite文件存储位置
```
<docset name>.docset/Contents/Resources/docSet.dsidx
```

## 5.生成索引表数据
生成的数据插入数据库，sql如下：
```sql
INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('name', 'type', 'path');
```

- `name`为要索引的关键字
- `type`为类型，可以通过官网指引 https://kapeli.com/docsets#supportedentrytypes
- `path`的该关键字要跳过去的锚点位置，在dash上，基本上使用自定义的锚点，参考[第6节](#6.生成TOC)

## 6.生成TOC
toc的内容如下图，官方说明[dash toc](https://kapeli.com/dash_guide#tableOfContents)

![dash-table](https://tenfy.cn/picture/dash-table.png)

官方文档的TOC格式已经落后，最新的TOC格式如下：
```html
<a name="//dash_ref_<NAME>/<TYPE>/<NAME>/<LEVEL>" class="dashAnchor"></a>
```
其中NAME, TYPE跟第5节对应。
LEVEL对应为以为0开始的级别。在TOC中最叶子层为0，上一层为1，跟我们写html或者markdown的级别刚好相反。
该节点插入到文档的锚点位置上。

另外，还需要插入一个`<link>`节点到html的`<head>`节点上。内容如下:
```html
<link name="//dash_ref_<NAME>/<TYPE>/<NAME>/<LEVEL>" />
```
内容跟锚点一样。

再回到第5节的`path`内容，格式如下：
```
<dash_entry_name=NAME><dash_entry_originalName=BUNDLE_NAME.NAME><dash_entry_menuDescription=BUNDLE_NAME>HTML_FILE#//dash_ref_NAME/TYPE/NAME/LEVEL>
```

我们生成的TOC内容主要与`<head>`里的`<link>`的顺序一致。另外，对于数据库里的数据，我们应该只插入叶子节点，也就是LEVEL为0的节点。高层节点不用插入数据库。

## 7.总结
总结一下我们的生成思路。

我们创建好目录后，下载html内容，然后解析内容，对里面的资源也下载下来，放到对应的目录，然后把资源的地址改成相对路径。
解析我们需要处理的关键字，然后在关键字节点上插入锚点。
在`<head>`节点上插入我们对应的`<link>`节点。
把叶子节点的锚点信息写入数据库。

如果我们还需要解析html的子页面，我们需要使用dfs，处理完子页面后，把节点的路径改成相对路径。

# dashdog的使用
dash提供了制作文档的方法(https://kapeli.com/docsets#dashDocset)，并且有挺多人写了相关的工具。甚至官方文档还推荐了两个对html生成文档的方法。但是研究下来，发现它们并不好用，而且达不到我要的预期。

我想要的特性
- 对在线html文档生成离线文档
- 只需要配置，就能跑，不需要我重新写代码(因为写新的代码就意味着我投入测试的时间成本)
- 可单独运行，无三方依赖，方便写脚本进行批量下载，以便电脑迁移时可以方便下载

| 特性       | dashing  | dash-docset-builder |
|------------|----------|---------------------|
| 文档数据源 | 本地html | 线上网页            |
| 配置       | json配置 | 编写php代码         |
| 可单独运行 | 支持     | 依赖php环境         |


基于以上需要的特性，我开发了[dashdog](https://github.com/tenfyzhong/dashdog)

整体的开发思路与[dash文档生成指引](#dash文档生成指引)一致。

## 安装
可以下载go代码进行编译，建议使用brew进行安装。命令如下：
```bash
brew install tenfyzhong/tap/dashdog
```

## 使用说明
dashdog使用yml配置，模板可以参考[pkg.go.dev.yml](`https://github.com/tenfyzhong/dashdog/blob/main/conf/pkg.go.dev.yml`)。该模板是对go文档进行解析生成。文档有注释。

工具同时对一些简单的配置提供了命令行参数的方式。因为对于同类型的文档，选择器之类的操作都是一致的。这样我们通过提供名字、url这些参数就能下载同站的不同包文档。

另外，对于go，还提供了一个`dashdog-go`的脚本，用于下载go的文档。只需要使用`-p`参数指定go的包名，就会下载生成对应包的文档。
```
dashdog-go -p pkg-name
```

dashdog的文档默认生成到`~/Documents/dashdog-doc`目录下。

生成后，在dash中导入即可。另外，如果文档重新生成，需要重启dash来重新加载。

## 分析文档选择节点
dashdog最复杂的部分是选择节点进行索引、删除、设置属性等操作。

dashdog使用css选择器进行选择节点，css选择器比较简单，可以参考[CSS 选择器参考手册](https://www.w3school.com.cn/cssref/css_selectors.asp)

我们以golang的文档来分析一下
```html
<h4 tabindex="-1" id="Assertions" data-kind="type" class="Documentation-typeHeader">

<h4 tabindex="-1" id="CallerInfo" data-kind="function" class="Documentation-functionHeader">

<span id="AnError" data-kind="variable">
```

查看html源代码，找到我们需要的节点。以上为三个示例，对应的配置如下
```yaml
- selector: h4[data-kind=type]
  type: tdef
  name:
    type: 1
    value: id
  level: 0
  anchor_only: false
- selector: h4[data-kind=function]
  type: Function
  name:
    type: 1
    value: id
  level: 0
  anchor_only: false
- selector: span[data-kind=variable]
  type: Variable
  name:
    type: 1
    value: id
  level: 0
  anchor_only: false
```
