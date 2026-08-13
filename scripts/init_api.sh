#!/bin/bash

# VikPea API 初始化脚本
# 一键启动 FastAPI + Next.js + 数据库

set -e

echo "🚀 VikPea SEO API 初始化"
echo "========================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 需要安装 Docker${NC}"
    echo "访问 https://docs.docker.com/get-docker/ 安装"
    exit 1
fi

echo -e "${GREEN}✅ Docker 已安装${NC}"

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ 需要安装 Docker Compose${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose 已安装${NC}"

# 创建必要的目录
echo -e "\n${YELLOW}📁 创建目录结构${NC}"
mkdir -p logs uploads data
mkdir -p api frontend nginx

# 检查 .env 文件
if [ ! -f "api/.env" ]; then
    echo -e "${YELLOW}⚠️  复制 .env.example 到 .env${NC}"
    cp api/.env.example api/.env
    echo -e "${YELLOW}⚠️  请编辑 api/.env 文件填入实际配置${NC}"
fi

# 构建和启动服务
echo -e "\n${YELLOW}🔨 构建 Docker 镜像${NC}"
docker-compose build

echo -e "\n${YELLOW}🚀 启动服务${NC}"
docker-compose up -d

echo -e "\n${GREEN}✅ 所有服务已启动${NC}"
echo ""
echo "访问地址："
echo "  - API 文档: http://localhost:8000/api/docs"
echo "  - 前端应用: http://localhost:3000"
echo "  - 数据库管理: http://localhost:8080 (adminer)"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f api"
echo ""
echo "停止服务:"
echo "  docker-compose down"
