#!/bin/bash

echo "正在启动网络监控程序..."

# 获取脚本所在目录
cd "$(dirname "$0")"

# 检查Python是否已安装
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python3，请先安装Python 3.6或更高版本"
    exit 1
fi

# 安装依赖
echo "正在安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "警告: 依赖包安装失败，但程序可能仍可运行"
fi

# 启动监控程序
echo "正在启动网络监控程序..."
python3 network_monitor.py