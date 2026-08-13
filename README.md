# 🎯 VikPea 外联工作台 2.0 - 完整项目

> 一个强大的 SEO 和邮箱开发自动化平台，现已升级为专业级 Web 应用

## 📊 项目概览

VikPea 是一个综合的外链开发工作台，通过整合关键词分析、邮箱验证、SEO 机会扫描等功能，帮助营销团队自动化和优化其工作流程。

### 🌟 核心特性

- 📈 **关键词分析** - 深度分析关键词潜力和邮箱发现率
- ✉️ **邮箱验证** - 批量验证邮箱地址有效性和黑名单状态
- 🔍 **SEO 扫描** - 发现高价值的 SEO 机会和合作目标
- 📊 **报告生成** - 自动生成详细的分析和统计报告
- 🎨 **现代 UI** - 优雅的 Next.js 前端界面
- 🚀 **生产就绪** - 完整的后端 API 和部署配置

---

## 🏗️ 项目架构

**全栈应用**
- 后端: FastAPI + PostgreSQL + Redis
- 前端: Next.js + TypeScript + Tailwind CSS
- 部署: Docker + Docker Compose
- 云服务: Vercel (前端) + Render/AWS (后端)

---

## 🚀 快速开始

## 🚀 快速开始

### ⚡ 最快启动（3 步）

```bash
# 1. 配置环境
chmod +x setup.sh
./setup.sh

# 2. 启动后端（新终端）
./start-backend.sh

# 3. 启动前端（新终端）
./start-frontend.sh
```

访问 **http://localhost:3000**

### 🐳 使用 Docker（推荐）

```bash
chmod +x docker-start.sh
./docker-start.sh
```

访问地址：
- 前端: http://localhost:3000
- API 文档: http://localhost:8000/docs

详见 [GETTING_STARTED.md](./GETTING_STARTED.md) 了解更多启动方式

---

## 📚 主要文档

| 文档 | 说明 |
|------|------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | 详细启动指南 |
| [frontend/README.md](./frontend/README.md) | 前端开发指南 |
| [docs/WEB_API_GUIDE.md](./docs/WEB_API_GUIDE.md) | API 完整文档 |
| [API_STRUCTURE.md](./API_STRUCTURE.md) | 项目结构说明 |

---

## 📁 项目结构

### 环境要求
- Python 3.10+
- macOS / Linux / Windows
- Aliyun 企业邮箱账号（可选，可改为其他SMTP服务）

### 2. 安装

```bash
# 克隆或下载项目
cd VikPea

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化配置和数据文件
python -m src.scripts.init_project
```

### 3. 配置

复制示例配置文件：
```bash
cp config/config_template.xlsx config/config.xlsx
cp config/blacklist_template.xlsx config/blacklist.xlsx
```

在 Excel 中编辑以下文件：
- `config/config.xlsx` - SMTP/IMAP 服务器、邮箱账号、发信模板等
- `config/blacklist.xlsx` - 黑名单（邮箱/域名/公司名）

### 4. 运行

**CLI 工作台（推荐）：**
```bash
python -m src.ui.cli_menu
```

**GUI 桌面应用：**
```bash
python -m src.ui.gui_app
```

**单个脚本：**
```bash
python -m src.searchers.youtube_search        # 搜索 YouTube KOL
python -m src.searchers.article_search        # 搜索文章站点
python -m src.email_finder.deep_finder        # 深度找邮箱
python -m src.outreach.sender                 # 发送开发信
python -m src.email_tracking.reply_reader     # 读取回复
```

## 项目结构


```
VikPea_项目改进版/
│
├── 📁 api/                          # FastAPI 后端
│   ├── app.py                       # 主应用入口（600+ 行）
│   ├── models.py                    # SQLAlchemy ORM 模型
│   ├── config.py                    # 配置管理
│   ├── client.py                    # Python 客户端库
│   ├── requirements.txt              # Python 依赖
│   ├── .env.example                 # 环境变量模板
│   └── Dockerfile                   # Docker 配置
│
├── 📁 frontend/                     # Next.js 前端
│   ├── 📁 app/                      # App Router 应用
│   │   ├── layout.tsx               # 根布局
│   │   ├── dashboard/page.tsx       # 仪表板
│   │   ├── analyze/page.tsx         # 关键词分析
│   │   ├── email/page.tsx           # 邮箱验证
│   │   ├── seo/page.tsx             # SEO 扫描
│   │   ├── reports/page.tsx         # 报告管理
│   │   ├── components/              # 通用组件
│   │   └── globals.css              # 全局样式
│   │
│   ├── 📁 lib/
│   │   ├── api/vikpea.ts            # API 客户端
│   │   ├── utils/helpers.ts         # 工具函数
│   │   └── store.ts                 # 状态管理
│   │
│   ├── package.json                 # 依赖定义
│   ├── next.config.js               # Next.js 配置
│   ├── .env.local.example           # 环境变量
│   └── Dockerfile                   # Docker 配置
│
├── 📁 docs/                         # 文档
│   └── WEB_API_GUIDE.md             # API 完整指南
│
├── 📁 examples/                     # 代码示例
│   └── api_integration.py           # 集成示例
│
├── 🐳 docker-compose.yml            # Docker 编排
├── 📋 GETTING_STARTED.md            # 启动指南
├── 📖 README.md                     # 本文件
│
├── 🚀 setup.sh                      # 一键配置
├── 🐳 docker-start.sh               # Docker 启动
├── 🔙 start-backend.sh              # 后端启动
├── 🔜 start-frontend.sh             # 前端启动
│
└── .gitignore                       # Git 忽略文件
```

---

## 🛠️ 技术栈

### 后端
- **FastAPI 0.104.1** - 现代 Python Web 框架
- **SQLAlchemy 2.0.23** - ORM 对象关系映射
- **Pydantic 2.5.0** - 数据验证
- **PostgreSQL 15** - 数据库
- **Redis 7** - 缓存

### 前端
- **Next.js 14** - React 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理
- **Axios** - HTTP 客户端

### DevOps
- **Docker** - 容器化
- **Docker Compose** - 容器编排
- **Nginx** - 反向代理

---

## 🎯 API 端点
