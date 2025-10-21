from flask import Flask, jsonify, request
import threading
import subprocess
import os
import sys
import time
from datetime import datetime

# 将当前目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# 全局变量用于存储监控状态
monitor_process = None
monitor_status = "未启动"
monitor_logs = []

def start_monitor():
    """在后台线程中启动网络监控"""
    global monitor_status, monitor_logs
    try:
        monitor_status = "运行中"
        # 导入并运行高级监控程序
        from advanced_network_monitor import NetworkMonitor
        import logging
        
        # 设置日志处理器以捕获日志
        class LogCaptureHandler(logging.Handler):
            def emit(self, record):
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                monitor_logs.append(log_entry)
                # 只保留最近100条日志
                if len(monitor_logs) > 100:
                    monitor_logs.pop(0)
        
        # 添加日志处理器
        log_handler = LogCaptureHandler()
        logging.getLogger().addHandler(log_handler)
        
        # 启动监控程序
        monitor = NetworkMonitor()
        monitor.run()
    except Exception as e:
        monitor_status = f"错误: {str(e)}"
        monitor_logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': 'ERROR',
            'message': f'监控程序启动失败: {str(e)}'
        })

def start_monitor_process():
    """启动监控进程"""
    global monitor_process
    monitor_process = threading.Thread(target=start_monitor)
    monitor_process.daemon = True
    monitor_process.start()

# 应用启动时自动启动监控程序
start_monitor_process()

@app.route('/')
def home():
    return jsonify({
        'message': '联通100M专线网络监控系统',
        'status': monitor_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'monitor_status': monitor_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    return jsonify({
        'monitor_status': monitor_status,
        'logs': monitor_logs[-20:],  # 返回最近20条日志
        'timestamp': datetime.now().isoformat()
    })

@app.route('/config', methods=['GET', 'POST'])
def config():
    config_file = 'config.json'
    if request.method == 'POST':
        # 更新配置文件
        new_config = request.json
        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            return jsonify({'message': '配置更新成功'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        # 返回当前配置
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/restart')
def restart():
    """重启监控程序"""
    global monitor_process, monitor_status
    try:
        # 重新启动监控程序
        start_monitor_process()
        return jsonify({'message': '监控程序重启成功', 'status': monitor_status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 从环境变量获取端口，默认为8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)