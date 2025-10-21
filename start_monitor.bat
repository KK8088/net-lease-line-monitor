@echo off
echo 正在启动网络监控程序...
cd /d %~dp0

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.6或更高版本
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 警告: 依赖包安装失败，但程序可能仍可运行
)

REM 启动监控程序
echo 正在启动网络监控程序...
python network_monitor.py

pause