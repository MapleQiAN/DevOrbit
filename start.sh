#!/bin/bash

# ============================================
# DevOrbit 一键启动脚本
# ============================================
# 用法: ./start.sh [选项]
# 选项:
#   -h, --help      显示帮助信息
#   -d, --dev       开发模式
#   -p, --prod      生产模式
#   -b, --build     重新构建镜像
#   -l, --logs      显示实时日志

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
MODE="dev"
BUILD=false
LOGS=false

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 函数：显示帮助信息
show_help() {
    cat << EOF
DevOrbit 一键启动脚本

用法: ./start.sh [选项]

选项:
    -h, --help      显示此帮助信息
    -d, --dev       开发模式（默认）
    -p, --prod      生产模式
    -b, --build     重新构建 Docker 镜像
    -l, --logs      启动后显示实时日志

示例:
    ./start.sh                  # 开发模式启动
    ./start.sh -p               # 生产模式启动
    ./start.sh -b -l            # 重新构建并显示日志
    ./start.sh --prod --build   # 生产模式，重新构建

EOF
}

# 函数：检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        echo "请访问 https://docs.docker.com/get-docker/ 安装 Docker"
        exit 1
    fi
    print_success "Docker 已安装: $(docker --version)"
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        echo "请访问 https://docs.docker.com/compose/install/ 安装 Docker Compose"
        exit 1
    fi
    print_success "Docker Compose 已安装: $(docker-compose --version)"
    
    # 检查 Docker 守护进程
    if ! docker ps &> /dev/null; then
        print_error "Docker 守护进程未运行"
        echo "请启动 Docker 服务"
        exit 1
    fi
    print_success "Docker 守护进程正在运行"
}

# 函数：检查环境文件
check_env_file() {
    print_info "检查环境配置..."
    
    if [ ! -f ".env" ]; then
        if [ ! -f ".env.example" ]; then
            print_error ".env 和 .env.example 都不存在"
            exit 1
        fi
        
        print_warning ".env 文件不存在，从 .env.example 复制..."
        cp .env.example .env
        print_success ".env 文件已创建"
        print_warning "请编辑 .env 文件，填入 GitHub OAuth 凭证等信息"
        print_warning "然后重新运行此脚本"
        exit 0
    fi
    
    print_success ".env 文件已存在"
    
    # 检查关键配置
    if ! grep -q "GITHUB_CLIENT_ID" .env || grep "^GITHUB_CLIENT_ID=$" .env; then
        print_warning "GITHUB_CLIENT_ID 未配置，请编辑 .env 文件"
    fi
}

# 函数：启动服务
start_services() {
    print_info "启动 Docker 服务..."
    
    local compose_cmd="docker-compose"
    
    if [ "$BUILD" = true ]; then
        print_info "重新构建镜像..."
        $compose_cmd build --no-cache
    fi
    
    # 启动服务
    $compose_cmd up -d
    
    print_success "Docker 服务已启动"
}

# 函数：等待服务就绪
wait_for_services() {
    print_info "等待服务就绪..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        # 检查后端
        if curl -s http://localhost:8000/health &> /dev/null; then
            print_success "后端 API 已就绪"
            break
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            echo "  等待中... ($attempt/$max_attempts)"
        fi
        
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_warning "后端 API 启动超时，但容器可能仍在初始化"
    fi
}

# 函数：显示启动信息
show_startup_info() {
    echo ""
    echo "=========================================="
    echo "🎉 DevOrbit 已启动！"
    echo "=========================================="
    echo ""
    echo "📍 访问地址:"
    echo "   🌐 前端应用:  http://localhost"
    echo "   🔌 后端 API:  http://localhost:8000"
    echo "   📚 API 文档:  http://localhost:8000/docs"
    echo "   [object Object] 重定向: http://localhost:8000/redoc"
    echo ""
    echo "📊 服务状态:"
    docker-compose ps
    echo ""
    echo "💡 常用命令:"
    echo "   查看日志:     docker-compose logs -f"
    echo "   停止服务:     docker-compose stop"
    echo "   重启服务:     docker-compose restart"
    echo "   进入容器:     docker-compose exec backend bash"
    echo ""
    echo "📖 更多信息: 查看 DOCKER_DEPLOYMENT.md"
    echo "=========================================="
    echo ""
}

# 函数：显示实时日志
show_logs() {
    print_info "显示实时日志（按 Ctrl+C 退出）..."
    echo ""
    docker-compose logs -f
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dev)
                MODE="dev"
                shift
                ;;
            -p|--prod)
                MODE="prod"
                shift
                ;;
            -b|--build)
                BUILD=true
                shift
                ;;
            -l|--logs)
                LOGS=true
                shift
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 清屏
    clear
    
    # 打印欢迎信息
    echo "=========================================="
    echo "[object Object] 启动脚本"
    echo "=========================================="
    echo "模式: $MODE"
    echo "重新构建: $BUILD"
    echo ""
    
    # 执行启动步骤
    check_dependencies
    echo ""
    
    check_env_file
    echo ""
    
    start_services
    echo ""
    
    wait_for_services
    echo ""
    
    show_startup_info
    
    # 显示日志
    if [ "$LOGS" = true ]; then
        show_logs
    fi
}

# 执行主函数
main "$@"

