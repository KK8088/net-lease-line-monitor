import subprocess
import time
import logging
import smtplib
import requests
import sqlite3
import json
import os
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_monitor.log'),
        logging.StreamHandler()
    ]
)

class NetworkMonitor:
    def __init__(self, config_file='config.json', db_file='network_stats.db'):
        self.config = self.load_config(config_file)
        self.db_file = db_file
        self.init_database()
        self.alert_history = {}
        self.stats = {}  # 存储每个目标的统计信息
        
    def load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            "targets": ["8.8.8.8", "114.114.114.114", "www.baidu.com"],
            "check_interval": 30,
            "alert_cooldown": 300,
            "timeout": 5,
            "packet_count": 4,
            "statistics_window": 3600,  # 1小时统计窗口
            "alert_threshold": 0.5,  # 50%失败率触发报警
            "email": {
                "enabled": False,
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "your_email@example.com",
                "password": "your_password",
                "to_emails": ["admin@example.com"]
            },
            "webhook": {
                "enabled": False,
                "url": "https://hooks.example.com/notify"
            },
            "sms": {
                "enabled": False,
                "api_url": "https://sms.example.com/send"
            },
            "database": {
                "enabled": True,
                "retention_days": 30
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置和用户配置
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        else:
            # 创建默认配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config
    
    def init_database(self):
        """初始化数据库"""
        if not self.config['database']['enabled']:
            return
            
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 创建网络状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                reachable BOOLEAN NOT NULL,
                ping_time REAL,
                packet_loss REAL,
                error_message TEXT
            )
        ''')
        
        # 创建统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                period_start DATETIME NOT NULL,
                period_end DATETIME NOT NULL,
                total_checks INTEGER NOT NULL,
                successful_checks INTEGER NOT NULL,
                avg_response_time REAL,
                packet_loss_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def ping_host(self, host) -> Tuple[bool, float, float, str]:
        """Ping指定主机，返回(是否可达, 响应时间, 丢包率, 错误信息)"""
        try:
            packet_count = self.config['packet_count']
            timeout = self.config['timeout']
            
            # Windows系统使用-n参数，其他系统使用-c参数
            if os.name == 'nt':
                cmd = ["ping", "-n", str(packet_count), "-w", str(timeout*1000), host]
            else:
                cmd = ["ping", "-c", str(packet_count), "-W", str(timeout), host]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
            
            if result.returncode == 0:
                # 解析ping输出获取响应时间和丢包率
                output = result.stdout
                ping_time = self._parse_ping_time(output)
                packet_loss = self._parse_packet_loss(output)
                return True, ping_time, packet_loss, ""
            else:
                return False, 0, 1.0, result.stdout + result.stderr
                
        except subprocess.TimeoutExpired:
            return False, 0, 1.0, "Ping超时"
        except Exception as e:
            logging.error(f"Ping {host} 失败: {e}")
            return False, 0, 1.0, str(e)
    
    def _parse_ping_time(self, output: str) -> float:
        """解析ping输出中的平均响应时间"""
        try:
            # Windows格式: Average = 20ms
            # Linux格式: avg = 20.0ms
            import re
            if 'Average' in output:
                match = re.search(r'Average = (\d+)ms', output)
            else:
                match = re.search(r'avg = ([\d.]+)', output)
                
            if match:
                return float(match.group(1))
            return 0
        except Exception:
            return 0
    
    def _parse_packet_loss(self, output: str) -> float:
        """解析ping输出中的丢包率"""
        try:
            import re
            # 格式: Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
            # 或: 4 packets transmitted, 4 received, 0% packet loss
            match = re.search(r'(\d+)%.*loss', output)
            if match:
                return float(match.group(1)) / 100.0
            return 0
        except Exception:
            return 0
    
    def check_dns_resolution(self, host) -> bool:
        """检查DNS解析"""
        try:
            import socket
            socket.gethostbyname(host)
            return True
        except Exception:
            return False
    
    def save_to_database(self, target: str, reachable: bool, ping_time: float, 
                        packet_loss: float, error_message: str):
        """保存检测结果到数据库"""
        if not self.config['database']['enabled']:
            return
            
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO network_status 
                (target, timestamp, reachable, ping_time, packet_loss, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (target, datetime.now(), reachable, ping_time, packet_loss, error_message))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"保存数据到数据库失败: {e}")
    
    def calculate_statistics(self, target: str) -> Dict:
        """计算指定时间段内的统计数据"""
        if not self.config['database']['enabled']:
            return {}
            
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 计算最近一段时间的统计数据
            window_start = datetime.now() - timedelta(seconds=self.config['statistics_window'])
            
            cursor.execute('''
                SELECT COUNT(*) as total, SUM(CASE WHEN reachable THEN 1 ELSE 0 END) as successful,
                       AVG(ping_time) as avg_ping, AVG(packet_loss) as avg_loss
                FROM network_status 
                WHERE target = ? AND timestamp >= ?
            ''', (target, window_start))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] > 0:
                return {
                    'total_checks': row[0],
                    'successful_checks': row[1] or 0,
                    'success_rate': (row[1] or 0) / row[0],
                    'avg_response_time': row[2] or 0,
                    'avg_packet_loss': row[3] or 0
                }
            
            return {}
        except Exception as e:
            logging.error(f"计算统计数据失败: {e}")
            return {}
    
    def should_send_alert(self, target: str, stats: Dict) -> bool:
        """检查是否应该发送报警"""
        # 检查基本连通性
        if stats.get('success_rate', 1.0) >= self.config['alert_threshold']:
            return False
            
        # 检查冷却时间
        now = time.time()
        if target in self.alert_history:
            last_alert = self.alert_history[target]
            if now - last_alert < self.config['alert_cooldown']:
                return False
        return True
    
    def record_alert(self, target: str):
        """记录报警时间"""
        self.alert_history[target] = time.time()
    
    def send_email_alert(self, subject: str, message: str):
        """发送邮件报警"""
        if not self.config['email']['enabled']:
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = ', '.join(self.config['email']['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
            logging.info("邮件报警发送成功")
        except Exception as e:
            logging.error(f"发送邮件报警失败: {e}")
    
    def send_webhook_alert(self, message: str, alert_type: str = "network_alert"):
        """发送Webhook报警"""
        if not self.config['webhook']['enabled']:
            return
            
        try:
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "type": alert_type,
                "system": "Unicom Line Monitor"
            }
            response = requests.post(
                self.config['webhook']['url'],
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                logging.info("Webhook报警发送成功")
            else:
                logging.error(f"Webhook报警发送失败，状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"发送Webhook报警失败: {e}")
    
    def send_sms_alert(self, message: str):
        """发送短信报警"""
        if not self.config['sms']['enabled']:
            return
            
        try:
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "priority": "high"
            }
            response = requests.post(
                self.config['sms']['api_url'],
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                logging.info("短信报警发送成功")
            else:
                logging.error(f"短信报警发送失败，状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"发送短信报警失败: {e}")
    
    def send_alert(self, target: str, stats: Dict, is_recovered: bool = False):
        """发送报警信息"""
        if is_recovered:
            subject = f"【恢复】网络连接恢复 - {target}"
            message = f"""监控目标: {target}
状态: 已恢复
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
统计信息:
- 成功率: {stats.get('success_rate', 0)*100:.1f}%
- 平均响应时间: {stats.get('avg_response_time', 0):.2f}ms
- 平均丢包率: {stats.get('avg_packet_loss', 0)*100:.1f}%

此通知表示该目标的网络连接已经恢复正常。"""
        else:
            subject = f"【警报】网络连接异常 - {target}"
            message = f"""监控目标: {target}
状态: 异常
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
统计信息:
- 成功率: {stats.get('success_rate', 0)*100:.1f}%
- 平均响应时间: {stats.get('avg_response_time', 0):.2f}ms
- 平均丢包率: {stats.get('avg_packet_loss', 0)*100:.1f}%
- 总检测次数: {stats.get('total_checks', 0)}
- 成功次数: {stats.get('successful_checks', 0)}

请及时检查网络连接情况!"""
        
        logging.warning(message if not is_recovered else f"恢复通知: {target}")
        
        # 发送各种报警
        self.send_email_alert(subject, message)
        self.send_webhook_alert(message, "network_recovery" if is_recovered else "network_alert")
        self.send_sms_alert(message)
    
    def cleanup_old_data(self):
        """清理过期数据"""
        if not self.config['database']['enabled']:
            return
            
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 删除过期的状态数据
            retention_date = datetime.now() - timedelta(days=self.config['database']['retention_days'])
            cursor.execute('''
                DELETE FROM network_status WHERE timestamp < ?
            ''', (retention_date,))
            
            # 删除过期的统计数据
            cursor.execute('''
                DELETE FROM network_statistics WHERE period_end < ?
            ''', (retention_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logging.info(f"已清理 {deleted_count} 条过期数据")
        except Exception as e:
            logging.error(f"清理过期数据失败: {e}")
    
    def is_ip_address(self, target: str) -> bool:
        """判断是否为IP地址"""
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(ip_pattern, target) is not None
    
    def monitor_target(self, target: str) -> Dict:
        """监控单个目标"""
        is_ping_ok, ping_time, packet_loss, error_msg = self.ping_host(target)
        is_dns_ok = self.check_dns_resolution(target) if not self.is_ip_address(target) else True
        
        reachable = is_ping_ok and is_dns_ok
        
        # 保存到数据库
        self.save_to_database(target, reachable, ping_time, packet_loss, error_msg)
        
        # 计算统计数据
        stats = self.calculate_statistics(target)
        
        # 更新内存中的统计信息
        self.stats[target] = stats
        
        # 检查是否需要报警
        if stats and stats.get('success_rate', 1.0) < self.config['alert_threshold']:
            if self.should_send_alert(target, stats):
                self.send_alert(target, stats)
                self.record_alert(target)
        else:
            # 检查是否是从中断状态恢复
            if target in self.alert_history:
                self.send_alert(target, stats, is_recovered=True)
                del self.alert_history[target]
        
        return {
            'ping': is_ping_ok,
            'dns': is_dns_ok,
            'reachable': reachable,
            'ping_time': ping_time,
            'packet_loss': packet_loss,
            'stats': stats
        }
    
    def print_status(self, results: Dict):
        """打印状态信息"""
        print("\n" + "="*80)
        print(f"网络监控状态报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        for target, status in results.items():
            reachable = "✓" if status['reachable'] else "✗"
            ping_time = f"{status['ping_time']:.2f}ms" if status['ping_time'] > 0 else "N/A"
            packet_loss = f"{status['packet_loss']*100:.1f}%"
            
            stats = status['stats']
            success_rate = f"{stats.get('success_rate', 1.0)*100:.1f}%" if stats else "N/A"
            
            print(f"{reachable} {target:<20} RTT:{ping_time:>8} 丢包:{packet_loss:>6} 成功率:{success_rate:>6}")
        
        print("="*80)
    
    def run(self):
        """运行监控程序"""
        logging.info("高级网络监控程序启动")
        logging.info(f"监控目标: {self.config['targets']}")
        logging.info(f"检查间隔: {self.config['check_interval']} 秒")
        logging.info(f"报警阈值: {self.config['alert_threshold']*100:.0f}% 失败率")
        
        # 启动数据清理线程
        cleanup_thread = threading.Thread(target=self.periodic_cleanup, daemon=True)
        cleanup_thread.start()
        
        while True:
            try:
                results = {}
                for target in self.config['targets']:
                    results[target] = self.monitor_target(target)
                    time.sleep(1)  # 避免同时ping太多目标
                
                # 打印状态
                self.print_status(results)
                
                time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                logging.info("监控程序被用户中断")
                break
            except Exception as e:
                logging.error(f"监控过程中发生错误: {e}")
                time.sleep(10)  # 发生错误时等待10秒再继续
    
    def periodic_cleanup(self):
        """定期清理过期数据"""
        while True:
            try:
                time.sleep(3600)  # 每小时执行一次
                self.cleanup_old_data()
            except Exception as e:
                logging.error(f"数据清理过程中发生错误: {e}")

def main():
    parser = argparse.ArgumentParser(description='网络连通性监控程序')
    parser.add_argument('--config', '-c', default='config.json', help='配置文件路径')
    parser.add_argument('--db', '-d', default='network_stats.db', help='数据库文件路径')
    parser.add_argument('--test', '-t', action='store_true', help='测试模式，只执行一次检测')
    
    args = parser.parse_args()
    
    monitor = NetworkMonitor(args.config, args.db)
    
    if args.test:
        print("执行测试检测...")
        results = {}
        for target in monitor.config['targets']:
            results[target] = monitor.monitor_target(target)
            time.sleep(1)
        monitor.print_status(results)
    else:
        monitor.run()

if __name__ == "__main__":
    main()