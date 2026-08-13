#!/bin/bash

# 只启动前端的脚本

cd "$(dirname "$0")/frontend" || exit 1

if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

echo "启动 Next.js 开发服务器..."
npm run dev
