# 网络监控系统Makefile

# 默认目标
.PHONY: help build up down logs status restart clean

# 显示帮助信息
help:
	@echo "网络监控系统 Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make build        - 构建Docker镜像"
	@echo "  make up           - 启动服务"
	@echo "  make down         - 停止并删除服务"
	@echo "  make logs         - 查看日志"
	@echo "  make status       - 查看服务状态"
	@echo "  make restart      - 重启服务"
	@echo "  make clean        - 清理构建文件"
	@echo "  make prod-up      - 启动生产环境服务"
	@echo "  make prod-down    - 停止并删除生产环境服务"
	@echo "  make prod-logs    - 查看生产环境日志"
	@echo "  make backup       - 备份数据"
	@echo "  make restore      - 恢复数据"

# 构建Docker镜像
build:
	docker-compose build

# 启动服务
up:
	docker-compose up -d

# 停止并删除服务
down:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f

# 查看服务状态
status:
	docker-compose ps

# 重启服务
restart:
	docker-compose restart

# 清理构建文件
clean:
	docker-compose down --rmi all
	rm -rf data logs

# 生产环境操作
prod-up:
	docker-compose -f docker-compose.production.yml up -d

prod-down:
	docker-compose -f docker-compose.production.yml down

prod-logs:
	docker-compose -f docker-compose.production.yml logs -f

prod-status:
	docker-compose -f docker-compose.production.yml ps

# 数据备份和恢复
backup:
	@echo "备份数据..."
	mkdir -p backups
	docker-compose exec network-monitor cp /app/network_stats.db /app/data/backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "数据备份完成"

restore:
	@echo "恢复数据..."
	@echo "请手动将备份文件复制到data目录并重命名为network_stats.db"
	@echo "或者使用以下命令:"
	@echo "docker-compose exec network-monitor cp /app/data/backup_XXXXXX.db /app/network_stats.db"

# 更新代码并重新部署
update:
	git pull origin main
	docker-compose down
	docker-compose build
	docker-compose up -d
	docker-compose ps

# 健康检查
health:
	docker-compose exec network-monitor python health_check.py