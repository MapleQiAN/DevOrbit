# DevOrbit Backend

个人开发者数字履历聚合平台的后端服务。

## 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.x
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT + GitHub OAuth
- **迁移**: Alembic

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

关键配置项：
- `DATABASE_URL`: 数据库连接字符串
- `GITHUB_CLIENT_ID` 和 `GITHUB_CLIENT_SECRET`: GitHub OAuth 应用凭证
- `JWT_SECRET_KEY`: JWT 签名密钥

### 3. 初始化数据库

```bash
# 创建数据库表
python3 -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"

# 或使用 Alembic（后续）
alembic upgrade head
```

### 4. 启动服务

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

或使用启动脚本：

```bash
chmod +x run.sh
./run.sh
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 验证服务状态

```bash
curl http://localhost:8000/health
# 返回: {"status": "ok"}
```

## 项目结构

```
app/
├── main.py              # FastAPI 应用入口
├── core/
│   ├── config.py        # 配置管理
│   └── security.py      # JWT 和安全工具
├── db/
│   ├── base.py          # SQLAlchemy declarative base
│   └── session.py       # 数据库连接和会话
├── models/              # 数据模型
│   ├── user.py
│   ├── github_repo.py
│   └── github_event.py
├── schemas/             # Pydantic 数据验证模型
├── api/
│   └── v1/
│       └── endpoints/   # API 端点
└── services/            # 业务逻辑服务
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/schemas/` 中定义请求/响应 schema
2. 在 `app/api/v1/endpoints/` 中创建新的路由文件
3. 在 `app/main.py` 中注册路由

### 添加新的数据模型

1. 在 `app/models/` 中创建模型类
2. 创建 Alembic 迁移：`alembic revision --autogenerate -m "description"`
3. 执行迁移：`alembic upgrade head`

## 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./devorbit.db` |
| `GITHUB_CLIENT_ID` | GitHub OAuth 应用 ID | - |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth 应用密钥 | - |
| `JWT_SECRET_KEY` | JWT 签名密钥 | - |
| `JWT_EXPIRE_MINUTES` | JWT 过期时间（分钟） | `10080` |
| `CORS_ORIGINS` | 允许的 CORS 源 | `["http://localhost:5173"]` |

## 常见问题

### 数据库连接错误

确保 `DATABASE_URL` 正确配置，SQLite 会自动创建数据库文件。

### GitHub OAuth 配置

1. 访问 https://github.com/settings/developers
2. 创建新的 OAuth App
3. 设置 Authorization callback URL 为 `http://localhost:3000/auth/github/callback`
4. 复制 Client ID 和 Client Secret 到 `.env` 文件

## 下一步

- [ ] Stage 2: 实现 GitHub OAuth 认证
- [ ] Stage 3: 实现 GitHub 数据同步
- [ ] Stage 4: 前端项目初始化
- [ ] Stage 5: 前端仪表盘实现

