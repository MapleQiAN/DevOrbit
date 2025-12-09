#!/bin/bash
# ============================================
# DevOrbit Docker 启动脚本
# ============================================
# 此脚本用于初始化和启动应用

set -e

echo "=========================================="
echo "DevOrbit Docker 部署启动脚本"
echo "=========================================="

# 检查必要的环境变量
check_env() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo "❌ 错误: 环境变量 $var_name 未设置"
        return 1
    fi
}

# 等待服务就绪
wait_for_service() {
    local host=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ 等待 $host:$port 就绪..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            echo "✅ $host:$port 已就绪"
            return 0
        fi
        
        echo "  尝试 $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ 错误: $host:$port 无法连接"
    return 1
}

# 主函数
main() {
    echo ""
    echo "📋 检查环境配置..."
    
    # 检查关键环境变量
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "🔒 生产环境模式"
        check_env "GITHUB_CLIENT_ID" || exit 1
        check_env "GITHUB_CLIENT_SECRET" || exit 1
        check_env "JWT_SECRET_KEY" || exit 1
    else
        echo "🔧 开发环境模式"
    fi
    
    echo ""
    echo "🗄️  检查数据库连接..."
    
    # 等待数据库就绪
    if [[ "$DATABASE_URL" == *"postgresql"* ]]; then
        # PostgreSQL
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        DB_PORT=${DB_PORT:-5432}
        
        wait_for_service "$DB_HOST" "$DB_PORT" || exit 1
    fi
    
    echo ""
    echo "🔄 运行数据库迁移..."
    
    # 运行 Alembic 迁移
    if command -v alembic &> /dev/null; then
        cd /app
        alembic upgrade head || {
            echo "⚠️  迁移失败，但继续启动..."
        }
    else
        echo "⚠️  Alembic 未安装，跳过迁移"
    fi
    
    echo ""
    echo "🚀 启动应用..."
    
    # 启动应用
    if [ -z "$1" ]; then
        # 默认启动 FastAPI
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000
    else
        # 执行自定义命令
        exec "$@"
    fi
}

# 执行主函数
main "$@"

