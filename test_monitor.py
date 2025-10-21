import subprocess
import time
import sys
import os

def test_ping(host="8.8.8.8", count=4):
    """测试ping功能"""
    print(f"测试Ping {host} ...")
    try:
        if os.name == 'nt':
            cmd = ["ping", "-n", str(count), host]
        else:
            cmd = ["ping", "-c", str(count), host]
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print("Ping输出:")
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        print(f"返回码: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"Ping测试失败: {e}")
        return False

def test_network_monitor():
    """测试网络监控程序"""
    print("测试网络监控程序...")
    
    # 测试基本文件是否存在
    required_files = [
        "network_monitor.py",
        "advanced_network_monitor.py",
        "config.json",
        "requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 不存在")
    
    # 测试Python环境
    try:
        import requests
        print("✓ requests库可用")
    except ImportError:
        print("✗ requests库不可用，请安装: pip install requests")
    
    # 测试ping功能
    print("\n" + "="*50)
    test_ping()
    
    # 测试DNS解析
    print("\n" + "="*50)
    print("测试DNS解析...")
    try:
        import socket
        host = "www.baidu.com"
        ip = socket.gethostbyname(host)
        print(f"✓ {host} 解析为 {ip}")
    except Exception as e:
        print(f"✗ DNS解析失败: {e}")

if __name__ == "__main__":
    test_network_monitor()