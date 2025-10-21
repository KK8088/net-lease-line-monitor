# 联通100M专线网络监控系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
[![CI/CD](https://github.com/KK8088/net-lease-line-monitor/actions/workflows/deploy.yml/badge.svg)](https://github.com/KK8088/net-lease-line-monitor/actions/workflows/deploy.yml)

## 项目简介

这是一个专门针对联通100M专线设计的网络监控系统，可以部署在云服务器上持续监控网络连通性，并在网络中断时及时发出报警。

该系统可以帮助IT管理员及时发现网络中断问题，通过多种报警方式确保问题得到及时处理，提高网络服务的可用性。

## 功能特性

### 基础功能
- **多目标监控**：同时监控多个目标的网络连通性（IP地址和域名）
- **多种检测方式**：支持Ping检测和DNS解析检测
- **多重报警机制**：支持邮件、Webhook（钉钉等）、短信等多种报警方式
- **防骚扰机制**：避免因网络短暂波动导致的频繁报警
- **状态恢复通知**：当网络恢复正常时会发送恢复通知
- **详细日志记录**：完整记录网络状态变化历史

### 高级功能
- **数据库存储**：将监控数据存储在SQLite数据库中
- **统计分析**：基于时间窗口的网络质量统计分析
- **智能报警**：基于成功率阈值的智能报警机制
- **数据清理**：自动清理过期数据
- **详细报告**：实时显示网络状态和统计信息

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   监控目标      │    │  网络监控系统    │    │   报警通知      │
│  (IP/域名)      │───▶│ (Python脚本)     │───▶│ (邮件/Webhook)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌───────────────┐
                       │  数据存储     │
                       │ (SQLite DB)   │
                       └───────────────┘
```

## 快速开始

### 环境要求
- Python 3.6 或更高版本
- Windows/Linux/macOS 操作系统
- 网络连接

### 安装步骤

1. 克隆或下载本仓库
```bash
git clone https://github.com/KK8088/net-lease-line-monitor.git
cd net-lease-line-monitor
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置监控参数
编辑 `config.json` 文件，设置监控目标和报警方式

4. 运行监控程序
```bash
# 基础版本
python network_monitor.py

# 高级版本（推荐）
python advanced_network_monitor.py
```

## 配置说明

配置文件 `config.json` 包含以下主要参数：

### 基本配置
```json
{
  "targets": ["8.8.8.8", "www.baidu.com"],
  "check_interval": 30,
  "alert_cooldown": 300,
  "timeout": 5,
  "packet_count": 4,
  "statistics_window": 3600,
  "alert_threshold": 0.5
}
```

### 邮件报警配置
```json
"email": {
  "enabled": true,
  "smtp_server": "smtp.mxhichina.com",
  "smtp_port": 587,
  "username": "admin@yourcompany.com",
  "password": "your_email_password",
  "to_emails": ["it-admin@yourcompany.com"]
}
```

### Webhook报警配置
```json
"webhook": {
  "enabled": true,
  "url": "https://oapi.dingtalk.com/robot/send?access_token=your_dingtalk_token"
}
```

## 部署指南

### Windows系统部署

1. 确保已安装Python 3.6或更高版本
2. 下载所有文件到本地目录
3. 根据需要修改`config.json`配置文件
4. 双击运行`start_monitor.bat`启动监控程序

### Linux系统部署

1. 确保已安装Python 3.6或更高版本
2. 下载所有文件到本地目录（建议使用`/opt/network-monitor/`目录）
3. 根据需要修改`config.json`配置文件
4. 运行以下命令安装依赖：
   ```bash
   chmod +x start_monitor.sh
   ./start_monitor.sh
   ```

### 作为系统服务运行（Linux）

1. 将文件复制到`/opt/network-monitor/`目录：
   ```bash
   sudo mkdir -p /opt/network-monitor
   sudo cp -r * /opt/network-monitor/
   cd /opt/network-monitor
   ```

2. 修改service文件中的路径（如需要）：
   ```bash
   sudo nano network-monitor.service
   ```

3. 安装并启动服务：
   ```bash
   sudo cp network-monitor.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable network-monitor
   sudo systemctl start network-monitor
   ```

4. 查看服务状态：
   ```bash
   sudo systemctl status network-monitor
   ```

### Docker部署

使用Docker和Docker Compose可以简化部署过程：

```bash
# 构建并启动容器
docker-compose up -d

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 使用建议

1. **监控目标选择**：
   - 建议包含国内外不同地区的IP和域名
   - 包含一些关键业务系统的地址
   
2. **报警策略**：
   - 合理设置报警冷却时间，避免频繁报警
   - 多种报警方式结合使用，确保通知到位

3. **部署位置**：
   - 建议部署在与联通专线不同的网络环境中
   - 可以考虑部署在多个云服务商的服务器上

## 故障排查

1. **查看日志**：
   程序会生成`network_monitor.log`日志文件，包含详细的运行信息。

2. **常见问题**：
   - 如果无法发送邮件，请检查SMTP配置和网络连接
   - 如果无法访问Webhook，请检查URL是否正确和网络连接
   - 如果监控不准确，请调整检查间隔和目标列表

## API接口

高级版本提供以下命令行参数：

```bash
# 标准运行模式
python advanced_network_monitor.py

# 测试模式（只执行一次检测）
python advanced_network_monitor.py --test

# 指定配置文件
python advanced_network_monitor.py --config /path/to/config.json

# 指定数据库文件
python advanced_network_monitor.py --db /path/to/database.db
```

## 数据库结构

系统使用SQLite数据库存储监控数据，主要包含以下表：

1. `network_status`：存储每次检测的详细结果
2. `network_statistics`：存储统计分析结果

## 定制开发

如果需要添加其他报警方式或功能，可以直接修改源代码：

1. 添加新的报警方法到NetworkMonitor类
2. 在`send_alert`方法中调用新的报警方法
3. 在配置文件中添加相应的配置项

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

## 持续集成/持续部署 (CI/CD)

本项目使用GitHub Actions进行持续集成和持续部署：

- **测试**: 自动运行代码语法检查和单元测试
- **构建**: 自动构建Docker镜像
- **发布**: 自动创建GitHub Release

工作流文件位于 [.github/workflows/deploy.yml](.github/workflows/deploy.yml)。

要启用完整的CI/CD功能，您需要在GitHub仓库设置中配置以下Secrets：

- `DOCKERHUB_USERNAME`: Docker Hub用户名
- `DOCKERHUB_TOKEN`: Docker Hub访问令牌
- `ALIBABA_CLOUD_HOST`: 阿里云服务器IP地址
- `ALIBABA_CLOUD_USERNAME`: 阿里云服务器用户名
- `ALIBABA_CLOUD_SSH_KEY`: 阿里云服务器SSH私钥
- `WEBHOOK_URL`: 部署完成通知Webhook URL

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

项目维护者： [Zk0x0](https://github.com/Zk0x0)

项目链接：[https://github.com/KK8088/net-lease-line-monitor](https://github.com/KK8088/net-lease-line-monitor)

## 更新日志

### v1.0.0
- 初始版本发布
- 基础网络监控功能
- 多种报警方式支持
- 配置文件支持
- 日志记录功能

### v1.1.0
- 添加高级监控版本
- 数据库存储支持
- 统计分析功能
- 健康检查工具
- Docker支持