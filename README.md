# 网络专线监控系统

## 功能说明

这是一个专门针对联通100M专线设计的网络监控系统，可以部署在云服务器上持续监控网络连通性，并在网络中断时及时发出报警。

### 主要功能

1. **多目标监控**：同时监控多个目标的网络连通性
2. **多种检测方式**：支持Ping检测和DNS解析检测
3. **多重报警机制**：支持邮件、Webhook、短信等多种报警方式
4. **防骚扰机制**：避免因网络短暂波动导致的频繁报警
5. **状态恢复通知**：当网络恢复正常时会发送恢复通知
6. **详细日志记录**：完整记录网络状态变化历史

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

## 配置说明

配置文件`config.json`包含以下参数：

### 基本配置

- `targets`: 监控目标列表，可以是IP地址或域名
- `check_interval`: 检查间隔（秒）
- `alert_cooldown`: 报警冷却时间（秒），防止频繁报警

### 邮件报警配置

- `email.enabled`: 是否启用邮件报警
- `email.smtp_server`: SMTP服务器地址
- `email.smtp_port`: SMTP端口
- `email.username`: 邮箱用户名
- `email.password`: 邮箱密码或授权码
- `email.to_emails`: 接收报警邮件的邮箱列表

### Webhook报警配置

- `webhook.enabled`: 是否启用Webhook报警
- `webhook.url`: Webhook地址（如钉钉机器人地址）

### 短信报警配置

- `sms.enabled`: 是否启用短信报警
- `sms.api_url`: 短信API地址

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

## 高级监控系统

系统还包含一个高级监控版本 `advanced_network_monitor.py`，提供以下增强功能：

1. **数据库存储**：将监控数据存储在SQLite数据库中
2. **统计分析**：基于时间窗口的网络质量统计分析
3. **智能报警**：基于成功率阈值的智能报警机制
4. **数据清理**：自动清理过期数据
5. **详细报告**：实时显示网络状态和统计信息

### 高级版使用方法

```bash
# 使用高级监控系统
python advanced_network_monitor.py

# 测试模式（只执行一次检测）
python advanced_network_monitor.py --test
```

## 故障排查

1. **查看日志**：
   程序会生成`network_monitor.log`日志文件，包含详细的运行信息。

2. **常见问题**：
   - 如果无法发送邮件，请检查SMTP配置和网络连接
   - 如果无法访问Webhook，请检查URL是否正确和网络连接
   - 如果监控不准确，请调整检查间隔和目标列表

## 定制开发

如果需要添加其他报警方式或功能，可以直接修改`network_monitor.py`文件：

1. 添加新的报警方法
2. 在`send_alert`方法中调用新的报警方法
3. 在配置文件中添加相应的配置项

## 注意事项

1. 请定期检查日志文件，确保监控系统正常运行
2. 请及时更新配置文件中的联系人信息
3. 建议定期测试报警功能是否正常工作
4. 在生产环境中建议使用系统服务方式运行