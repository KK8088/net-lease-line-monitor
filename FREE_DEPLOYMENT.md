# 免费服务器部署指南

本指南将介绍如何将联通100M专线网络监控系统部署到各种免费的云服务平台上。

## 支持的免费平台

1. [Render](https://render.com/) - 提供免费的Web服务和后台服务
2. [Railway](https://railway.app/) - 简单易用的部署平台
3. [Fly.io](https://fly.io/) - 提供免费的容器部署
4. [Heroku](https://www.heroku.com/) - 经典的PaaS平台（有限免费额度）
5. [Google Cloud Run](https://cloud.google.com/run) - Google的容器化服务
6. [GitHub Codespaces](https://github.com/features/codespaces) - GitHub的云端开发环境

## 1. Render部署指南

### 准备工作
1. 访问 [Render](https://render.com/) 并注册账户
2. 在GitHub上Fork本项目或连接您的GitHub仓库

### 部署步骤
1. 登录Render控制台
2. 点击"New+"按钮，选择"Web Service"
3. 连接您的GitHub账户并选择仓库
4. 配置服务设置：
   - Name: network-monitor
   - Region: 选择离您最近的区域
   - Branch: main
   - Root Directory: 留空
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python advanced_network_monitor.py`

5. 在"Advanced"设置中添加环境变量：
   - PYTHON_VERSION: 3.9.0

6. 点击"Create Web Service"

### 配置注意事项
由于Render是为Web应用设计的，而我们的网络监控程序是后台服务，需要进行以下调整：

1. 创建一个web.py文件作为Web入口：
```python
from flask import Flask
import threading
import subprocess
import os

app = Flask(__name__)

def start_monitor():
    """在后台线程中启动网络监控"""
    os.system("python advanced_network_monitor.py")

# 在单独的线程中启动监控程序
monitor_thread = threading.Thread(target=start_monitor)
monitor_thread.daemon = True
monitor_thread.start()

@app.route('/')
def home():
    return "网络监控系统正在运行中..."

@app.route('/health')
def health():
    return "健康检查正常"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
```

2. 更新requirements.txt文件：
```
requests>=2.25.1
flask>=2.0.0
```

## 2. Railway部署指南

### 准备工作
1. 访问 [Railway](https://railway.app/) 并注册账户
2. 安装Railway CLI：`npm i -g @railway/cli`

### 部署步骤
1. 克隆项目到本地：
```bash
git clone https://github.com/KK8088/net-lease-line-monitor.git
cd net-lease-line-monitor
```

2. 登录Railway：
```bash
railway login
```

3. 初始化新项目：
```bash
railway init
```

4. 部署项目：
```bash
railway up
```

### 配置注意事项
同样需要创建Web入口文件，参考Render部分的web.py文件。

## 3. Fly.io部署指南

### 准备工作
1. 访问 [Fly.io](https://fly.io/) 并注册账户
2. 安装Fly CLI：`curl -L https://fly.io/install.sh | sh`

### 部署步骤
1. 登录Fly：
```bash
flyctl auth login
```

2. 启动部署向导：
```bash
flyctl launch
```

3. 按照提示操作：
   - 应用名称：network-monitor
   - 选择地区
   - 是否部署PostgreSQL：否
   - 是否部署现在：是

### 配置注意事项
需要创建fly.toml配置文件：
```toml
# fly.toml file generated for network-monitor
app = "network-monitor"
kill_signal = "SIGINT"
kill_timeout = 5
processes = []

[build]
  builder = "paketobuildpacks/builder:base"
  buildpacks = ["gcr.io/paketo-buildpacks/python"]

[env]
  PORT = "8080"

[experimental]
  allowed_public_ports = []
  auto_rollback = true

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []
```

## 4. GitHub Codespaces部署指南

### 准备工作
1. 确保您的GitHub账户有Codespaces的使用权限
2. 在GitHub仓库页面点击"Code"按钮，选择"Open with Codespaces"

### 部署步骤
1. 创建新的Codespace：
   - 点击"New codespace"
   - 选择合适的机器类型（4-core机器每月有120小时免费额度）

2. 在Codespace终端中运行：
```bash
# 安装依赖
pip install -r requirements.txt

# 运行监控程序
python advanced_network_monitor.py
```

### 配置注意事项
Codespaces适合开发和测试，但不适合长期运行后台服务。

## 5. Google Cloud Run部署指南

### 准备工作
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用Cloud Run API
4. 安装Google Cloud SDK

### 部署步骤
1. 构建Docker镜像并推送到Google Container Registry：
```bash
# 配置项目ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# 构建镜像
gcloud builds submit --tag gcr.io/$PROJECT_ID/network-monitor

# 部署到Cloud Run
gcloud run deploy --image gcr.io/$PROJECT_ID/network-monitor --platform managed
```

### 配置注意事项
同样需要创建Web入口文件，参考Render部分的web.py文件。

## 6. Heroku部署指南

### 准备工作
1. 访问 [Heroku](https://www.heroku.com/) 并注册账户
2. 安装Heroku CLI
3. 登录Heroku：`heroku login`

### 部署步骤
1. 克隆项目：
```bash
git clone https://github.com/KK8088/net-lease-line-monitor.git
cd net-lease-line-monitor
```

2. 创建Heroku应用：
```bash
heroku create network-monitor-app
```

3. 设置构建包：
```bash
heroku buildpacks:set heroku/python
```

4. 部署应用：
```bash
git push heroku main
```

### 配置注意事项
需要创建Procfile文件：
```
web: python web.py
```

## 推荐方案

对于网络监控系统，我推荐以下方案：

1. **开发和测试**：使用GitHub Codespaces，免费且功能完整
2. **生产部署**：使用Render或Railway，简单易用且有免费额度
3. **长期运行**：考虑使用付费的VPS服务，如阿里云、腾讯云的学生机

## 配置文件调整

部署到免费平台时，可能需要调整config.json中的配置：

```json
{
  "targets": ["8.8.8.8", "114.114.114.114", "www.baidu.com"],
  "check_interval": 60,
  "alert_cooldown": 600,
  "timeout": 5,
  "packet_count": 2,
  "statistics_window": 1800,
  "alert_threshold": 0.5,
  "email": {
    "enabled": true,
    "smtp_server": "smtp.mxhichina.com",
    "smtp_port": 587,
    "username": "your-email@example.com",
    "password": "your-email-password",
    "to_emails": ["admin@yourcompany.com"]
  },
  "webhook": {
    "enabled": true,
    "url": "https://oapi.dingtalk.com/robot/send?access_token=your-dingtalk-token"
  },
  "sms": {
    "enabled": false,
    "api_url": "https://sms.example.com/send"
  },
  "database": {
    "enabled": true,
    "retention_days": 7
  }
}
```

注意调整：
- 增加检查间隔以节省资源
- 增加报警冷却时间
- 减少数据保留天数以节省存储空间

## 监控和维护

1. 定期检查日志文件
2. 监控平台的免费额度使用情况
3. 根据需要调整配置参数
4. 备份重要的监控数据

## 故障排除

1. **部署失败**：
   - 检查依赖文件是否完整
   - 确认Python版本兼容性
   - 查看平台的构建日志

2. **运行异常**：
   - 检查环境变量配置
   - 确认网络连接权限
   - 查看应用日志

3. **性能问题**：
   - 调整检查间隔
   - 减少监控目标数量
   - 优化配置参数

通过以上指南，您可以将网络监控系统部署到各种免费的云服务平台上。根据您的具体需求和使用场景选择最适合的部署方案。