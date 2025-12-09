# Stage 3: GitHub 数据同步与查询 - 完成总结

## 🎯 阶段目标

✅ **已完成**

- 实现 GitHub API 调用服务（获取仓库、活动数据）
- 实现数据聚合逻辑（按日期统计 commit 数）
- 实现 `/github/sync` 和 `/github/stats/daily` 端点

---

## 📁 新增/修改的文件

### 新增的文件

| 文件 | 说明 |
|------|------|
| `backend/app/services/github_sync.py` | 完整实现 GitHub 数据同步服务 |
| `STAGE3_SUMMARY.md` | 本文件 |

### 修改的文件

| 文件 | 说明 |
|------|------|
| `backend/app/api/v1/endpoints/github.py` | 完整实现 GitHub 数据端点 |

---

## 🔧 实现的功能详解

### 1. GitHub 数据同步服务 (`app/services/github_sync.py`)

#### 函数 1: `fetch_user_repos(github_token: str) -> List[dict]`

**功能**: 获取用户的所有仓库列表

**实现细节**:
- 调用 GitHub API: `GET /user/repos`
- 支持分页（每页 100 个）
- 按更新时间倒序排列
- 返回仓库的完整信息（id, name, full_name, private, language, html_url, description）

**示例**:
```python
repos = await fetch_user_repos(github_token)
# 返回: [
#   {
#     "id": 123456,
#     "name": "my-repo",
#     "full_name": "username/my-repo",
#     "private": False,
#     "language": "Python",
#     "html_url": "https://github.com/username/my-repo",
#     "description": "My awesome project"
#   },
#   ...
# ]
```

#### 函数 2: `fetch_user_events(github_token: str, days: int = 90) -> List[dict]`

**功能**: 获取用户的事件列表（push、PR、issue、star 等）

**实现细节**:
- 调用 GitHub API: `GET /users/{username}/events`
- 支持分页（每页 100 个）
- 自动过滤超出时间范围的事件
- 默认获取最近 90 天的事件
- 返回事件的完整信息（type, created_at, payload）

**支持的事件类型**:
- `PushEvent`: 代码提交
- `PullRequestEvent`: Pull Request
- `IssuesEvent`: Issue
- `WatchEvent`: Star

**示例**:
```python
events = await fetch_user_events(github_token, days=30)
# 返回: [
#   {
#     "type": "PushEvent",
#     "created_at": "2025-12-09T10:30:00Z",
#     "payload": {
#       "commits": [
#         {"message": "Fix bug", "url": "..."},
#         {"message": "Add feature", "url": "..."}
#       ]
#     }
#   },
#   ...
# ]
```

#### 函数 3: `aggregate_daily_stats(events: List[dict]) -> Dict[date, Dict[str, int]]`

**功能**: 聚合事件数据，按日期统计各类活动

**实现细节**:
- 遍历所有事件
- 按事件日期分组
- 统计各类事件数量：
  - `commit_count`: 代码提交数
  - `pr_count`: Pull Request 数
  - `issue_count`: Issue 数
  - `star_delta`: Star 增量

**示例**:
```python
daily_stats = aggregate_daily_stats(events)
# 返回: {
#   date(2025-12-09): {
#     "commit_count": 5,
#     "pr_count": 1,
#     "issue_count": 0,
#     "star_delta": 2,
#   },
#   date(2025-12-08): {
#     "commit_count": 3,
#     "pr_count": 0,
#     "issue_count": 1,
#     "star_delta": 0,
#   },
#   ...
# }
```

#### 函数 4: `sync_github_data(user: User, db: Session) -> Tuple[int, int]`

**功能**: 同步用户的所有 GitHub 数据

**工作流程**:

```
1. 获取用户的仓库列表
   ↓
2. 更新/创建仓库记录到数据库
   ↓
3. 获取用户的事件列表（最近 90 天）
   ↓
4. 聚合每日统计数据
   ↓
5. 更新/创建每日统计记录到数据库
   ↓
6. 返回同步结果 (仓库数, 更新的统计记录数)
```

