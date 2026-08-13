#!/bin/bash

# VikPea 项目启动脚本（使用 Docker Compose）
# 一键启动完整环境

set -e

echo "========================================"
echo "🐳 VikPea Docker 启动脚本"
echo "========================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未检测到 Docker"
    echo "请先安装 Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker 已安装"

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：未检测到 Docker Compose"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo "✓ Docker Compose 已安装"

# 启动服务
echo ""
echo "🚀 启动所有服务..."
docker-compose up -d

echo ""
echo "========================================"
echo "✅ Docker 容器已启动！"
echo "========================================"
echo ""
echo "📍 服务地址："
echo "   前端: http://localhost:3000"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo "   数据库管理: http://localhost:8080"
echo ""
echo "📊 查看日志："
echo "   docker-compose logs -f api"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 停止服务："
echo "   docker-compose down"
echo ""
echo "📚 完整文档："
echo "   cat docs/WEB_API_GUIDE.md"
echo ""
echo "========================================"
