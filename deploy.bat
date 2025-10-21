@echo off
title 网络监控系统部署脚本

echo =========================================
echo   网络监控系统Windows部署脚本
echo =========================================

REM 检查Python是否已安装
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.6或更高版本
    pause
    exit /b 1
)

REM 安装依赖
echo 安装Python依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 警告: 依赖包安装失败
    pause
)

REM 创建数据目录
echo 创建数据目录...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo =========================================
echo 部署完成！
echo =========================================
echo 可以通过以下方式运行监控程序：
echo 1. 双击 start_monitor.bat
echo 2. 命令行运行: python advanced_network_monitor.py
echo.
echo 配置文件: config.json
echo 日志文件: network_monitor.log
echo 数据库文件: network_stats.db
echo =========================================

pause