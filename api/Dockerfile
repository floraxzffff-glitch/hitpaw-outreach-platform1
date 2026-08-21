# 多阶段构建：构建阶段 + 运行阶段
FROM python:3.10-slim as builder

WORKDIR /app

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY api/requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt && \
    /app/venv/bin/pip install yt-dlp

# ======================== 运行阶段 ========================
FROM python:3.10-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /app/venv /app/venv

# 复制应用代码
COPY api/ /app/
COPY src/ /app/src/
COPY workspace/ /app/workspace/

# 创建必要的目录（包括 workspace 用于存放 VikPea 工作台文件）
RUN mkdir -p /app/logs /app/uploads /app/data /app/workspace

# 设置环境变量
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/venv/bin/python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动命令
CMD ["/app/venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
