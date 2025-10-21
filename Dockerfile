# 使用Python官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY network_monitor.py .
COPY advanced_network_monitor.py .
COPY config.json .
COPY start_monitor.sh .

# 创建日志目录
RUN mkdir -p /var/log/network-monitor

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 给脚本执行权限
RUN chmod +x start_monitor.sh

# 暴露端口（如果需要Web界面）
# EXPOSE 8000

# 启动应用程序
CMD ["python", "advanced_network_monitor.py"]