# 云服务器部署指南

## 部署到阿里云ECS服务器

### 1. 连接到ECS服务器

```bash
ssh root@your-ecs-ip-address
```

### 2. 安装Git和Python

```bash
# 更新系统包
yum update -y

# 安装Git
yum install git -y

# 安装Python 3
yum install python3 python3-pip -y

# 验证安装
python3 --version
pip3 --version
```

### 3. 克隆项目代码

```bash
# 创建项目目录
mkdir -p /opt/network-monitor
cd /opt/network-monitor

# 克隆项目
git clone https://github.com/KK8088/net-lease-line-monitor.git .
```

### 4. 安装依赖

```bash
# 安装Python依赖
pip3 install -r requirements.txt
```

### 5. 配置监控参数

编辑配置文件：
```bash
nano config.json
```

修改以下关键配置：
```json
{
  "targets": ["8.8.8.8", "114.114.114.114", "www.baidu.com", "your-critical-system.com"],
  "check_interval": 30,
  "alert_cooldown": 300,
  "email": {
    "enabled": true,
    "smtp_server": "your-smtp-server",
    "smtp_port": 587,
    "username": "your-email@example.com",
    "password": "your-email-password",
    "to_emails": ["admin@yourcompany.com"]
  },
  "webhook": {
    "enabled": true,
    "url": "https://oapi.dingtalk.com/robot/send?access_token=your-dingtalk-token"
  }
}
```

### 6. 创建系统服务

创建服务文件：
```bash
sudo nano /etc/systemd/system/network-monitor.service
```

添加以下内容：
```ini
[Unit]
Description=Network Connectivity Monitor for Unicom Line
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/network-monitor
ExecStart=/usr/bin/python3 /opt/network-monitor/advanced_network_monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 7. 启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务开机自启
sudo systemctl enable network-monitor

# 启动服务
sudo systemctl start network-monitor

# 检查服务状态
sudo systemctl status network-monitor
```

### 8. 查看日志

```bash
# 实时查看日志
journalctl -u network-monitor -f

# 查看最近的日志
journalctl -u network-monitor --since "10 minutes ago"
```

## 部署到腾讯云CVM服务器

步骤与阿里云ECS类似，主要区别在于系统包管理器：

### 1. 连接到CVM服务器

```bash
ssh ubuntu@your-cvm-ip-address
```

### 2. 安装Git和Python

```bash
# 更新系统包
sudo apt update -y

# 安装Git
sudo apt install git -y

# 安装Python 3
sudo apt install python3 python3-pip -y

# 验证安装
python3 --version
pip3 --version
```

### 3. 其他步骤

后续步骤与阿里云部署相同。

## Docker部署（推荐）

### 1. 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 克隆项目并配置

```bash
# 克隆项目
git clone https://github.com/KK8088/net-lease-line-monitor.git
cd net-lease-line-monitor

# 编辑配置文件
nano config.json
```

### 3. 启动容器

```bash
# 构建并启动容器
docker-compose up -d

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 配置报警方式

### 邮件报警配置

推荐使用企业邮箱SMTP服务：
- 阿里云企业邮箱：smtp.mxhichina.com:587
- 腾讯企业邮箱：smtp.exmail.qq.com:587
- Gmail：smtp.gmail.com:587

### 钉钉Webhook配置

1. 打开钉钉群设置
2. 选择"智能群助手"
3. 添加"自定义机器人"
4. 设置安全验证方式（推荐使用加签）
5. 复制Webhook URL并填入配置文件

### 短信报警配置

可以集成阿里云短信服务或腾讯云短信服务。

## 监控策略建议

### 监控目标选择
1. 国内DNS服务器：8.8.8.8、114.114.114.114
2. 国内大型网站：www.baidu.com、www.taobao.com
3. 国外网站：www.google.com、www.github.com
4. 关键业务系统：your-critical-system.com

### 报警策略
1. 检查间隔：30秒
2. 报警阈值：50%失败率
3. 冷却时间：300秒（5分钟）
4. 多种报警方式结合使用

## 故障排查

### 常见问题

1. **无法发送邮件**
   - 检查SMTP配置是否正确
   - 检查网络连接是否正常
   - 检查防火墙是否阻止SMTP端口

2. **Ping检测失败**
   - 检查目标主机是否允许Ping
   - 检查本地防火墙设置
   - 检查网络路由是否正常

3. **数据库错误**
   - 检查磁盘空间是否充足
   - 检查文件权限是否正确

### 日志分析

查看日志文件：
```bash
# 查看实时日志
tail -f network_monitor.log

# 搜索错误信息
grep "ERROR" network_monitor.log
```

## 性能优化

### 资源使用优化
1. 合理设置检查间隔，避免过度消耗CPU
2. 定期清理过期数据，避免数据库过大
3. 使用系统服务方式运行，确保稳定性

### 网络优化
1. 部署在不同网络环境中的多个监控节点
2. 使用CDN加速配置文件更新
3. 实现负载均衡避免单点故障

## 安全建议

1. 使用非root用户运行监控程序
2. 定期更新系统和依赖包
3. 保护配置文件中的敏感信息
4. 限制对日志文件的访问权限
5. 使用HTTPS/Webhook进行安全通信