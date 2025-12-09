# 🐳 DevOrbit Docker 一键部署指南

## 📋 目录

1. [快速开始](#快速开始)
2. [前置条件](#前置条件)
3. [部署步骤](#部署步骤)
4. [配置说明](#配置说明)
5. [常见问题](#常见问题)
6. [监控和维护](#监控和维护)
7. [生产部署](#生产部署)

---

## 🚀 快速开始

### 最简单的方式（3 步）

```bash
# 1. 克隆项目
git clone <repository-url>
cd DevOrbit

# 2. 复制环境配置
cp .env.example .env
# 编辑 .env，填入 GitHub OAuth 凭证等信息

# 3. 一键启动
docker-compose up -d
```

**完成！** 应用现在运行在：
- 🌐 前端: http://localhost
- 🔌 后端 API: http://localhost:8000
- 📚 API 文档: http://localhost:8000/docs

---

## 📦 前置条件

### 必需

- **Docker** >= 20.10
  ```bash
  # 检查 Docker 版本
  docker --version
  ```

- **Docker Compose** >= 1.29
  ```bash
  # 检查 Docker Compose 版本
  docker-compose --version
  ```

### 推荐

- **Git** - 用于克隆项目
- **curl** 或 **Postman** - 用于测试 API

### 系统要求

| 资源 | 最低要求 | 推荐配置 |
|------|---------|--------|
| CPU | 2 核 | 4 核 |
| 内存 | 2 GB | 4 GB |
| 磁盘 | 5 GB | 20 GB |
| 网络 | 100 Mbps | 1 Gbps |

---

## 🔧 部署步骤

### 第 1 步：准备环境

```bash
# 1.1 克隆项目
git clone <repository-url>
cd DevOrbit

# 1.2 检查 Docker 状态
docker ps
docker-compose --version

# 1.3 创建环境配置文件
cp .env.example .env
```

### 第 2 步：配置环境变量

编辑 `.env` 文件，填入必要的配置：

```bash
# 使用你喜欢的编辑器打开 .env
nano .env
# 或
vim .env
# 或
code .env  # VS Code
```

**必填项：**

```env
# GitHub OAuth 配置（从 https://github.com/settings/developers 获取）
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here

# JWT 密钥（生成方式见下文）
JWT_SECRET_KEY=your_generated_secret_key
```

**生成 JWT 密钥：**

```bash
# 方式 1: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方式 2: OpenSSL
openssl rand -base64 32

# 方式 3: Docker
docker run --rm python:3.10 python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 第 3 步：启动应用

```bash
# 3.1 启动所有服务（后台运行）
docker-compose up -d

# 3.2 查看启动日志
docker-compose logs -f

# 3.3 等待服务就绪（约 30-60 秒）
docker-compose ps
```

### 第 4 步：验证部署

```bash
# 4.1 检查服务状态
docker-compose ps

# 4.2 测试后端 API
curl http://localhost:8000/health
# 预期输出: {"status":"ok"}

# 4.3 测试前端
curl http://localhost/health
# 预期输出: healthy

# 4.4 访问应用
# 前端: http://localhost
# API 文档: http://localhost:8000/docs
```

---

## ⚙️ 配置说明

### 环境变量详解

#### 数据库配置

```env
# PostgreSQL 用户名
DB_USER=devorbit

# PostgreSQL 密码（强烈建议修改）
DB_PASSWORD=devorbit_password

# 数据库名称
DB_NAME=devorbit

# PostgreSQL 端口
DB_PORT=5432
```

#### GitHub OAuth 配置

```env
# GitHub OAuth 应用 ID
GITHUB_CLIENT_ID=your_client_id

# GitHub OAuth 应用密钥
GITHUB_CLIENT_SECRET=your_client_secret

# OAuth 回调 URL（必须与 GitHub 应用设置一致）
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
```

**获取 GitHub OAuth 凭证：**

1. 访问 https://github.com/settings/developers
2. 点击 "New OAuth App"
3. 填写应用信息：
   - **Application name**: DevOrbit
   - **Homepage URL**: http://localhost:3000
   - **Authorization callback URL**: http://localhost:3000/auth/github/callback
4. 复制 Client ID 和 Client Secret 到 `.env`

#### JWT 配置

```env
# JWT 签名密钥（用于生成和验证 token）
JWT_SECRET_KEY=your-secret-key

# JWT 算法
JWT_ALGORITHM=HS256

# Token 过期时间（分钟）
JWT_EXPIRE_MINUTES=30
```

#### CORS 配置

```env
# 允许的源（逗号分隔）
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost
```

#### 应用配置

```env
# 运行环境（development/production）
ENVIRONMENT=production

# 调试模式（true/false）
DEBUG=false

# 后端 API 端口
BACKEND_PORT=8000

# 前端应用端口
FRONTEND_PORT=80

# Redis 缓存端口
REDIS_PORT=6379
```

### Docker Compose 服务

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| `db` | devorbit-db | 5432 | PostgreSQL 数据库 |
| `backend` | devorbit-backend | 8000 | FastAPI 后端 API |
| `frontend` | devorbit-frontend | 80 | Vue 3 前端应用 |
| `redis` | devorbit-redis | 6379 | Redis 缓存（可选） |

---

## 🛠️ 常见操作

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# 查看最后 100 行日志
docker-compose logs --tail=100
```

### 停止和启动

```bash
# 停止所有服务
docker-compose stop

# 启动所有服务
docker-compose start

# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend

# 停止并删除容器（保留数据）
docker-compose down

# 停止并删除容器和数据卷
docker-compose down -v
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec db psql -U devorbit -d devorbit

# 进入前端容器
docker-compose exec frontend sh
```

### 查看容器状态

```bash
# 查看所有容器
docker-compose ps

# 查看容器详细信息
docker-compose ps -a

# 查看容器资源使用情况
docker stats
```

### 数据库操作

```bash
# 连接数据库
docker-compose exec db psql -U devorbit -d devorbit

# 查看所有表
\dt

# 查看表结构
\d users

# 退出数据库
\q
```

### 运行数据库迁移

```bash
# 手动运行迁移
docker-compose exec backend alembic upgrade head

# 查看迁移历史
docker-compose exec backend alembic history

# 回滚到上一个版本
docker-compose exec backend alembic downgrade -1
```

---

## ❓ 常见问题

### Q1: 容器无法启动

**症状**: `docker-compose up` 失败

**解决方案**:

```bash
# 1. 检查日志
docker-compose logs

# 2. 检查端口是否被占用
lsof -i :8000
lsof -i :80
lsof -i :5432

# 3. 清理并重新启动
docker-compose down -v
docker-compose up -d
```

### Q2: 数据库连接失败

**症状**: `ERROR: could not connect to server`

**解决方案**:

```bash
# 1. 检查数据库容器状态
docker-compose ps db

# 2. 查看数据库日志
docker-compose logs db

# 3. 等待数据库就绪（约 10 秒）
sleep 10
docker-compose restart backend

# 4. 检查网络连接
docker-compose exec backend ping db
```

### Q3: 前端无法访问后端 API

**症状**: CORS 错误或连接超时

**解决方案**:

```bash
# 1. 检查 CORS 配置
# 编辑 .env，确保 CORS_ORIGINS 包含前端 URL

# 2. 检查网络连接
docker-compose exec frontend ping backend

# 3. 检查 Nginx 配置
docker-compose exec frontend cat /etc/nginx/nginx.conf

# 4. 重启前端服务
docker-compose restart frontend
```

### Q4: 磁盘空间不足

**症状**: `no space left on device`

**解决方案**:

```bash
# 1. 清理未使用的镜像
docker image prune -a

# 2. 清理未使用的容器
docker container prune

# 3. 清理未使用的卷
docker volume prune

# 4. 查看磁盘使用情况
docker system df
```

### Q5: 忘记 GitHub OAuth 凭证

**症状**: 无法登录

**解决方案**:

```bash
# 1. 获取新的凭证
# 访问 https://github.com/settings/developers

# 2. 更新 .env 文件
nano .env

# 3. 重启后端服务
docker-compose restart backend
```

### Q6: 数据库迁移失败

**症状**: `Alembic migration failed`

**解决方案**:

```bash
# 1. 检查迁移状态
docker-compose exec backend alembic current

# 2. 查看迁移历史
docker-compose exec backend alembic history

# 3. 手动运行迁移
docker-compose exec backend alembic upgrade head

# 4. 如果失败，查看错误日志
docker-compose logs backend
```

---

## 📊 监控和维护

### 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查前端健康状态
curl http://localhost/health

# 检查数据库连接
docker-compose exec db pg_isready -U devorbit
```

### 性能监控

```bash
# 实时监控容器资源使用
docker stats

# 查看容器进程
docker-compose top backend

# 查看容器网络统计
docker stats --no-stream
```

### 日志分析

```bash
# 查看错误日志
docker-compose logs --tail=50 | grep -i error

# 查看特定时间范围的日志
docker-compose logs --since 2025-12-09T10:00:00

# 导出日志到文件
docker-compose logs > app.log
```

### 备份和恢复

```bash
# 备份数据库
docker-compose exec db pg_dump -U devorbit devorbit > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U devorbit devorbit < backup.sql

# 备份数据卷
docker run --rm -v devorbit_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

---

## 🚀 生产部署

### 生产环境检查清单

- [ ] 修改所有默认密码
- [ ] 生成强 JWT 密钥
- [ ] 配置 GitHub OAuth 凭证
- [ ] 设置 CORS 允许的源
- [ ] 启用 HTTPS/SSL
- [ ] 配置备份策略
- [ ] 设置监控告警
- [ ] 配置日志收集
- [ ] 进行安全审计
- [ ] 进行性能测试

### 生产环境配置

```env
# 生产环境
ENVIRONMENT=production
DEBUG=false

# 强密码
DB_PASSWORD=very_strong_password_here
JWT_SECRET_KEY=very_long_random_secret_key_here

# 生产域名
GITHUB_REDIRECT_URI=https://yourdomain.com/auth/github/callback
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 生产数据库
DATABASE_URL=postgresql://devorbit:password@db:5432/devorbit
```

### 使用 Nginx 反向代理

创建 `nginx-prod.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # 前端
    location / {
        proxy_pass http://frontend;
    }
    
    # 后端 API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 自动备份脚本

创建 `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
docker-compose exec -T db pg_dump -U devorbit devorbit | \
    gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# 保留最近 7 天的备份
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sql.gz"
```

运行备份：

```bash
# 添加到 crontab（每天凌晨 2 点执行）
0 2 * * * /path/to/backup.sh
```

---

## 📚 相关文档

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Docker 镜像](https://hub.docker.com/_/postgres)

---

## 🆘 获取帮助

如遇到问题，请：

1. 查看 [常见问题](#常见问题) 部分
2. 检查 Docker 日志: `docker-compose logs`
3. 查看项目 GitHub Issues
4. 提交新 Issue 并包含：
   - 错误信息
   - Docker 版本
   - 操作系统
   - 完整的日志输出

---

**最后更新**: 2025-12-09  
**版本**: 1.0.0

