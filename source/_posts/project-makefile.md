---
title: 工程makefile管理的一种比较合理的方案
date: 2017-09-01 23:52:14
tags:
  - 后台
  - c
  - c++
categories: 
  - 工程管理
---
# 现状  
可以说makefile也是代码，都是命令的集合。代码臭味中最出名的算是重复代码了。而工程
中的makefile存在这样的情况。每新建一个目录，就将别的目录下的makefile拷过来，这个
makefile文件包含了进行编译的所有指令。  

这篇文章将会让你的Makefile清晰明了。
<!-- more -->

# 问题
基于现状引入以下的问题。
- 难以维护，当发现被拷过来的makefile有bug，需要将所有的makefile去改一次，特别是
  有拷过来的文件有所特殊的改动时，还不能进行覆盖。  
- 增加新特性时，比较麻烦。  

# 方案
makefile中公共的部分提出来，就像代码中的函数。需要用的地方去包含就行了。

# 补充几个必要的知识点,更详情的可以找makefile的文档来看（对于熟悉makefile的可以跳过）
1. include。makefile解释到include指令的时候，停止当前文件的解释，去将include的
   文件插到当前文件来，然后解释被include的文件。完成后再去解释当前文件剩下的部分。  
2. 目标。makefile最终的目的是生成我们要的目标。每个目标后面加一个冒号，后面加依
   赖的文件。换行缩进一个tab，写命令。而makefile最张展开后的第一个目标是默认的
   终极目标。我们可以在make的时候传入一个目标做为终极目标。终极目标会根据依赖进
   行树状展开。

# 核心代码
对于编译代码，跟目录层级进行make -C，我们要使用不同的规则。所以这里有两个不同核
心部分代码。  
1. 编译代码的makefile, 文件名comm.mk，这里的makefile.plib是我们工程里定义的一些
   makefile变量，用于编译时传给gcc的头文件和库文件的查找路径。这里定义了INC_DIR, 
   SRC_DIR等变量的目的是可以让需要进行编译的目录有一个可以自定义目录层次的入口。
   默认一个目录下的头文件放在include下，源文件放在src下，生成的目标文件放在obj下，
   生成的库文件放在lib下。目前看不懂，没关系。第3点会说怎么使用。

