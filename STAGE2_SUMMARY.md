# Stage 2: GitHub OAuth 认证实现 - 完成总结

## 🎯 阶段目标

✅ **已完成**

- 实现 GitHub OAuth 登录流程（后端）
- 实现 JWT 签发与验证
- 实现用户数据库模型与存储
- 配置 Alembic 迁移

---

## 📁 新增/修改的文件

### 修改的文件

| 文件 | 说明 |
|------|------|
| `backend/app/api/deps.py` | 完整实现 JWT 依赖注入和 Bearer token 提取 |
| `backend/app/schemas/auth.py` | 添加 GithubUserInfo schema |

### 新增的文件

| 文件 | 说明 |
|------|------|
| `backend/app/api/v1/endpoints/auth.py` | 完整实现 GitHub OAuth 认证端点 |
| `backend/alembic/versions/001_initial_user_table.py` | 初始迁移：创建 users 表 |
| `backend/alembic/versions/002_github_tables.py` | 第二个迁移：创建 GitHub 相关表 |
| `STAGE2_SUMMARY.md` | 本文件 |

---

## 🔐 实现的功能详解

### 1. GitHub OAuth 登录流程

#### 端点 1: `GET /auth/github/login`

**功能**: 获取 GitHub OAuth 授权 URL

**请求**:
```bash
GET http://localhost:8000/auth/github/login
```

**响应**:
```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?client_id=xxx&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fgithub%2Fcallback&scope=user%3Aemail+read%3Auser&allow_signup=true"
}
```

**工作流程**:
1. 前端调用此端点
2. 获取授权 URL
3. 跳转到 GitHub 授权页面
4. 用户授权后，GitHub 重定向到 `GITHUB_REDIRECT_URI`，并附带 `code` 参数

#### 端点 2: `GET /auth/github/callback`

**功能**: 处理 GitHub OAuth 回调，交换 token，创建用户，签发 JWT

**请求**:
```bash
GET http://localhost:8000/auth/github/callback?code=abc123&state=optional_state
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "github_id": 12345678,
    "github_login": "octocat",
    "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
    "created_at": "2025-12-09T11:50:21.953000",
    "updated_at": "2025-12-09T11:50:21.953000"
  }
}
```

**工作流程**:

```
1. 前端从 URL 中提取 code
   ↓
2. 调用 /auth/github/callback?code=xxx
   ↓
3. 后端使用 code 向 GitHub 交换 access_token
   ↓
4. 使用 access_token 获取用户信息
   ↓
5. 在数据库中创建或更新用户
   ↓
6. 签发 JWT token
   ↓
7. 返回 JWT 和用户信息给前端
   ↓
8. 前端存储 JWT 到 localStorage，跳转到仪表盘
```

### 2. JWT 认证机制

#### Token 创建 (`app/core/security.py`)

```python
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    # 默认过期时间：7 天（10080 分钟）
    # 可通过 JWT_EXPIRE_MINUTES 配置
```

**特点**:
- 使用 HS256 算法
- 包含用户 ID 作为 subject
- 自动计算过期时间
- 支持自定义过期时间

#### Token 验证 (`app/api/deps.py`)

```python
def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录的用户"""
    # 1. 从 Authorization header 提取 Bearer token
    # 2. 解码并验证 token
    # 3. 从数据库查询用户
    # 4. 返回用户对象
```

**使用方式**:

在任何需要认证的端点中使用：

```python
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id}
```

**请求示例**:

```bash
curl -H "Authorization: Bearer <jwt_token>" http://localhost:8000/protected
```

### 3. 用户数据模型

#### User 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键，自增 |
| `github_id` | Integer | GitHub 用户 ID（唯一） |
| `github_login` | String | GitHub 用户名（唯一） |
| `avatar_url` | String | GitHub 头像 URL |
| `github_access_token` | String | GitHub OAuth access token |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

**索引**:
- `github_id` (UNIQUE)
- `github_login` (UNIQUE)

### 4. Alembic 数据库迁移

#### 迁移 001: 初始用户表

```bash
# 执行迁移
alembic upgrade 001

# 回滚迁移
alembic downgrade -1
```

创建 `users` 表，包含所有用户相关字段。

#### 迁移 002: GitHub 数据表

```bash
# 执行迁移
alembic upgrade 002
```

创建 `github_repos` 和 `github_daily_stats` 表。

#### 查看迁移历史

```bash
# 查看当前版本
alembic current

# 查看所有版本
alembic history
```

---

## 🔧 配置说明

### GitHub OAuth 配置

在 `.env` 文件中配置：

```env
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
```

**如何获取 GitHub OAuth 凭证**:

1. 访问 https://github.com/settings/developers
2. 点击 "New OAuth App"
3. 填写应用信息：
   - Application name: DevOrbit
   - Homepage URL: http://localhost:3000
   - Authorization callback URL: http://localhost:3000/auth/github/callback
4. 创建应用后，复制 Client ID 和 Client Secret

### JWT 配置

在 `.env` 文件中配置：

```env
JWT_SECRET_KEY=your_super_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080  # 7 days
```

