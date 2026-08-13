#!/bin/bash

# Next.js 前端项目初始化脚本

set -e

echo "🎨 VikPea Next.js 前端初始化"
echo "============================="

PROJECT_NAME="vikpea-frontend"
FRONTEND_DIR="frontend"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 需要安装 Node.js 18+，访问 https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version) 已安装${NC}"
echo -e "${GREEN}✅ npm $(npm --version) 已安装${NC}"

# 创建 Next.js 项目（如果不存在）
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "\n${YELLOW}📦 创建 Next.js 项目${NC}"
    npx create-next-app@latest $FRONTEND_DIR \
        --typescript \
        --eslint \
        --tailwind \
        --app \
        --no-src-dir \
        --no-git \
        --import-alias '@/*'
else
    echo -e "\n${YELLOW}📂 前端目录已存在，跳过创建${NC}"
fi

cd $FRONTEND_DIR

# 安装依赖
echo -e "\n${YELLOW}📚 安装依赖${NC}"
npm install

# 安装额外的依赖
echo -e "\n${YELLOW}📦 安装额外依赖${NC}"
npm install axios zustand react-query next-auth

# 创建环境文件
if [ ! -f ".env.local" ]; then
    echo -e "\n${YELLOW}⚙️  创建环境配置${NC}"
    cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=VikPea
NEXTAUTH_SECRET=your-secret-key-change-in-production
EOF
fi

echo -e "\n${GREEN}✅ 前端项目初始化完成${NC}"
echo ""
echo "开发运行:"
echo "  cd $FRONTEND_DIR && npm run dev"
echo ""
echo "生产构建:"
echo "  cd $FRONTEND_DIR && npm run build && npm start"
