# 🐳 Docker 快速参考指南

## 📋 快速命令速查表

### 🚀 启动和停止

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 重启所有服务
docker-compose restart

# 重新构建镜像
docker-compose build --no-cache
```

### 📊 查看状态

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 查看资源使用情况
docker stats
```

### 🔧 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec db psql -U devorbit -d devorbit

# 进入前端容器
docker-compose exec frontend sh
```

### 🗄️ 数据库操作

```bash
# 运行迁移
docker-compose exec backend alembic upgrade head

# 查看迁移状态
docker-compose exec backend alembic current

# 备份数据库
docker-compose exec -T db pg_dump -U devorbit devorbit > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U devorbit devorbit < backup.sql
```

---

## 🎯 使用 Makefile 快速操作

如果项目包含 Makefile，可以使用以下命令：

```bash
# 显示所有可用命令
make help

# 启动服务
make up

# 停止服务
make down

# 查看日志
make logs
make logs-backend

# 进入容器
make shell-backend
make shell-db

# 数据库操作
make migrate
make backup

# 代码检查和格式化
make lint
make format

# 快速启动（一键）
make quick-start
```

---

## 🛠️ 使用启动脚本快速操作

如果项目包含启动脚本，可以使用以下命令：

```bash
# 开发模式启动
./start.sh

# 生产模式启动
./start.sh --prod

# 重新构建并启动
./start.sh --build

# 启动并显示日志
./start.sh --logs

# 停止服务
./stop.sh

# 强制停止
./stop.sh --force

# 强制停止并删除数据
./stop.sh --force --volumes
```

---

## 📝 环境配置

### 创建 .env 文件

```bash
# 从示例创建
cp .env.example .env

# 编辑配置
nano .env
```

### 必填项

```env
# GitHub OAuth
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret

# JWT 密钥
JWT_SECRET_KEY=your_secret_key
```

### 生成 JWT 密钥

```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Docker
docker run --rm python:3.10 python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔍 故障排查

### 容器无法启动

```bash
# 查看详细错误
docker-compose logs backend

# 检查端口是否被占用
lsof -i :8000
lsof -i :80

# 清理并重新启动
docker-compose down -v
docker-compose up -d
```

### 数据库连接失败

```bash
# 检查数据库容器
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 等待数据库就绪后重启后端
sleep 10
docker-compose restart backend
```

### 前端无法访问后端

```bash
# 检查网络连接
docker-compose exec frontend ping backend

# 检查 CORS 配置
grep CORS_ORIGINS .env

# 查看 Nginx 配置
docker-compose exec frontend cat /etc/nginx/nginx.conf
```

---

## 📊 监控和性能

### 实时监控

```bash
# 监控容器资源使用
docker stats

# 查看容器进程
docker-compose top backend

# 查看网络统计
docker network inspect devorbit_devorbit-network
```

### 日志分析

```bash
# 查看错误日志
docker-compose logs | grep -i error

# 查看最后 100 行
docker-compose logs --tail=100

# 导出日志
docker-compose logs > app.log
```

---

## 🔐 安全操作

### 修改密码

```bash
# 进入数据库
docker-compose exec db psql -U devorbit -d devorbit

# 修改用户密码
ALTER USER devorbit WITH PASSWORD 'new_password';

# 退出
\q
```

### 更新环境变量

```bash
# 编辑 .env
nano .env

# 重启服务
docker-compose restart
```

---

## 🧹 清理和维护

### 清理未使用的资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 查看磁盘使用情况
docker system df
```

### 备份和恢复

```bash
# 备份数据库
docker-compose exec -T db pg_dump -U devorbit devorbit | gzip > backup.sql.gz

# 恢复数据库
gunzip -c backup.sql.gz | docker-compose exec -T db psql -U devorbit devorbit

# 备份整个卷
docker run --rm -v devorbit_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

---

## 🌐 访问应用

| 服务 | URL | 说明 |
|------|-----|------|
| 前端 | http://localhost | Vue 3 应用 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | ReDoc 文档 |
| 健康检查 | http://localhost:8000/health | 后端健康状态 |
| 数据库 | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | Redis 缓存 |

---

## 📚 常用组合命令

### 完整重启

```bash
# 停止、删除、重建、启动
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### 查看完整日志

```bash
# 显示所有日志并跟踪新日志
docker-compose logs -f --tail=50
```

### 数据库完整备份和恢复

```bash
# 备份
docker-compose exec -T db pg_dump -U devorbit devorbit | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# 恢复
gunzip -c backup_*.sql.gz | docker-compose exec -T db psql -U devorbit devorbit
```

### 清理所有数据并重新初始化

```bash
docker-compose down -v && docker-compose up -d
```

---

## 🆘 获取帮助

```bash
# Docker 帮助
docker --help
docker-compose --help

# 查看特定命令帮助
docker-compose up --help
docker-compose logs --help

# 查看项目文档
cat DOCKER_DEPLOYMENT.md
```

---

## 📖 相关资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Docker 镜像](https://hub.docker.com/_/postgres)

---

**最后更新**: 2025-12-09

