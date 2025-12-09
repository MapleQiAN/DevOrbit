# 多阶段构建 - 后端 API 服务
# Stage 1: 构建阶段
FROM python:3.10-slim-bookworm as builder

WORKDIR /app

# 安装系统依赖（增加重试以缓解 503）
RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Stage 2: 运行阶段
FROM python:3.10-slim-bookworm

WORKDIR /app

# 安装运行时依赖（增加重试以缓解 503）
RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

