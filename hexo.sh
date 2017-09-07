#!/bin/bash -
#################################################################
#
#    file: hexo.sh
#   usage: ./hexo.sh
#   brief:  
#  author: tenfyzhong
#   email: tenfyzhong@qq.com
# created: 2017-09-02 11:07:48
#
#################################################################

set -o nounset                              # Treat unset variables as an error


if [ $# -ne 1 ]; then
    echo "Usage ./hexo.sh d|s"
    exit 1
fi

if [ "$1" == "d" ]; then
    echo -n "Confirm to deploy?(Y/n): "
    read -r input
    if [ "$input" != 'y' ] && [ "$input" != 'Y' ]; then
        exit 0
    fi
elif [ "$1" != "s" ]; then
    echo "Usage ./hexo.sh d|s"
    exit 2
fi

cwd=$(pwd)
proc=$0
proc_path=$(dirname "$(readlink -f "$proc")")

if [ "$cwd" != "$proc_path" ]; then
    echo "请在$proc_path目录下执行"
    exit 2
fi

hexo --config source/_data/next.yml clean
hexo --config source/_data/next.yml g
hexo --config source/_data/next.yml "$1"

