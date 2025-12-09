.PHONY: help build up down logs restart clean test lint format

# 颜色定义
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## 显示帮助信息
	@echo "$(BLUE)DevOrbit Docker 命令帮助$(NC)"
	@echo ""
	@echo "$(GREEN)启动和停止:$(NC)"
	@echo "  make up              启动所有服务"
	@echo "  make down            停止所有服务"
	@echo "  make restart         重启所有服务"
	@echo "  make build           构建 Docker 镜像"
	@echo "  make rebuild         重新构建镜像（不使用缓存）"
	@echo ""
	@echo "$(GREEN)日志和监控:$(NC)"
	@echo "  make logs            查看所有服务日志"
	@echo "  make logs-backend    查看后端日志"
	@echo "  make logs-frontend   查看前端日志"
	@echo "  make logs-db         查看数据库日志"
	@echo "  make ps              查看容器状态"
	@echo "  make stats           查看容器资源使用"
	@echo ""
	@echo "$(GREEN)容器操作:$(NC)"
	@echo "  make shell-backend   进入后端容器"
	@echo "  make shell-frontend  进入前端容器"
	@echo "  make shell-db        进入数据库容器"
	@echo ""
	@echo "$(GREEN)数据库操作:$(NC)"
	@echo "  make migrate         运行数据库迁移"
	@echo "  make backup          备份数据库"
	@echo "  make restore         恢复数据库"
	@echo ""
	@echo "$(GREEN)开发工具:$(NC)"
	@echo "  make test            运行测试"
	@echo "  make lint            代码检查"
	@echo "  make format          代码格式化"
	@echo "  make clean           清理临时文件"
	@echo ""
	@echo "$(GREEN)环境配置:$(NC)"
	@echo "  make env             创建 .env 文件"
	@echo "  make env-show        显示环境变量"
	@echo ""

# ============================================
# 启动和停止
# ============================================

up: ## 启动所有服务
	@echo "$(BLUE)启动 DevOrbit...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ 服务已启动$(NC)"
	@make ps

down: ## 停止所有服务
	@echo "$(BLUE)停止 DevOrbit...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ 服务已停止$(NC)"

restart: ## 重启所有服务
	@echo "$(BLUE)重启 DevOrbit...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✅ 服务已重启$(NC)"
	@make ps

build: ## 构建 Docker 镜像
	@echo "$(BLUE)构建镜像...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ 镜像构建完成$(NC)"

rebuild: ## 重新构建镜像（不使用缓存）
	@echo "$(BLUE)重新构建镜像...$(NC)"
	docker-compose build --no-cache
	@echo "$(GREEN)✅ 镜像重建完成$(NC)"

# ============================================
# 日志和监控
# ============================================

logs: ## 查看所有服务日志
	docker-compose logs -f

logs-backend: ## 查看后端日志
	docker-compose logs -f backend

logs-frontend: ## 查看前端日志
	docker-compose logs -f frontend

logs-db: ## 查看数据库日志
	docker-compose logs -f db

ps: ## 查看容器状态
	@echo "$(BLUE)容器状态:$(NC)"
	@docker-compose ps

stats: ## 查看容器资源使用
	docker stats

# ============================================
# 容器操作
# ============================================

shell-backend: ## 进入后端容器
	docker-compose exec backend bash

shell-frontend: ## 进入前端容器
	docker-compose exec frontend sh

shell-db: ## 进入数据库容器
	docker-compose exec db psql -U devorbit -d devorbit

# ============================================
# 数据库操作
# ============================================

migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(NC)"
	docker-compose exec backend alembic upgrade head
	@echo "$(GREEN)✅ 迁移完成$(NC)"

migrate-status: ## 查看迁移状态
	docker-compose exec backend alembic current

migrate-history: ## 查看迁移历史
	docker-compose exec backend alembic history

backup: ## 备份数据库
	@echo "$(BLUE)备份数据库...$(NC)"
	@mkdir -p backups
	@docker-compose exec -T db pg_dump -U devorbit devorbit | gzip > backups/db_backup_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "$(GREEN)✅ 备份完成$(NC)"

restore: ## 恢复数据库
	@echo "$(BLUE)恢复数据库...$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)⚠️  请指定备份文件: make restore FILE=backups/db_backup_*.sql.gz$(NC)"; \
		exit 1; \
	fi
	@gunzip -c $(FILE) | docker-compose exec -T db psql -U devorbit devorbit
	@echo "$(GREEN)✅ 恢复完成$(NC)"

# ============================================
# 开发工具
# ============================================

test: ## 运行测试
	@echo "$(BLUE)运行测试...$(NC)"
	docker-compose exec backend pytest -v

lint: ## 代码检查
	@echo "$(BLUE)运行代码检查...$(NC)"
	docker-compose exec backend ruff check app/
	docker-compose exec backend mypy app/

format: ## 代码格式化
	@echo "$(BLUE)格式化代码...$(NC)"
	docker-compose exec backend black app/
	docker-compose exec backend ruff check --fix app/

# ============================================
# 环境配置
# ============================================

env: ## 创建 .env 文件
	@if [ -f ".env" ]; then \
		echo "$(YELLOW)⚠️  .env 文件已存在$(NC)"; \
	else \
		cp .env.example .env; \
		echo "$(GREEN)✅ .env 文件已创建$(NC)"; \
		echo "$(YELLOW)⚠️  请编辑 .env 文件，填入必要的配置$(NC)"; \
	fi

env-show: ## 显示环境变量
	@echo "$(BLUE)环境变量:$(NC)"
	@grep -v "^#" .env | grep -v "^$$"

# ============================================
# 清理
# ============================================

clean: ## 清理临时文件和容器
	@echo "$(BLUE)清理临时文件...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "$(GREEN)✅ 清理完成$(NC)"

clean-all: clean ## 清理所有（包括容器和卷）
	@echo "$(BLUE)清理所有容器和卷...$(NC)"
	docker-compose down -v
	@echo "$(GREEN)✅ 清理完成$(NC)"

# ============================================
# 健康检查
# ============================================

health: ## 检查服务健康状态
	@echo "$(BLUE)检查服务健康状态...$(NC)"
	@echo ""
	@echo "后端 API:"
	@curl -s http://localhost:8000/health || echo "$(YELLOW)❌ 无法连接$(NC)"
	@echo ""
	@echo "前端应用:"
	@curl -s http://localhost/health || echo "$(YELLOW)❌ 无法连接$(NC)"
	@echo ""
	@echo "数据库:"
	@docker-compose exec db pg_isready -U devorbit || echo "$(YELLOW)❌ 无法连接$(NC)"
	@echo ""

# ============================================
# 快速启动
# ============================================

quick-start: env build up ## 快速启动（创建 .env、构建、启动）
	@echo ""
	@echo "$(GREEN)✅ DevOrbit 已启动！$(NC)"
	@echo ""
	@echo "访问地址:"
	@echo "  🌐 前端: http://localhost"
	@echo "  🔌 API:  http://localhost:8000"
	@echo "  📚 文档: http://localhost:8000/docs"
	@echo ""

# ============================================
# 默认目标
# ============================================

.DEFAULT_GOAL := help

