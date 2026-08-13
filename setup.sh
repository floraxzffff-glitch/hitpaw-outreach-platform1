#!/bin/bash

# VikPea 项目启动脚本
# 用途：快速启动完整的前后端开发环境

set -e

echo "========================================"
echo "🚀 VikPea 项目启动脚本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未检测到 Python 3"
    echo "请先安装 Python 3.10+"
    exit 1
fi

echo "✓ Python 3 已安装"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未检测到 Node.js"
    echo "请先安装 Node.js 18+"
    exit 1
fi

echo "✓ Node.js 已安装"

# 配置后端
echo ""
echo "📦 配置后端..."
cd "$(dirname "$0")/api" || exit 1

if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请在 api/.env 中配置数据库信息"
fi

if [ ! -d "venv" ]; then
    echo "📝 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 安装 Python 依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "✓ 后端已准备好"

# 配置前端
echo ""
echo "📦 配置前端..."
cd "$(dirname "$0")/frontend" || exit 1

if [ ! -f ".env.local" ]; then
    echo "📝 创建 .env.local 文件..."
    cp .env.local.example .env.local
fi

if [ ! -d "node_modules" ]; then
    echo "📥 安装 Node.js 依赖..."
    npm install
fi

echo "✓ 前端已准备好"

# 显示启动说明
echo ""
echo "========================================"
echo "✅ 项目配置完成！"
echo "========================================"
echo ""
echo "📚 接下来的步骤："
echo ""
echo "1️⃣  启动后端（新终端）："
echo "   cd api"
echo "   source venv/bin/activate"
echo "   python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2️⃣  启动前端（新终端）："
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3️⃣  访问应用："
echo "   http://localhost:3000"
echo ""
echo "📖 API 文档："
echo "   http://localhost:8000/docs"
echo ""
echo "🐳 或使用 Docker Compose："
echo "   docker-compose up"
echo ""
echo "========================================"
