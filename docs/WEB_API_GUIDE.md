# VikPea Web API 部署指南

> 将 VikPea 核心功能包装成生产级 Web API，采用 **FastAPI + Next.js + PostgreSQL + Redis** 架构

## 📋 目录

1. [快速开始](#快速开始)
2. [系统要求](#系统要求)
3. [部署方式](#部署方式)
4. [API 文档](#api-文档)
5. [前端配置](#前端配置)
6. [生产部署](#生产部署)
7. [故障排查](#故障排查)

---

## 🚀 快速开始

### 本地开发（最快）

**1. 安装依赖**
```bash
cd /Users/xuzifu/Downloads/VikPea_项目改进版

# 后端依赖
python -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt

# 前端依赖
cd frontend
npm install
cd ..
```

**2. 启动后端 API**
```bash
source venv/bin/activate
cd api
python -m uvicorn app:app --reload --port 8000
```

访问：http://localhost:8000/api/docs

**3. 启动前端**
```bash
cd frontend
npm run dev
```

访问：http://localhost:3000

### Docker 一键启动（推荐）

```bash
# 一键启动所有服务（API + 前端 + 数据库 + Redis）
bash scripts/quick_start.sh

# 或手动启动
docker-compose up -d
```

服务将在以下地址可用：
- 🔵 **API**: http://localhost:8000
- 🎨 **前端**: http://localhost:3000
- 📊 **API 文档**: http://localhost:8000/api/docs
- 🗄️  **数据库管理**: http://localhost:8080

---

## 📦 系统要求

### 本地开发
- Python 3.10+
- Node.js 18+
- Redis（可选，本地缓存）
- PostgreSQL（可选，持久化数据库）

### Docker 部署
- Docker 20.10+
- Docker Compose 2.0+

---

## 🔧 部署方式

### 方式 1：本地开发环境

**优点**: 快速开发、调试便利
**缺点**: 不支持高并发、需要本机环境

```bash
# 后端
cd api
python app.py

# 前端（新终端）
cd frontend
npm run dev
```

### 方式 2：Docker Compose（推荐开发）

**优点**: 隔离环境、一致的配置、支持多服务
**缺点**: 需要 Docker

```bash
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

**配置说明** (`docker-compose.yml`)：
- **api**: FastAPI 后端（8000 端口）
- **db**: PostgreSQL 数据库（5432 端口）
- **cache**: Redis 缓存（6379 端口）
- **frontend**: Next.js 前端（3000 端口）
- **nginx**: 反向代理（80/443 端口）
- **adminer**: 数据库管理工具（8080 端口）

### 方式 3：Kubernetes（生产环境）

参考 [生产部署](#生产部署) 章节

---

## 📚 API 文档

### 基础信息

- **基础 URL**: `http://localhost:8000`
- **API 前缀**: `/api`
- **文档**: `http://localhost:8000/api/docs`（Swagger UI）
- **OpenAPI 规范**: `http://localhost:8000/api/openapi.json`

### 核心接口

#### 1. 分析关键词

**请求**
```bash
curl -X POST "http://localhost:8000/api/analyze/keyword" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "python web development",
    "source": "article",
    "limit": 30,
    "min_score": 3.0
  }'
```

**响应**
```json
{
  "keyword": "python web development",
  "source": "article",
  "total_found": 15,
  "eligible_count": 12,
  "email_found_count": 10,
  "email_rate": 0.83,
  "timestamp": "2024-01-15T10:30:00",
  "details": {
    "search_time": "2.5s",
    "domains_count": 12,
    "quality_score": 7.5
  }
}
```

#### 2. 验证邮箱

**请求**
```bash
curl -X POST "http://localhost:8000/api/validate/email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contact@example.com",
    "check_blacklist": true
  }'
```

**响应**
```json
{
  "email": "contact@example.com",
  "is_valid": true,
  "is_blacklisted": false,
  "confidence_score": 0.95
}
```

#### 3. 扫描 SEO 机会

**请求**
```bash
curl -X POST "http://localhost:8000/api/seo/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "video enhancer",
    "source": "seo",
    "limit": 50,
    "min_score": 3.0
  }'
```

**响应**
```json
[
  {
    "url": "https://example.com/tools",
    "title": "Best Video Enhancement Tools",
    "relevance_score": 8.5,
    "level": "A",
    "opportunity_type": "榜单/工具合集",
    "action": "优先开发"
  }
]
```

#### 4. 生成报告

**请求**
```bash
curl -X POST "http://localhost:8000/api/report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "keyword_review",
    "include_stats": true
  }'
```

**响应**
```json
{
  "report_id": "report_20240115103000",
  "report_type": "keyword_review",
  "title": "keyword_review Report",
  "generated_at": "2024-01-15T10:30:00",
  "data": {
    "status": "generating",
    "progress": "0%"
  }
}
```

### Python 客户端

```python
from api.client import VikPeaAPIClient
import asyncio

async def main():
    async with VikPeaAPIClient("http://localhost:8000") as client:
        # 分析关键词
        result = await client.analyze_keyword("python web development")
        print("分析结果:", result)
        
        # 验证邮箱
        email_result = await client.validate_email("contact@example.com")
        print("邮箱验证:", email_result)
        
        # 扫描 SEO 机会
        opportunities = await client.scan_seo_opportunities("video enhancer")
        print(f"找到 {len(opportunities)} 个机会")

asyncio.run(main())
```

### JavaScript/TypeScript 客户端

```typescript
// 前端示例
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 分析关键词
const analyzeKeyword = async (keyword: string) => {
  const response = await axios.post(`${API_URL}/api/analyze/keyword`, {
    keyword,
    source: 'article',
    limit: 30,
    min_score: 3.0,
  });
  return response.data;
};

// 验证邮箱
const validateEmail = async (email: string) => {
  const response = await axios.post(`${API_URL}/api/validate/email`, {
    email,
    check_blacklist: true,
  });
  return response.data;
};

// 使用
const result = await analyzeKeyword('python web development');
console.log(result);
```

---

## 🎨 前端配置

### 环境变量

创建 `frontend/.env.local`：
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=VikPea
NEXTAUTH_SECRET=your-secret-key-change-in-production
```

### 文件结构

```
frontend/
├── app/                      # Next.js 13+ App Router
│   ├── layout.tsx           # 根布局
│   ├── page.tsx             # 首页
│   ├── dashboard/           # 仪表板
│   │   ├── page.tsx
│   │   ├── keywords/        # 关键词管理
│   │   ├── emails/          # 邮箱管理
│   │   └── reports/         # 报告
│   └── api/                 # API 路由（可选）
├── components/              # React 组件
│   ├── common/             # 公共组件
│   └── features/           # 功能组件
├── lib/                    # 工具函数
│   ├── api.ts             # API 调用
│   └── utils.ts           # 工具函数
├── styles/                # 样式
├── public/                # 静态文件
└── package.json
```

---

## 🏗️ 生产部署

### 1. Vercel 部署（前端）

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd frontend
vercel

# 或连接 GitHub 自动部署
```

环境变量设置在 Vercel 仪表板：
```
NEXT_PUBLIC_API_URL=https://api.example.com
```

### 2. Render/Railway 部署（后端）

**Render 部署步骤**：

1. 连接 GitHub 仓库
2. 创建新 Web Service
3. 配置：
   ```
   构建命令: pip install -r api/requirements.txt
   启动命令: uvicorn app:app --host 0.0.0.0 --port 8000
   ```
4. 添加环境变量：
   ```
   ENVIRONMENT=production
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   SECRET_KEY=your-secure-key
   ```

### 3. AWS 部署（完整方案）

**架构**:
```
CloudFront (CDN) 
  ↓
ALB (Application Load Balancer)
  ├→ ECS/Fargate (FastAPI)
  └→ S3/CloudFront (Next.js 静态)
RDS (PostgreSQL)
ElastiCache (Redis)
```

**步骤**：
1. 创建 RDS PostgreSQL 实例
2. 创建 ElastiCache Redis 集群
3. 创建 ECR 仓库并推送 Docker 镜像
4. 部署到 ECS Fargate
5. 配置 ALB 和路由规则
6. 部署前端到 S3 + CloudFront

### 4. Docker Swarm/Kubernetes

**Kubernetes 部署示例** (`k8s/deploy.yaml`)：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vikpea-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vikpea-api
  template:
    metadata:
      labels:
        app: vikpea-api
    spec:
      containers:
      - name: api
        image: vikpea-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: vikpea-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: vikpea-secrets
              key: redis_url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**部署**：
```bash
kubectl apply -f k8s/

# 查看状态
kubectl get pods
kubectl logs deployment/vikpea-api
```

---

## 🔍 故障排查

### 1. API 连接失败

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查 Docker 容器状态
docker-compose ps

# 查看容器日志
docker-compose logs api
```

### 2. 前端无法调用 API

**检查项**：
- CORS 配置: `api/app.py` 中的 `CORSMiddleware`
- 环境变量: `frontend/.env.local` 中的 `NEXT_PUBLIC_API_URL`
- 网络: 防火墙/代理设置

**修复 CORS**：
```python
# api/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 数据库连接错误

```bash
# 检查 PostgreSQL
docker-compose exec db psql -U vikpea -d vikpea -c "\dt"

# 检查 Redis
docker-compose exec cache redis-cli ping
```

### 4. 性能问题

**优化建议**：
- 启用 Redis 缓存
- 使用 Connection pooling（SQLAlchemy）
- 添加数据库索引
- 使用 CDN for 静态资源
- 配置 Gunicorn worker 数: `--workers 4 --worker-class uvicorn.workers.UvicornWorker`

```bash
# 生产启动命令
gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

---

## 📊 监控和日志

### 日志文件

```
logs/
├── app.log           # 应用日志
├── access.log        # 访问日志
└── error.log         # 错误日志
```

### 实时日志查看

```bash
# Docker 日志
docker-compose logs -f api

# 或使用 Sentry（生产环境）
export SENTRY_DSN="https://xxxxx@sentry.io/xxxxx"
```

### 性能监控

使用 `/api/stats` 端点获取实时统计：
```bash
curl http://localhost:8000/api/stats | jq .
```

---

## 🔐 安全建议

### 1. 环境变量管理
- ✅ 使用 `.env` 文件（不提交到 Git）
- ✅ 生产环境使用密钥管理服务（AWS Secrets Manager、HashiCorp Vault）
- ✅ 定期轮换密钥

### 2. 认证和授权
- ✅ 实现 API 密钥认证
- ✅ 添加 JWT token 支持
- ✅ 设置适当的权限控制

### 3. 数据安全
- ✅ 启用 HTTPS/TLS
- ✅ 加密敏感数据
- ✅ 定期备份数据库

### 4. 速率限制
```python
# app.py 已包含速率限制配置
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100  # 每分钟 100 个请求
```

---

## 📝 常用命令

```bash
# Docker Compose
docker-compose up -d           # 启动服务
docker-compose down            # 停止服务
docker-compose logs -f api     # 查看日志
docker-compose exec api bash   # 进入容器

# 本地开发
source venv/bin/activate       # 激活虚拟环境
pip install -r requirements.txt # 安装依赖
python -m uvicorn app:app --reload  # 启动开发服务器

# 前端开发
npm run dev      # 开发服务器
npm run build    # 构建
npm start        # 生产启动
```

---

## 🤝 获得帮助

- 📖 [FastAPI 文档](https://fastapi.tiangolo.com/)
- 📖 [Next.js 文档](https://nextjs.org/docs)
- 📖 [Docker 文档](https://docs.docker.com/)
- 💬 [VikPea 项目问题](https://github.com/your-repo/issues)

---

**最后更新**: 2024-01-15
**版本**: VikPea API 2.0.0
