# DevOrbit 快速启动指南

欢迎使用 DevOrbit！本指南将帮助你快速启动项目。

---

## 📋 前置要求

- **Python**: 3.10 或更高版本
- **Node.js**: 16.0 或更高版本
- **pnpm**（建议通过 Corepack 启用）
- **GitHub 账户**（用于 OAuth 登录）

---

## 🔧 第一步：GitHub OAuth 配置

### 1. 创建 GitHub OAuth App

1. 访问 https://github.com/settings/developers
2. 点击「New OAuth App」
3. 填写以下信息：
   - **Application name**: DevOrbit
   - **Homepage URL**: http://localhost:3000
   - **Authorization callback URL**: http://localhost:3000/auth/github/callback
4. 点击「Create OAuth application」
5. 复制 **Client ID** 和 **Client Secret**

### 2. 配置后端环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入 GitHub OAuth 凭证：

```env
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback
```

---

## 🚀 第二步：启动后端服务

### 1. 安装依赖

```bash
cd backend
pip install -e .
```

### 2. 初始化数据库

```bash
# 使用 Alembic 迁移
alembic upgrade head

# 或直接创建表
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### 3. 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

你应该看到：

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 4. 验证后端

在另一个终端中：

```bash
curl http://localhost:8000/health
# 返回: {"status":"ok"}
```

或访问 API 文档：http://localhost:8000/docs

---

## 🎨 第三步：启动前端服务

### 1. 安装依赖

```bash
cd frontend
corepack enable
pnpm install
```

### 2. 配置环境变量

```bash
# 创建 .env.local 文件
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF
```

### 3. 启动开发服务器

```bash
pnpm run dev
```

你应该看到：

```
  VITE v4.5.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
```

---

## 🎯 第四步：完整的端到端测试

### 1. 打开应用

在浏览器中访问 http://localhost:5173

你应该看到登录页面。

### 2. 测试登录流程

1. 点击「使用 GitHub 登录」按钮
2. 重定向到 GitHub 授权页面
3. 点击「Authorize」授权
4. 重定向回应用，显示加载动画
5. 自动跳转到仪表盘

### 3. 查看仪表盘

仪表盘应该显示：
- 4 个统计卡片（总提交数、PR、Issues、Stars）
- 「同步 GitHub 数据」按钮
- GitHub 每日活动图表

### 4. 测试数据同步

1. 点击「同步 GitHub 数据」按钮
2. 显示加载状态
3. 同步完成后显示成功消息
4. 统计卡片和图表自动更新

### 5. 测试图表交互

1. 在图表上方修改日期范围
2. 图表自动重新加载
3. 显示指定时间范围的数据

### 6. 测试用户菜单

1. 点击右上角的头像
2. 展开用户菜单
3. 点击「退出登录」
4. 重定向到登录页面

---

## 📊 项目结构

```
DevOrbit/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── core/              # 配置和安全
│   │   ├── db/                # 数据库配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API 端点
│   │   └── services/          # 业务逻辑
│   ├── alembic/               # 数据库迁移
│   ├── pyproject.toml         # 项目配置
│   ├── .env                   # 环境变量
│   └── README.md              # 后端文档
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── main.ts            # 应用入口
│   │   ├── App.vue            # 根组件
│   │   ├── api/               # API 调用
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── router/            # Vue Router 路由
│   │   ├── views/             # 页面组件
│   │   └── components/        # 通用组件
│   ├── package.json           # 项目依赖
│   ├── vite.config.ts         # Vite 配置
│   ├── tsconfig.json          # TypeScript 配置
│   └── index.html             # HTML 入口
│
├── README.md                   # 项目总体文档
├── SETUP.md                    # 详细设置指南
├── QUICKSTART.md              # 本文件
├── STAGE1_SUMMARY.md          # Stage 1 总结
├── STAGE2_SUMMARY.md          # Stage 2 总结
├── STAGE3_SUMMARY.md          # Stage 3 总结
├── STAGE4_SUMMARY.md          # Stage 4 总结
├── STAGE5_SUMMARY.md          # Stage 5 总结
└── STAGE6_SUMMARY.md          # Stage 6 总结
```

---

## 🔍 常见问题

### Q1: 后端启动失败，提示 "ModuleNotFoundError"

**解决**:
```bash
cd backend
pip install -e .
```

### Q2: 前端启动失败，提示 "Cannot find module"

**解决**:
```bash
cd frontend
pnpm install
```

### Q3: 登录时提示 "GitHub OAuth 配置不完整"

**解决**:
检查 `backend/.env` 文件中的 `GITHUB_CLIENT_ID` 和 `GITHUB_CLIENT_SECRET` 是否正确填写。

### Q4: 同步数据时提示 "401 Unauthorized"

**解决**:
- 确保 JWT token 有效
- 尝试重新登录
- 检查后端日志中的详细错误信息

### Q5: 图表不显示数据

**解决**:
1. 点击「同步 GitHub 数据」按钮同步数据
2. 检查浏览器控制台中的错误信息
3. 确保后端 API 返回正确的数据

---

## 📚 文档导航

- **项目总体文档**: [README.md](README.md)
- **详细设置指南**: [SETUP.md](SETUP.md)
- **后端文档**: [backend/README.md](backend/README.md)
- **GitHub OAuth 指南**: [backend/OAUTH_GUIDE.md](backend/OAUTH_GUIDE.md)
- **Stage 1 总结**: [STAGE1_SUMMARY.md](STAGE1_SUMMARY.md)
- **Stage 2 总结**: [STAGE2_SUMMARY.md](STAGE2_SUMMARY.md)
- **Stage 3 总结**: [STAGE3_SUMMARY.md](STAGE3_SUMMARY.md)
- **Stage 4 总结**: [STAGE4_SUMMARY.md](STAGE4_SUMMARY.md)
- **Stage 5 总结**: [STAGE5_SUMMARY.md](STAGE5_SUMMARY.md)

---

## 🆘 获取帮助

如果遇到问题：

1. 查看相关的文档和 README
2. 检查后端日志和浏览器控制台
3. 查看 GitHub Issues
4. 提交 Issue 或 PR

---

## 🎉 下一步

完成快速启动后，你可以：

1. **探索代码**: 了解项目的代码结构和实现细节
2. **自定义配置**: 修改样式、添加新功能
3. **部署上线**: 使用 Docker 或其他方式部署到生产环境
4. **扩展功能**: 添加刷题平台、本地笔记等数据源

---

**祝你使用愉快！** 🚀

**最后更新**: 2025-12-09  
**版本**: 0.1.0

