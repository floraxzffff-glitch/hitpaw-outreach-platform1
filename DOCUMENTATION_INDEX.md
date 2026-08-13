# 🎯 VikPea 2.0 项目 - 核心文档导航

> 快速查找您需要的文档

## 📋 按需要查找

### 🆕 我是第一次接触这个项目？
→ 从这里开始：[README.md](./README.md)
- 项目概览
- 核心功能
- 技术栈
- 快速开始

### 🚀 我想立即启动项目
→ 按照这个步骤：[GETTING_STARTED.md](./GETTING_STARTED.md)
- 三种启动方式
- 环境配置
- 故障排除
- 常用命令速查

### 👨‍💻 我是后端开发者
→ 查看这些文档：
- [docs/WEB_API_GUIDE.md](./docs/WEB_API_GUIDE.md) - 完整 API 文档
- [API_STRUCTURE.md](./API_STRUCTURE.md) - 项目结构
- [examples/api_integration.py](./examples/api_integration.py) - 代码示例

### 🎨 我是前端开发者
→ 查看这些文档：
- [frontend/README.md](./frontend/README.md) - 前端开发指南
- [frontend/package.json](./frontend/package.json) - 依赖列表
- 代码位置：`frontend/app/` 和 `frontend/lib/`

### 🐳 我想用 Docker 部署
→ 按照这个步骤：
1. 查看 [GETTING_STARTED.md](./GETTING_STARTED.md) 中的 Docker 部分
2. 运行 `./docker-start.sh`
3. 访问 http://localhost:3000

### 📚 我想深入了解 API
→ 查看：
- [docs/WEB_API_GUIDE.md](./docs/WEB_API_GUIDE.md) - 详细文档
- http://localhost:8000/docs - 实时文档（启动后）
- [examples/](./examples/) - 集成示例

### 🚢 我想部署到生产
→ 查看 [GETTING_STARTED.md](./GETTING_STARTED.md) 中的云部署部分

### ❓ 我遇到了问题
→ 查看 [GETTING_STARTED.md](./GETTING_STARTED.md) 中的故障排除部分

---

## 📁 文件导航

### 根目录重要文件

| 文件 | 说明 | 用途 |
|------|------|------|
| **README.md** | 项目总览 | 了解项目 |
| **GETTING_STARTED.md** | 详细启动指南 | 启动项目 |
| **setup.sh** | 自动配置脚本 | 环境配置 |
| **docker-start.sh** | Docker 启动 | Docker 部署 |
| **docker-compose.yml** | 容器编排 | Docker 配置 |
| **start-backend.sh** | 后端启动 | 本地开发 |
| **start-frontend.sh** | 前端启动 | 本地开发 |

### 后端文件（`api/`）

| 文件 | 功能 | 行数 |
|------|------|------|
| **app.py** | 主 API 应用 | 600+ |
| **models.py** | 数据库模型 | 300+ |
| **config.py** | 配置管理 | 100+ |
| **client.py** | Python 客户端 | 400+ |

### 前端文件（`frontend/`）

