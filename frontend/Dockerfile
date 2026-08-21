# Next.js 前端 Dockerfile

FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY frontend/package*.json ./

# 清除缓存并显式安装正确版本
RUN npm cache clean --force && \
    npm install next@14.2.33 react@18 react-dom@18 && \
    npm ci

# 复制源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# ======================== 生产镜像 ========================
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production

# 复制 package 文件
COPY frontend/package*.json ./

# 清除缓存并显式安装正确版本
RUN npm cache clean --force && \
    npm install next@14.2.33 react@18 react-dom@18 --only=production && \
    npm ci --only=production

# 复制构建结果
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

EXPOSE 3000

CMD ["npm", "start"]
