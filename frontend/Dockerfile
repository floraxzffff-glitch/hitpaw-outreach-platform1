# Next.js 前端 Dockerfile

FROM node:18-alpine AS builder

WORKDIR /app

# 安装依赖
COPY frontend/package*.json ./
RUN npm cache clean --force && npm ci --prefer-offline --no-audit

# 复制源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# ======================== 生产镜像 ========================
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production

# 安装 next-runtime
COPY frontend/package*.json ./
RUN npm cache clean --force && npm ci --prefer-offline --no-audit --only=production

# 复制构建结果
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

EXPOSE 3000

CMD ["npm", "start"]