| 目录 | 内容 |
|------|------|
| **app/dashboard/** | 仪表板页面 |
| **app/analyze/** | 关键词分析 |
| **app/email/** | 邮箱验证 |
| **app/seo/** | SEO 扫描 |
| **app/reports/** | 报告管理 |
| **app/components/** | 通用 UI 组件 |
| **lib/api/** | API 客户端 |
| **lib/utils/** | 工具函数 |

### 文档文件（`docs/`）

| 文件 | 说明 |
|------|------|
| **WEB_API_GUIDE.md** | 完整 API 文档 |

---

## 🔥 常用命令

### 快速启动
```bash
# 一键配置
./setup.sh

# 后端开发
./start-backend.sh

# 前端开发
./start-frontend.sh

# Docker 启动
./docker-start.sh
```

### 开发命令
```bash
# 后端
cd api
source venv/bin/activate
python3 -m uvicorn app:app --reload

# 前端
cd frontend
npm run dev

# 检查
npm run type-check
npm run lint
```

### Docker 命令
```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f api
docker-compose logs -f frontend

# 停止
docker-compose down
```

---

## 💡 核心概念

### 功能模块

**1. 关键词分析** (`/analyze`)
- 输入关键词和参数
- 系统分析搜索潜力
- 显示邮箱发现率

**2. 邮箱验证** (`/email`)
- 单个或批量验证邮箱
- 检查黑名单状态
- 显示置信度评分

**3. SEO 扫描** (`/seo`)
- 输入关键词
- 发现 SEO 机会
- 显示优先级等级（A/B/C）

**4. 报告管理** (`/reports`)
- 生成多类型报告
- 查看和下载报告

**5. 仪表板** (`/dashboard`)
- 显示统计数据
- 快速导航
- 系统状态检查

---

## 🎓 学习路径

### 初级（了解项目）
1. 阅读 [README.md](./README.md)
2. 运行 `./setup.sh`
3. 启动服务访问 http://localhost:3000
4. 浏览各个功能页面

### 中级（开发改进）
1. 阅读 [frontend/README.md](./frontend/README.md)
2. 了解前端代码结构
3. 修改样式或添加组件
4. 查看 [docs/WEB_API_GUIDE.md](./docs/WEB_API_GUIDE.md)

### 高级（部署运维）
1. 理解 Docker 配置
2. 配置数据库和缓存
3. 部署到云平台
4. 配置 CI/CD

---

## ✨ 项目特色

✅ **完整的全栈应用**
- 后端：FastAPI + SQLAlchemy + PostgreSQL
- 前端：Next.js + TypeScript + Tailwind CSS

✅ **生产就绪**
- Docker 容器化
- 多环境配置
- 错误处理完善

✅ **开发者友好**
- 详细的文档
- 丰富的代码示例
- 一键启动脚本

✅ **可扩展设计**
- 模块化架构
- 清晰的接口
- 易于集成

---

## 📞 快速参考

### 前端地址
- 主应用：http://localhost:3000
- 仪表板：http://localhost:3000/dashboard
- 关键词分析：http://localhost:3000/analyze
- 邮箱验证：http://localhost:3000/email
- SEO 扫描：http://localhost:3000/seo
- 报告管理：http://localhost:3000/reports

### 后端地址
- API 基地址：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 数据库管理：http://localhost:8080（Adminer）

### 端口分配
- 前端：3000
- 后端 API：8000
- PostgreSQL：5432
- Redis：6379
- Nginx：80/443
- Adminer：8080

---

## 🆘 需要帮助？

### 文档不完整或有错误？
- 查看 [GETTING_STARTED.md](./GETTING_STARTED.md) 的故障排除部分
- 查看代码注释
- 检查 [docs/WEB_API_GUIDE.md](./docs/WEB_API_GUIDE.md)

### 无法启动项目？
- 检查 Python 3.10+ 和 Node.js 18+ 已安装
- 运行 `./setup.sh` 进行环境配置
- 查看 Docker 日志：`docker-compose logs`

### API 端点不工作？
- 检查后端是否运行：http://localhost:8000/health
- 查看 API 文档：http://localhost:8000/docs
- 检查数据库连接

---

## 📈 项目统计

- **代码行数**: ~6000 行
- **文件数量**: 40+ 个
- **API 端点**: 25+ 个
- **数据库表**: 9 个
- **UI 页面**: 5 个
- **UI 组件**: 5+ 个

---

## ✅ 项目完成度

🟢 **100% 完成** - 所有计划功能已实现

- ✅ 后端 API
- ✅ 前端 UI
- ✅ 数据库模型
- ✅ Docker 配置
- ✅ 部署脚本
- ✅ 完整文档

---

**准备好了吗？开始使用吧！** 🚀

👉 [点击这里查看详细启动指南](./GETTING_STARTED.md)