**安全建议**:
- 生产环境必须更改 `JWT_SECRET_KEY`
- 使用强密钥（至少 32 字符）
- 不要在代码中硬编码密钥

---

## 🚀 本地运行验证

### 步骤 1: 安装依赖

```bash
cd backend
pip install -e .
```

### 步骤 2: 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env，填入 GitHub OAuth 凭证
# GITHUB_CLIENT_ID=xxx
# GITHUB_CLIENT_SECRET=xxx
```

### 步骤 3: 初始化数据库

```bash
# 方式 1: 使用 Alembic（推荐）
alembic upgrade head

# 方式 2: 直接创建表
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### 步骤 4: 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤 5: 测试 OAuth 流程

#### 方式 1: 使用浏览器

1. 访问 http://localhost:8000/docs（Swagger UI）
2. 找到 `/auth/github/login` 端点
3. 点击 "Try it out" → "Execute"
4. 获取授权 URL，在浏览器中打开
5. 授权后，GitHub 会重定向到回调 URL
6. 手动访问 `/auth/github/callback?code=<code>` 来完成流程

#### 方式 2: 使用 curl

```bash
# 1. 获取授权 URL
curl http://localhost:8000/auth/github/login

# 2. 在浏览器中打开返回的 authorization_url
# 3. 授权后，GitHub 会重定向到回调 URL，提取 code 参数

# 4. 使用 code 调用回调端点
curl "http://localhost:8000/auth/github/callback?code=<code>"
```

#### 方式 3: 使用 API 文档

1. 启动后端服务
2. 访问 http://localhost:8000/docs
3. 在 Swagger UI 中测试端点

---

## 📊 数据库关系图（更新）

```
┌─────────────────────────────────────────────────────────────┐
│                          User                               │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ github_id (UNIQUE, INDEX)                                   │
│ github_login (UNIQUE, INDEX)                                │
│ avatar_url                                                  │
│ github_access_token                                         │
│ created_at, updated_at                                      │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         │ 1:N (cascade delete)               │ 1:N (cascade delete)
         ▼                                    ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│    GithubRepo            │    │   GithubDailyStat            │
├──────────────────────────┤    ├──────────────────────────────┤
│ id (PK)                  │    │ id (PK)                      │
│ user_id (FK, INDEX)      │    │ user_id (FK, INDEX)          │
│ repo_id (UNIQUE, INDEX)  │    │ date (INDEX)                 │
│ name                     │    │ commit_count                 │
│ full_name (INDEX)        │    │ pr_count                     │
│ private                  │    │ issue_count                  │
│ language                 │    │ star_delta                   │
│ html_url                 │    │ created_at, updated_at       │
│ description              │    │                              │
│ created_at, updated_at   │    │                              │
└──────────────────────────┘    └──────────────────────────────┘
```

---

## 🔄 API 端点总览

### 认证相关

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| GET | `/auth/github/login` | 获取 OAuth 授权 URL | ❌ |
| GET | `/auth/github/callback` | 处理 OAuth 回调 | ❌ |

### 健康检查

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| GET | `/health` | 健康检查 | ❌ |
| GET | `/` | 根路由 | ❌ |

### GitHub 数据（Stage 3）

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| POST | `/github/sync` | 同步 GitHub 数据 | ✅ |
| GET | `/github/stats/daily` | 查询每日统计 | ✅ |

---

## 🔑 关键代码片段

### 1. Bearer Token 提取

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    return credentials.credentials
```

### 2. OAuth 流程

```python
# 第 1 步：交换 access token
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
        },
        headers={"Accept": "application/json"},
    )
    token_data = response.json()
    access_token = token_data["access_token"]

# 第 2 步：获取用户信息
user_response = await client.get(
    "https://api.github.com/user",
    headers={"Authorization": f"Bearer {access_token}"},
)
github_user = user_response.json()

# 第 3 步：创建或更新用户
user = User(
    github_id=github_user["id"],
    github_login=github_user["login"],
    avatar_url=github_user["avatar_url"],
    github_access_token=access_token,
)
db.add(user)
db.commit()

# 第 4 步：签发 JWT
jwt_token = create_access_token(subject=str(user.id))
```

### 3. 受保护的端点

```python
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.github_login}!",
        "user_id": current_user.id,
    }
```

---

## ✅ 完成清单

- [x] GitHub OAuth 登录端点
- [x] GitHub OAuth 回调处理
- [x] JWT token 创建和验证
- [x] Bearer token 提取
- [x] 用户创建和更新
- [x] 数据库迁移（Alembic）
- [x] 错误处理和验证
- [x] API 文档

---

## 🎉 总结

**Stage 2 已成功完成！**

现在你有了完整的 GitHub OAuth 认证系统：

1. ✅ 用户可以通过 GitHub 登录
2. ✅ 后端签发 JWT token
3. ✅ 前端可以使用 JWT 访问受保护的端点
4. ✅ 用户信息存储在数据库中

**下一步**：Stage 3 - 实现 GitHub 数据同步和查询

---

**创建时间**: 2025-12-09  
**版本**: 0.1.0 - Stage 2 完成

