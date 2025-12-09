# 多阶段构建 - 前端应用
# Stage 1: 构建阶段
FROM node:18-alpine as builder

WORKDIR /app

# 启用 corepack 并准备 pnpm（使用 package.json 中声明的版本）
RUN corepack enable

# 复制 package 文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN corepack install && pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建应用
RUN pnpm run build

# Stage 2: 运行阶段 - 使用 Nginx
FROM nginx:alpine

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 创建非 root 用户（若已存在则忽略错误）
RUN addgroup -S -g 101 nginx 2>/dev/null || true && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx 2>/dev/null || true

# 暴露端口（改为非特权端口，避免 80 端口权限问题）
EXPOSE 13233

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:813233/health || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

