---
title: 制作U盘启动盘
categories:
  - misc
date: 2017-09-26 17:09:54
---

本文介绍在osx和linux下制作U盘启动盘的方法。

<!-- more -->

假如要把ubuntu.iso做成启动盘。

# osx下制作启动盘
osx下制作启动盘，需要先将iso转成dmg格式的镜像。然后再把dmg dd到U盘里
### 1. 在终端下将iso转成dmg格式：
```sh
hdiutil convert -format UDRW -o ubuntu.dmg ubuntu.iso
```
### 2. 插入U盘
### 3. 查看U盘的挂载点
```sh
df -h
```
我的输出如下：
> Filesystem      Size  Used Avail Use% Mounted on  
> /dev/disk1      233G  190G   44G  82% /  
> /dev/disk2s1     28G   18G  9.8G  65% /Volumes/Aþ?EAUU  

这里disk1为电脑的硬盘，disk2s1为U盘
### 4. 卸载U盘
```sh
diskutil umountdisk /dev/disk2s1
```
### 5. 使用dd把ubuntu.dmg dmup到U盘
```sh
sudo dd if=ubuntu.dmg of=/dev/disk2 bs=1M
```
### 6. 完了会弹出无法识别文件系统，点弹出即可


# linux下制作启动盘
### 1. 插入U盘
### 2. 卸载U盘(请先用df查看U盘的卸载点)
```sh
sudo umount /dev/sdb
```
### 3. 使用dd把ubuntu.iso dump到U盘
```sh
sudo dd if=ubuntu.iso of=/dev/sdb bs=1M
```
