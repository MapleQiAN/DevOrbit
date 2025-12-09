# DevOrbit 本地开发环境设置指南

本文档详细说明如何在本地搭建并运行 DevOrbit 项目。

## 前置要求

### 系统要求

- **操作系统**: Windows / macOS / Linux
- **Python**: 3.10 或更高版本
- **Node.js**: 16.0 或更高版本
- **npm** 或 **yarn**: 用于前端包管理

### 检查环境

```bash
# 检查 Python 版本
python --version
# 或
python3 --version

# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version
```

如果版本不符，请访问以下链接下载安装：

- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

## Stage 1: 后端初始化（当前阶段）

### 步骤 1: 克隆项目

```bash
git clone https://github.com/your-username/DevOrbit.git
cd DevOrbit
```

### 步骤 2: 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 步骤 3: 安装后端依赖

```bash
cd backend

# 安装项目依赖
pip install -e .

# 或者使用 requirements.txt（如果存在）
pip install -r requirements.txt
```

### 步骤 4: 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入必要的配置
# 关键配置项：
# - DATABASE_URL: 数据库连接字符串（开发环境默认 SQLite）
# - GITHUB_CLIENT_ID: GitHub OAuth 应用 ID（暂时可留空，Stage 2 需要）
# - GITHUB_CLIENT_SECRET: GitHub OAuth 应用密钥（暂时可留空，Stage 2 需要）
# - JWT_SECRET_KEY: JWT 签名密钥（已有默认值，生产环境需修改）
```

### 步骤 5: 初始化数据库

```bash
# 方式 1: 直接创建表（Stage 1 使用）
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine); print('✓ Database initialized')"

# 方式 2: 使用 Alembic（后续阶段）
# alembic upgrade head
```

### 步骤 6: 启动后端服务

```bash
# 方式 1: 使用 uvicorn 直接启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方式 2: 使用启动脚本（如果有）
# chmod +x run.sh
# ./run.sh
```

你应该看到类似的输出：

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 步骤 7: 验证后端

在另一个终端窗口中，测试 API：

```bash
# 测试健康检查
curl http://localhost:8000/health

# 预期返回:
# {"status":"ok"}

# 查看 API 文档
# 在浏览器中打开: http://localhost:8000/docs
```

---

## 项目结构说明（Stage 1）

```
DevOrbit/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI 应用入口
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # 配置管理（从 .env 读取）
│   │   │   └── security.py            # JWT 工具函数
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # SQLAlchemy declarative base
│   │   │   └── session.py             # 数据库连接和会话管理
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # 用户模型
│   │   │   ├── github_repo.py         # GitHub 仓库模型
│   │   │   └── github_event.py        # GitHub 每日统计模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # 用户 Pydantic schema
│   │   │   ├── auth.py                # 认证 schema
│   │   │   └── github.py              # GitHub schema
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # 依赖注入函数
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── health.py      # 健康检查端点 ✓ 已实现
│   │   │           ├── auth.py        # OAuth 端点（Stage 2）
│   │   │           └── github.py      # GitHub 数据端点（Stage 3）
│   │   └── services/
│   │       ├── __init__.py
│   │       └── github_sync.py         # GitHub 数据同步服务（Stage 3）
│   ├── alembic/                       # 数据库迁移配置
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   ├── versions/
│   │   └── __init__.py
│   ├── pyproject.toml                 # 项目配置和依赖声明
│   ├── .env.example                   # 环境变量示例
│   ├── .env                           # 本地环境变量（不提交到 git）
│   ├── alembic.ini                    # Alembic 配置
│   ├── run.sh                         # 启动脚本
│   └── README.md                      # 后端文档
│
├── frontend/                          # 前端项目（Stage 4 开始）
│   └── (待创建)
│
├── README.md                          # 项目总体文档
└── SETUP.md                           # 本文件
```

---

## 常见问题

### Q1: 如何修改数据库位置？

编辑 `.env` 文件中的 `DATABASE_URL`:

```env
# SQLite 数据库（文件位置）
DATABASE_URL=sqlite:///./devorbit.db

# 或指定其他位置
DATABASE_URL=sqlite:////tmp/devorbit.db
```

### Q2: 如何切换到 PostgreSQL？

1. 安装 PostgreSQL 和 Python 驱动：

```bash
pip install psycopg2-binary
```

2. 修改 `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/devorbit
```

3. 创建数据库：

```bash
createdb devorbit
```

### Q3: 如何重置数据库？

```bash
# 删除 SQLite 数据库文件
rm devorbit.db

# 重新初始化
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### Q4: 启动时出现 "ModuleNotFoundError"？

确保：

1. 虚拟环境已激活
2. 依赖已安装：`pip install -e .`
3. 在 `backend/` 目录中运行命令

### Q5: 如何查看 API 文档？

启动后端服务后，访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 下一步

完成 Stage 1 后，你可以：

1. ✅ 后端框架已搭建
2. ✅ 数据库模型已定义
3. ✅ 基础 API 端点已创建
4. ⏭ 下一步：Stage 2 - 实现 GitHub OAuth 认证

---

## 故障排除

### 问题: 端口 8000 已被占用

```bash
# 使用其他端口启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 问题: 数据库锁定（SQLite）

```bash
# 确保没有其他进程在访问数据库
# 删除 .db 文件并重新初始化
rm devorbit.db
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### 问题: 导入错误

```bash
# 确保在正确的目录中
cd backend

# 重新安装依赖
pip install -e . --force-reinstall
```

---

## 获取帮助

如有问题，请：

1. 查看 `backend/README.md` 中的文档
2. 检查 `.env` 配置是否正确
3. 查看启动日志中的错误信息
4. 提交 Issue 到项目仓库

---

**祝你开发愉快！** 🚀

