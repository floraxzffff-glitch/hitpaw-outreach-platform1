# Frontend Dockerfile - Next.js (Simplified for faster builds)
FROM node:20-alpine

WORKDIR /app

# 使用淘宝镜像加速 npm 安装
RUN npm config set registry https://registry.npmmirror.com

# 复制依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install --production=false

# 复制前端源码（所有文件，包括 app/ 目录）
COPY frontend/ ./

# 构建 Next.js 应用
RUN npm run build

# 暴露端口
EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 启动应用
CMD ["npm", "start"]
