#!/bin/bash

# 网络监控系统部署脚本

set -e  # 遇到错误时退出

echo "========================================="
echo "  网络监控系统部署脚本"
echo "========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本: sudo $0"
    exit 1
fi

# 创建安装目录
INSTALL_DIR="/opt/network-monitor"
echo "创建安装目录: $INSTALL_DIR"
mkdir -p $INSTALL_DIR

# 复制文件
echo "复制文件到安装目录..."
cp -r ./* $INSTALL_DIR/
cd $INSTALL_DIR

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 创建日志目录
echo "创建日志目录..."
mkdir -p /var/log/network-monitor

# 创建系统服务
echo "创建系统服务..."
cat > /etc/systemd/system/network-monitor.service << EOF
[Unit]
Description=Network Connectivity Monitor for Unicom Line
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/advanced_network_monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
echo "重新加载systemd配置..."
systemctl daemon-reload

# 启用并启动服务
echo "启用并启动网络监控服务..."
systemctl enable network-monitor
systemctl start network-monitor

# 检查服务状态
echo "检查服务状态..."
systemctl status network-monitor --no-pager

echo "========================================="
echo "部署完成！"
echo "========================================="
echo "查看服务状态: systemctl status network-monitor"
echo "查看日志: journalctl -u network-monitor -f"
echo "配置文件位置: $INSTALL_DIR/config.json"
echo "数据库文件位置: $INSTALL_DIR/network_stats.db"
echo "========================================="