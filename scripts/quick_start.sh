#!/bin/bash

# 快速启动脚本 - 一键启动所有组件

set -e

echo "🚀 快速启动 VikPea API + 前端"
echo "=============================="

# 启动 Docker Compose
echo "启动 Docker 容器..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 显示服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

# 显示访问地址
echo ""
echo "🌐 访问地址："
echo "  - API 文档: http://localhost:8000/api/docs"
echo "  - 前端应用: http://localhost:3000"
echo "  - 数据库: http://localhost:8080"
echo ""
echo "💡 提示："
echo "  - 查看 API 日志: docker-compose logs -f api"
echo "  - 查看前端日志: docker-compose logs -f frontend"
echo "  - 停止所有服务: docker-compose down"