**返回值**:
- `repos_count`: 用户拥有的仓库总数
- `stats_updated`: 更新/创建的每日统计记录数

**示例**:
```python
repos_count, stats_updated = await sync_github_data(user, db)
# 返回: (15, 45)  # 15 个仓库，45 条每日统计记录
```

### 2. GitHub 数据端点 (`app/api/v1/endpoints/github.py`)

#### 端点 1: `POST /github/sync`

**功能**: 同步用户的 GitHub 数据

**认证**: ✅ 需要 JWT token

**请求**:
```bash
curl -X POST http://localhost:8000/github/sync \
  -H "Authorization: Bearer <jwt_token>"
```

**响应**:
```json
{
  "message": "GitHub 数据同步成功",
  "repos_count": 15,
  "stats_updated": 45,
  "date_range": "最近 90 天"
}
```

**说明**:
- 前端点击「同步数据」按钮时调用
- 后端从 GitHub API 拉取最新数据
- 更新本地数据库
- 返回同步结果

#### 端点 2: `GET /github/stats/daily`

**功能**: 查询用户的每日 GitHub 统计数据

**认证**: ✅ 需要 JWT token

**查询参数**:
- `from_date` (可选): 开始日期 (YYYY-MM-DD)，默认为 30 天前
- `to_date` (可选): 结束日期 (YYYY-MM-DD)，默认为今天

**请求示例**:
```bash
# 查询最近 30 天的数据
curl http://localhost:8000/github/stats/daily \
  -H "Authorization: Bearer <jwt_token>"

# 查询指定时间范围的数据
curl "http://localhost:8000/github/stats/daily?from_date=2025-11-09&to_date=2025-12-09" \
  -H "Authorization: Bearer <jwt_token>"
```

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "date": "2025-12-09",
      "commit_count": 5,
      "pr_count": 1,
      "issue_count": 0,
      "star_delta": 2,
      "created_at": "2025-12-09T11:50:21.953000",
      "updated_at": "2025-12-09T11:50:21.953000"
    },
    {
      "id": 2,
      "user_id": 1,
      "date": "2025-12-08",
      "commit_count": 3,
      "pr_count": 0,
      "issue_count": 1,
      "star_delta": 0,
      "created_at": "2025-12-09T11:50:21.953000",
      "updated_at": "2025-12-09T11:50:21.953000"
    }
  ],
  "total": 2
}
```

**说明**:
- 返回指定时间范围内的每日统计数据
- 按日期升序排列
- 前端可以用这些数据绘制折线图

---

## 📊 数据流图

```
GitHub API
    │
    ├─ /user/repos ────────────────────────┐
    │                                       │
    ├─ /users/{username}/events ───────────┤
    │                                       ▼
    │                            fetch_user_repos()
    │                            fetch_user_events()
    │                                       │
    │                                       ▼
    │                            aggregate_daily_stats()
    │                                       │
    │                                       ▼
    │                            sync_github_data()
    │                                       │
    │                                       ▼
    │                            Database (SQLite)
    │                                       │
    │                    ┌──────────────────┼──────────────────┐
    │                    ▼                  ▼                  ▼
    │              github_repos    github_daily_stats         users
    │
    └─────────────────────────────────────────────────────────────
                            ▲
                            │
                    POST /github/sync
                    GET /github/stats/daily
                            │
                        Frontend
```

---

## 🔄 API 端点总览（更新）

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

### GitHub 数据 ✅

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| POST | `/github/sync` | 同步 GitHub 数据 | ✅ |
| GET | `/github/stats/daily` | 查询每日统计 | ✅ |

---

## 🚀 本地运行验证

### 步骤 1: 安装依赖

```bash
cd backend
pip install -e .
```

### 步骤 2: 配置环境变量

```bash
# 编辑 .env 文件，确保 GitHub OAuth 凭证已配置
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
```

### 步骤 3: 初始化数据库

```bash
# 使用 Alembic 迁移
alembic upgrade head

