# VikPea 项目完整启动指南

## 🎯 三种启动方式

### 方式 1️⃣：本地开发（推荐）

#### 前提条件
- Python 3.10+
- Node.js 18+
- pip 和 npm

#### 步骤

1. **一键配置**
```bash
chmod +x setup.sh
./setup.sh
```

2. **启动后端** (在新终端中)
```bash
cd api
source venv/bin/activate
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. **启动前端** (在新终端中)
```bash
cd frontend
npm run dev
```

4. **访问应用**
- 前端: http://localhost:3000
- API 文档: http://localhost:8000/docs

---

### 方式 2️⃣：Docker 启动（推荐用于部署）

#### 前提条件
- Docker 20.10+
- Docker Compose 2.0+

#### 步骤

```bash
# 一键启动所有服务
chmod +x docker-start.sh
./docker-start.sh
```

或手动启动：

```bash
docker-compose up -d
```

#### 访问地址
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 数据库管理 (Adminer): http://localhost:8080

#### 常用命令
```bash
# 查看日志
docker-compose logs -f api
docker-compose logs -f frontend

# 停止服务
docker-compose down

# 重建镜像
docker-compose up -d --build

# 进入容器
docker exec -it vikpea_api bash
docker exec -it vikpea_frontend bash
```

---

### 方式 3️⃣：Vercel + Render 云部署

#### 前端部署（Vercel）

1. 连接 GitHub 仓库
2. 设置环境变量：
   - `NEXT_PUBLIC_API_URL`: 后端 API 地址
3. 自动部署

#### 后端部署（Render）

1. 连接 GitHub 仓库
2. 创建新 Web Service
3. 构建命令: `pip install -r requirements.txt`
4. 启动命令: `uvicorn app:app --host 0.0.0.0 --port 8080`
5. 设置环境变量
6. 部署

---

## 📋 环境变量配置

### 后端 (`api/.env`)

```env
# 数据库
DATABASE_URL=postgresql://vikpea:vikpea123@localhost:5432/vikpea_db

# 缓存
REDIS_URL=redis://localhost:6379/0

# 邮件
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API 密钥
API_KEY_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-xxx

# 环境
ENVIRONMENT=development
DEBUG=true

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 前端 (`frontend/.env.local`)

```env
# API 地址
NEXT_PUBLIC_API_URL=http://localhost:8000

# 应用名称
NEXT_PUBLIC_APP_NAME=VikPea

# 可选：认证
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
```

---

## 🚀 快速命令速查

### 后端开发
```bash
cd api

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python3 -m uvicorn app:app --reload

# 运行测试
pytest

# 代码检查
flake8 .

# 代码格式化
black .
```

### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 开发服务器
npm run dev

# 生产构建
npm run build

# 启动生产服务器
npm start

# 类型检查
npm run type-check

# 代码格式化
npm run format

# 代码检查
npm run lint
```

### Docker 命令
```bash
# 查看容器
docker ps

# 查看日志
docker logs -f vikpea_api
docker logs -f vikpea_frontend

# 进入容器
docker exec -it vikpea_api bash

# 重启服务
docker restart vikpea_api

# 完全重置
docker-compose down -v
docker-compose up -d --build
```

---

## ✅ 验证安装

### 后端检查
```bash
# 访问 API 文档
curl http://localhost:8000/docs

# 健康检查
curl http://localhost:8000/health
```

### 前端检查
```bash
# 访问首页
curl http://localhost:3000

# 检查是否有错误
npm run type-check
```

---

## 🐛 故障排除

### 后端无法启动
```bash
# 检查 Python 版本
python3 --version  # 需要 3.10+

# 检查依赖
pip list

# 重新安装依赖
pip install -r requirements.txt --upgrade

# 检查端口占用
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### 前端无法启动
```bash
# 检查 Node 版本
node --version  # 需要 18+

# 清除缓存
rm -rf .next node_modules
npm install

# 检查环境变量
cat .env.local
```

### 数据库连接错误
```bash
# 检查 PostgreSQL 是否运行
psql -U vikpea -d vikpea_db -c "SELECT 1"

# 检查 Redis
redis-cli ping
```

### Docker 错误
```bash
# 检查 Docker 状态
docker ps

# 重建镜像
docker-compose up -d --build

# 清理所有数据（谨慎！）
docker-compose down -v
```

---

## 📚 进一步阅读

- [后端 API 文档](./docs/WEB_API_GUIDE.md)
- [前端 README](./frontend/README.md)
- [项目结构](./API_STRUCTURE.md)
- [项目配置说明](./docs/PROJECT_CONFIG.md)

---

## 🎓 学习资源

### 后端
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://www.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev

### 前端
- Next.js: https://nextjs.org
- React: https://react.dev
- Tailwind CSS: https://tailwindcss.com

### DevOps
- Docker: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose

---

## 💡 开发小贴士

1. **开发时使用 `--reload` 标志自动重新加载**
   ```bash
   uvicorn app:app --reload
   ```

2. **使用 TypeScript 获得更好的类型检查**
   ```bash
   npm run type-check
   ```

3. **定期提交代码**
   ```bash
   git add .
   git commit -m "描述变更"
   ```

4. **使用 Git 忽略敏感文件**
   - `.env` 文件不应提交到 Git
   - 使用 `.env.example` 作为模板

---

## 🎉 完成！

现在您的 VikPea 项目应该已经完全配置好了！

- ✅ 后端 API 已就绪
- ✅ 前端界面已就绪
- ✅ 数据库已配置
- ✅ 文档已完整

**开始开发吧！** 🚀