```
include $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/plib/makefile.plib

ifndef INC_DIR
    INC_DIR = include/
endif

ifndef SRC_DIR
    SRC_DIR = src/
endif

ifndef OBJ_DIR
    OBJ_DIR = obj/
endif

ifndef LIB_DIR
    LIB_DIR = lib/
endif

ifndef OBJ_EXT
    OBJ_EXT = .o
endif

ifndef DEPEND_EXT
    DEPEND_EXT = .d
endif

ifndef CPPSRC_EXT
    CPPSRC_EXT = .cpp
endif

ifndef PREPROCESS_EXT
    PREPROCESS_EXT = .e
endif

ifndef PRECOMPILE_EXT
    PRECOMPILE_EXT = .gch
endif

ifndef OBJECTS
    OBJECTS=$(patsubst $(SRC_DIR)%.cpp,$(OBJ_DIR)%.o,$(wildcard $(SRC_DIR)*.cpp))
endif

ifndef DEPENDS
    DEPENDS=$(patsubst $(SRC_DIR)%.cpp,$(OBJ_DIR)%.d,$(wildcard $(SRC_DIR)*.cpp))
endif

ifndef PRE_PROCESS_OBJS
    PRE_PROCESS_OBJS=$(patsubst $(SRC_DIR)%.cpp,$(OBJ_DIR)%.i,$(wildcard $(SRC_DIR)*.cpp))
endif

PWD=$(shell pwd)

ifndef LIB_TARGET
    LIB_TARGET = $(LIB_DIR)lib$(TARGET_PREFIX)$(shell basename $(PWD))$(TARGET_POSTFIX).a
endif

ALL+=$(LIB_TARGET)

ifeq "$(YCM_CONF)" "1"
ALL+=.ycm_extra_conf.py
endif

ifeq "$(HAS_GIT)" "1"
ALL+= $(OBJ_DIR).gitignore $(LIB_DIR).gitignore
endif

ifdef NEED_GCH
ifndef PRE_COMPILE_OBJS
    PRE_COMPILE_OBJS=$(patsubst $(INC_DIR)%.h,$(INC_DIR)%.gch,$(wildcard $(INC_DIR)*.h))
endif

ALL+= $(PRE_COMPILE_OBJS)
$(OBJECTS): $(PRE_COMPILE_OBJS)


$(PRE_COMPILE_OBJS): $(INC_DIR)%.gch: $(INC_DIR)%.h
    @echo -e "\033[1;33m\nPrecompiling $< ==> $@ \033[0m..."
    $(CXX) $(INC) $(C_FLAGS) $<
    @echo ""
endif

.PHONY: all clean test
all: $(ALL)

test:
    @echo $(ALL)

clean:
    rm $(OBJ_DIR)*$(OBJ_EXT) $(OBJ_DIR)*$(DEPEND_EXT) $(LIB_TARGET) $(PRE_COMPILE_OBJS) $(EXTRA) -rf

ifeq "$(HAS_GIT)" "1"
ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
$(OBJ_DIR).gitignore: | $(OBJ_DIR)
    touch $@

ifneq "$(OBJ_DIR)" "$(LIB_DIR)"
$(LIB_DIR).gitignore: | $(LIB_DIR)
    touch $@
endif

endif
endif
endif


ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
$(DEPENDS): $(OBJ_DIR)%$(DEPEND_EXT): $(SRC_DIR)%$(CPPSRC_EXT) | $(OBJ_DIR)
    @echo -e "\033[1;33m\nCompiling $< ==> $@ \033[0m..."
    @$(CXX) -MM $(INC) -I$(INC_DIR) $(C_FLAGS) $< > $@.$$$$; \
        sed 's,\($*\)\.o[ :]*,$(OBJ_DIR)\1.o $@ : ,g' < $@.$$$$ > $@; \
        rm -f $@.$$$$;
endif
endif

$(OBJECTS): $(OBJ_DIR)%$(OBJ_EXT): $(SRC_DIR)%$(CPPSRC_EXT) | $(OBJ_DIR)
    @echo -e "\033[1;33m\nCompiling $< ==> $@ \033[0m..."
    $(CXX) $(INC) -I$(INC_DIR) $(C_FLAGS) -c $< -o $@
    @echo ""

$(PRE_PROCESS_OBJS): $(OBJ_DIR)%.i: $(SRC_DIR)%$(CPPSRC_EXT) | $(OBJ_DIR)
    @echo -e "\033[1;33m\nPreprocessing $< ==> $@ \033[0m..."
    $(CXX) $(INC) -I$(INC_DIR) $(C_FLAGS) -E $< > $@
    @echo ""

ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
$(OBJ_DIR):
    -mkdir $@
endif
endif

ifneq "$(LIB_TARGET)" ""
# $(LIB_TARGET): | $(LIB_DIR)

$(LIB_TARGET):$(OBJECTS) $(DEPENDS) | $(LIB_DIR)
    @echo "$(OBJECTS) ==> $@"
    $(AR) rc $(LIB_TARGET) $(OBJECTS)
    @echo ""

ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
ifneq "$(OBJ_DIR)" "$(LIB_DIR)"
$(LIB_DIR):
    -mkdir $@
endif
endif
endif
endif

.ycm_extra_conf.py: makefile $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/tools/generate_ycm.sh $(DEPENDS)
    @echo -e "\033[1;33m\ngenerate .ycm_extra_conf \033[0m..."
    $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/tools/generate_ycm.sh "$(INC)"
    @echo ""

ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
sinclude $(DEPENDS)
endif
endif


```

2. 目录层级使用make -C来编译下一层目录, dir.mk。这里通过FILTER_OUT来排除要编译的目录。

```
include $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/plib/makefile.plib

FILTER_OUT+=$(wildcard makefile*) tags

ifndef ALL_DIRS
    ALL_DIRS=$(filter-out $(FILTER_OUT), $(wildcard *))
endif

.PHONY: all clean $(ALL_DIRS)
all: $(ALL_DIRS)

clean: $(ALL_DIRS)

$(ALL_DIRS):
    if [ -f $@/makefile ] ; \
    then \
        $(MAKE) -C $@ $(MAKECMDGOALS) ; \
        fi

```

3. 下面以我的工程中的comm_process目录来进行讲解一下普通目录的编译。目录树如下。

```
~/m/a/s/comm_process(master) $ tree -L 1
.
|-- include
|-- lib
|-- makefile
|-- obj
`-- src

```
makefile文件内容如下：

```
include $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/makeinclude/comm.mk

INC+=-I./include
INC+=$(INC_MOBILE_TAIL_API) $(INC_SHARE_BUIS_COMM)

LIB_TARGET=lib/libcommprocess.a

```
这个文件一开头就去include了我们之前的comm.mk文件，里面定义了各个编译.cpp，生成
目标文件的规则。而INC变量，可以在comm.mk的OBJECT生成规则那里用到，用于提供给
`gcc -I`进行查找头文件。而INC_MOBILE_TAIL_API， INC_SHARE_BUIS_COMM这些变量定义
在我们之前说的那个makefle.plib下。
一定定义成这样：

```
INC_MOBILE_TAIL_API=-I../mobile_tail_api/include
```

4. 下面介绍目录层级的makefile, 里面定义的规则是跳到下一级目录下去进行编译。以下
的目录结构如下：  

```
~/m/a/share(master) $ tree -L 1
.
|-- busi_comm
|-- comm_process
|-- makefile
|-- mt_spp
|-- mysql
|-- protocol
|-- server_frame
|-- task
|-- task_frame
`-- webapp_frame

9 directories, 1 file

```
makefile如下：

