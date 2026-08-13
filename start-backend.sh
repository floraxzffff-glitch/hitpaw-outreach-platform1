#!/bin/bash

# 只启动后端的脚本

cd "$(dirname "$0")/api" || exit 1

# 激活虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "启动 FastAPI 服务器..."
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
