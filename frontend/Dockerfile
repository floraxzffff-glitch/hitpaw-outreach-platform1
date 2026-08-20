# Frontend Dockerfile - Next.js
FROM node:20-alpine AS base

# 安装依赖阶段
FROM base AS deps
WORKDIR /app

# 复制依赖文件
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# 构建阶段
FROM base AS builder
WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
# 复制前端源码
COPY frontend/ ./

# 构建 Next.js 应用
RUN npm run build

# 生产运行阶段
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# 暴露端口
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 启动应用
CMD ["node", "server.js"]
