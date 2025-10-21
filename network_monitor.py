import subprocess
import time
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os

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
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.alert_history = {}
        
    def load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            "targets": ["8.8.8.8", "114.114.114.114", "www.baidu.com"],
            "check_interval": 30,
            "alert_cooldown": 300,
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
    
    def ping_host(self, host):
        """Ping指定主机"""
        try:
            # Windows系统使用-n参数，其他系统使用-c参数
            if os.name == 'nt':
                cmd = ["ping", "-n", "1", "-w", "1000", host]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", host]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            logging.error(f"Ping {host} 失败: {e}")
            return False
    
    def check_dns_resolution(self, host):
        """检查DNS解析"""
        try:
            import socket
            socket.gethostbyname(host)
            return True
        except Exception:
            return False
    
    def send_email_alert(self, subject, message):
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
    
    def send_webhook_alert(self, message):
        """发送Webhook报警"""
        if not self.config['webhook']['enabled']:
            return
            
        try:
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "type": "network_alert"
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
    
    def send_sms_alert(self, message):
        """发送短信报警"""
        if not self.config['sms']['enabled']:
            return
            
        try:
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat()
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
    
    def should_send_alert(self, target):
        """检查是否应该发送报警（避免频繁报警）"""
        now = time.time()
        if target in self.alert_history:
            last_alert = self.alert_history[target]
            if now - last_alert < self.config['alert_cooldown']:
                return False
        return True
    
    def record_alert(self, target):
        """记录报警时间"""
        self.alert_history[target] = time.time()
    
    def send_alert(self, target, is_recovered=False):
        """发送报警信息"""
        if is_recovered:
            subject = f"网络恢复通知 - {target}"
            message = f"目标主机 {target} 网络连接已恢复！\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            subject = f"网络中断警报 - {target}"
            message = f"目标主机 {target} 网络连接中断！\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        logging.warning(message if not is_recovered else f"恢复通知: {target}")
        
        # 发送各种报警
        self.send_email_alert(subject, message)
        self.send_webhook_alert(message)
        self.send_sms_alert(message)
    
    def monitor_target(self, target):
        """监控单个目标"""
        is_ping_ok = self.ping_host(target)
        is_dns_ok = self.check_dns_resolution(target) if not self.is_ip_address(target) else True
        
        status = {
            'ping': is_ping_ok,
            'dns': is_dns_ok,
            'reachable': is_ping_ok and is_dns_ok
        }
        
        # 检查是否需要报警
        if not status['reachable']:
            if self.should_send_alert(target):
                self.send_alert(target)
                self.record_alert(target)
        else:
            # 检查是否是从中断状态恢复
            if target in self.alert_history:
                self.send_alert(target, is_recovered=True)
                del self.alert_history[target]
        
        return status
    
    def is_ip_address(self, target):
        """判断是否为IP地址"""
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(ip_pattern, target) is not None
    
    def run(self):
        """运行监控程序"""
        logging.info("网络监控程序启动")
        logging.info(f"监控目标: {self.config['targets']}")
        logging.info(f"检查间隔: {self.config['check_interval']} 秒")
        
        while True:
            try:
                results = {}
                for target in self.config['targets']:
                    results[target] = self.monitor_target(target)
                    time.sleep(1)  # 避免同时ping太多目标
                
                # 记录当前状态
                status_summary = []
                for target, status in results.items():
                    status_summary.append(f"{target}: {'OK' if status['reachable'] else 'FAILED'}")
                
                logging.info("状态检查: " + ", ".join(status_summary))
                
                time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                logging.info("监控程序被用户中断")
                break
            except Exception as e:
                logging.error(f"监控过程中发生错误: {e}")
                time.sleep(10)  # 发生错误时等待10秒再继续

if __name__ == "__main__":
    monitor = NetworkMonitor()
    monitor.run()