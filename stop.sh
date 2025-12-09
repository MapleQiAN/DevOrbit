#!/bin/bash

# ============================================
# DevOrbit 停止脚本
# ============================================
# 用法: ./stop.sh [选项]
# 选项:
#   -h, --help      显示帮助信息
#   -f, --force     强制停止并删除容器
#   -v, --volumes   删除数据卷（谨慎使用！）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 默认配置
FORCE=false
REMOVE_VOLUMES=false

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
DevOrbit 停止脚本

用法: ./stop.sh [选项]

选项:
    -h, --help      显示此帮助信息
    -f, --force     强制停止并删除容器
    -v, --volumes   删除数据卷（谨慎使用！）

示例:
    ./stop.sh               # 正常停止
    ./stop.sh -f            # 强制停止
    ./stop.sh -f -v         # 强制停止并删除数据

EOF
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
            -f|--force)
                FORCE=true
                shift
                ;;
            -v|--volumes)
                REMOVE_VOLUMES=true
                shift
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "=========================================="
    echo "🛑 DevOrbit 停止脚本"
    echo "=========================================="
    echo ""
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 显示当前运行的服务
    print_info "当前运行的服务:"
    docker-compose ps
    echo ""
    
    # 停止服务
    if [ "$FORCE" = true ]; then
        print_warning "强制停止并删除容器..."
        
        if [ "$REMOVE_VOLUMES" = true ]; then
            print_warning "⚠️  将删除所有数据卷！"
            read -p "确认删除数据卷？(y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker-compose down -v
                print_success "容器和数据卷已删除"
            else
                print_info "已取消删除数据卷"
                docker-compose down
                print_success "容器已删除（数据卷保留）"
            fi
        else
            docker-compose down
            print_success "容器已删除（数据卷保留）"
        fi
    else
        print_info "正常停止服务..."
        docker-compose stop
        print_success "服务已停止"
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ 停止完成"
    echo "=========================================="
    echo ""
    echo "💡 提示:"
    echo "   重新启动:  ./start.sh"
    echo "   查看日志:  docker-compose logs"
    echo "   删除容器:  docker-compose down"
    echo ""
}

# 执行主函数
main "$@"

