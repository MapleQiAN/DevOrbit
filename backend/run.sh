#!/bin/bash

# DevOrbit Backend 启动脚本

set -e

echo "🚀 Starting DevOrbit Backend..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# 安装依赖
echo "📦 Installing dependencies..."
pip install -e .

# 创建数据库表（如果不存在）
echo "[object Object]Setting up database..."
python3 -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"

# 启动 API 服务
echo "✨ Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