```
FILTER_OUT+=mt_spp
include $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/makeinclude/dir.mk

```
首先加入一些我们不希望编译的目录在FILTER_OUT里面。然后include我们第2点的dir.mk
文件。然后在这层目录进行make，就会进行跳到各个目录去编译了。

5. 到这里，会发现还不能达到我们项目的要求。我们项目一般是编出来一个动态库或者一
个可执行文件。而我们上面编出来的只是静态库。我们可以根据在comm.mk的基础上去加规
则来生成动态库或者可执行文件。以下以生成一个动态库为例子。  mtserver.mk

```
ifndef LIB_DIR
    LIB_DIR = bin/
endif

ifndef BIN_TARGET
    BIN_TARGET = $(LIB_DIR)lib$(TARGET_PREFIX)$(shell basename $(shell basename $(PWD)))$(TARGET_POSTFIX).so
endif

BIN_SO_NAME = $(word $(words $(subst /, ,$(BIN_TARGET))), $(subst /, ,$(BIN_TARGET)))

BIN_LIB=$(shell dirname $(BIN_TARGET))


LIB_TARGET=
ALL+=$(BIN_TARGET)
EXTRA+=$(BIN_TARGET)

ifeq "$(HAS_GIT)" "1"
ALL+=$(BIN_DIR).gitignore
endif

include $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/makeinclude/comm.mk

SO_DIR=$(PATH_PROJ_ROOT)/so
STRIP_SO_DIR=$(PATH_PROJ_ROOT)/strip_so

$(BIN_TARGET): $(OBJECTS) $(DEPENDS)
    @echo -e "\033[1;33m\nCompiling $< ==> $@ \033[0m..."
    $(CXX) $(INC) $(C_FLAGS) -shared -Wl,-rpath,/usr/local/qzone/lib $(PATH_PROJ_ROOT)/application/share/server_frame/obj/service.o $(OBJECTS) $(LIB) -lz -o $@ ; \
        $(PATH_PROJ_ROOT)/tools/check_symbol.sh $@; \
        if [ $$? -eq 0 ]; then \
            cp $@ $(SO_DIR) ;\
            cp $@ $(STRIP_SO_DIR); \
            strip $(STRIP_SO_DIR)/$(BIN_SO_NAME); \
        fi;

$(ALL) : del_target

$(BIN_TARGET): | $(BIN_DIR)

ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
$(BIN_DIR):
    -mkdir $@
endif
endif

ifeq "$(HAS_GIT)" "1"
ifneq "$(MAKECMDGOALS)" "clean"
ifneq "$(MAKECMDGOALS)" "test"
$(BIN_DIR).gitignore: | $(BIN_DIR)
    touch $@
endif
endif
endif

.PHONY:del_target
del_target:
    $(RM) bin/*

```
这里我们一样include了comm.mk，然后在它的基础上去编译生成动态库。

6. 到目前，我们的规则可以生成动态库了。但是还存在一个问题，就是同层目录，可能编
译会有先后顺序的问题，比如，我要先编好share目录，才能去编业务的so目录。如以下的
目录结构：  

```
~/m/application(master) $ tree -L 1
.
|-- makefile
|-- server
|-- share
|-- tools
`-- webapps

4 directories, 1 file

```
makefile如下：

```
~/m/application(master) $ cat makefile
include $(shell dirname $(PATH_MV_PRJ))/$(shell basename $(PATH_MV_PRJ))/makeinclude/dir.mk

WITHOUT_SHARE=$(filter-out share, $(ALL_DIRS))

$(WITHOUT_SHARE): share

```
会发现，其实makefile跟其他跳去编下一层目录的makefile差不多，就是多了最后两行。
倒数第二行，是将目录文件将share去掉，最后一行是将除了share目录的其他目录编译都
需要先依赖share目录编译完才会去编译。

到这里我们的整个工程makefile都可以使用上面定义的comm.mk，dir.mk，mtserver.mk目录
进行组织了。

# 总结一下改造的过程

1. 编写comm.mk，dir.mk，放在工程比较顶层的目录中，以便其他目录去include。
2. 编写特殊的makefile，如mtserver.mk文件，以便生成特殊上目标文件（如.so）去include。
3. 从工程的根目录开始，如果当前目录下放的是一些子目录，则写一个makefile，去
   `include dir.mk`。如果当前目录下放的是src include obj lib的文件，里面分别放了
   .cpp .h文件，则去include comm.mk文件，如果当前目录下没有src include obj lib
   目录来组织.cpp .h文件，则将INC_DIR SRC_DIR OBJ_DIR LIB_DIR赋空，再去include comm.mk文件。