# 或直接创建表
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### 步骤 4: 启动后端服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤 5: 测试 GitHub 数据同步

#### 方式 1: 使用 API 文档

1. 打开 http://localhost:8000/docs
2. 点击「Authorize」按钮，输入 JWT token
3. 找到 `POST /github/sync` 端点
4. 点击 "Try it out" → "Execute"
5. 查看同步结果

#### 方式 2: 使用 curl

```bash
# 1. 首先进行 GitHub OAuth 登录，获取 JWT token
# (参考 Stage 2 的步骤)

# 2. 使用 JWT token 调用同步端点
curl -X POST http://localhost:8000/github/sync \
  -H "Authorization: Bearer <jwt_token>"

# 3. 查询每日统计数据
curl "http://localhost:8000/github/stats/daily?from_date=2025-11-09&to_date=2025-12-09" \
  -H "Authorization: Bearer <jwt_token>"
```

---

## 📝 关键代码片段

### 1. 获取仓库列表

```python
async def fetch_user_repos(github_token: str) -> List[dict]:
    repos = []
    page = 1
    
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"{settings.GITHUB_API_BASE_URL}/user/repos",
                params={"page": page, "per_page": 100},
                headers={"Authorization": f"Bearer {github_token}"},
            )
            response.raise_for_status()
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend(page_repos)
            page += 1
    
    return repos
```

### 2. 聚合每日统计

```python
def aggregate_daily_stats(events: List[dict]) -> Dict[date, Dict[str, int]]:
    stats: Dict[date, Dict[str, int]] = {}
    
    for event in events:
        event_date = datetime.fromisoformat(
            event["created_at"].replace("Z", "+00:00")
        ).date()
        
        if event_date not in stats:
            stats[event_date] = {
                "commit_count": 0,
                "pr_count": 0,
                "issue_count": 0,
                "star_delta": 0,
            }
        
        # 根据事件类型统计
        if event["type"] == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            stats[event_date]["commit_count"] += len(commits)
        # ... 其他事件类型处理
    
    return stats
```

### 3. 同步数据到数据库

```python
async def sync_github_data(user: User, db: Session) -> Tuple[int, int]:
    # 获取仓库
    repos = await fetch_user_repos(user.github_access_token)
    
    # 更新数据库
    for repo_data in repos:
        existing = db.query(GithubRepo).filter(
            GithubRepo.repo_id == repo_data["id"]
        ).first()
        
        if existing:
            # 更新
            existing.name = repo_data["name"]
        else:
            # 创建
            db.add(GithubRepo(...))
    
    db.commit()
    
    # 获取事件并聚合
    events = await fetch_user_events(user.github_access_token)
    daily_stats = aggregate_daily_stats(events)
    
    # 更新统计数据
    for stat_date, stat_data in daily_stats.items():
        # ... 创建或更新 GithubDailyStat
    
    return len(repos), len(daily_stats)
```

---

## ✅ 完成清单

- [x] GitHub 仓库列表获取
- [x] GitHub 事件列表获取
- [x] 每日统计数据聚合
- [x] 数据库同步逻辑
- [x] `/github/sync` 端点
- [x] `/github/stats/daily` 端点
- [x] 日期范围查询
- [x] 错误处理和验证
- [x] API 文档

---

## 🎉 总结

**Stage 3 已成功完成！**

现在你有了完整的 GitHub 数据同步系统：

1. ✅ 可以从 GitHub API 拉取用户数据
2. ✅ 可以聚合每日统计数据
3. ✅ 可以查询指定时间范围的统计数据
4. ✅ 前端可以使用这些数据绘制图表

**后端 API 已完全实现！** 🎊

**下一步**：Stage 4 - 前端项目初始化与登录流程

---

**创建时间**: 2025-12-09  
**版本**: 0.1.0 - Stage 3 完成

