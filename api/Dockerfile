# API Dockerfile - FastAPI Backend
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目依赖文件
COPY backend/requirements.txt /app/requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制 API 代码
COPY api/ /app/api/
COPY 01_请在这个文件夹里操作/ /app/workspace/

# 设置 Python 模块搜索路径
ENV PYTHONPATH=/app:/app/workspace:$PYTHONPATH
ENV WORKSPACE_DIR=/app/workspace

# 设置工作目录为 api
WORKDIR /app/api

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 应用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
