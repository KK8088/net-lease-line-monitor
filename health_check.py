#!/usr/bin/env python3
import sqlite3
import json
import os
from datetime import datetime, timedelta

def check_health():
    """检查监控系统的健康状态"""
    print("="*60)
    print("网络监控系统健康检查报告")
    print("="*60)
    
    # 1. 检查配置文件
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✓ 配置文件正常")
            print(f"  监控目标数量: {len(config.get('targets', []))}")
            print(f"  检查间隔: {config.get('check_interval', 30)}秒")
        except Exception as e:
            print(f"✗ 配置文件解析失败: {e}")
    else:
        print("✗ 配置文件不存在")
    
    # 2. 检查数据库
    db_file = "network_stats.db"
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if 'network_status' in tables:
                # 获取数据统计
                cursor.execute("SELECT COUNT(*) FROM network_status")
                count = cursor.fetchone()[0]
                print("✓ 数据库正常")
                print(f"  已记录 {count} 条监控数据")
                
                # 获取最近一次检查时间
                cursor.execute("SELECT timestamp FROM network_status ORDER BY timestamp DESC LIMIT 1")
                last_check = cursor.fetchone()
                if last_check:
                    last_time = datetime.fromisoformat(last_check[0])
                    print(f"  最近检查时间: {last_time}")
            else:
                print("✗ 数据库表结构不完整")
                
            conn.close()
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
    else:
        print("ℹ 数据库文件不存在（首次运行时正常）")
    
    # 3. 检查日志文件
    log_file = "network_monitor.log"
    if os.path.exists(log_file):
        try:
            # 获取文件大小
            size = os.path.getsize(log_file)
            print("✓ 日志文件存在")
            print(f"  日志文件大小: {size} 字节 ({size/1024/1024:.2f} MB)")
            
            # 检查最近的错误日志
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                error_lines = [line for line in lines if 'ERROR' in line]
                if error_lines:
                    print(f"  发现 {len(error_lines)} 条错误日志")
                    if error_lines:
                        print(f"  最近错误: {error_lines[-1].strip()}")
                else:
                    print("  无错误日志")
        except Exception as e:
            print(f"✗ 日志文件读取失败: {e}")
    else:
        print("ℹ 日志文件不存在（首次运行时正常）")
    
    # 4. 检查依赖
    try:
        import requests
        print("✓ Python依赖正常")
    except ImportError as e:
        print(f"✗ Python依赖缺失: {e}")
    
    print("="*60)

if __name__ == "__main__":
    check_health()