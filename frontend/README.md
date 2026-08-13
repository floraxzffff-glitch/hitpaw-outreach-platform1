# VikPea Next.js 前端

> 强大的 SEO 和邮箱开发工具的 Next.js 前端界面

## 📋 技术栈

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **API Communication**: RESTful API (FastAPI)

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
# 或使用 yarn
yarn install
```

### 2. 配置环境变量

复制环境变量示例并填入实际配置：

```bash
cp .env.local.example .env.local
```

编辑 `.env.local`：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=VikPea
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
npm start
```

## 📁 项目结构

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # 根布局
│   ├── page.tsx                 # 首页（重定向到仪表板）
│   ├── globals.css              # 全局样式
│   │
│   ├── dashboard/
│   │   └── page.tsx             # 仪表板页面
│   │
│   ├── analyze/
│   │   └── page.tsx             # 关键词分析页面
│   │
│   ├── email/
│   │   └── page.tsx             # 邮箱验证页面
│   │
│   ├── seo/
│   │   └── page.tsx             # SEO 扫描页面
│   │
│   ├── reports/
│   │   └── page.tsx             # 报告页面
│   │
│   └── components/              # 通用组件
│       ├── Navbar.tsx           # 导航栏
│       ├── LoadingSpinner.tsx    # 加载动画
│       ├── ErrorAlert.tsx        # 错误提示
│       ├── SuccessAlert.tsx      # 成功提示
│       └── StatsCard.tsx         # 统计卡片
│
├── lib/
│   ├── api/
│   │   └── vikpea.ts            # API 调用库（核心）
│   ├── utils/
│   │   └── helpers.ts           # 工具函数
│   └── store.ts                 # 状态管理 (Zustand)
│
├── public/                      # 静态资源
├── .env.local.example           # 环境变量示例
├── next.config.js               # Next.js 配置
├── tailwind.config.js           # Tailwind CSS 配置
├── postcss.config.js            # PostCSS 配置
├── tsconfig.json                # TypeScript 配置
└── package.json                 # 项目依赖
```

## 🎨 主要功能页面

### 1. 仪表板 (`/dashboard`)
- 显示统计数据（关键词分析数、邮箱验证数等）
- 显示今日活动
- 功能导航链接
- 快速入门指南

### 2. 关键词分析 (`/analyze`)
- 输入关键词并选择搜索源（文章、YouTube、SEO）
- 自定义搜索结果数量和最低评分
- 显示分析结果：
  - 找到结果数
  - 有效结果数
  - 邮箱找到数
  - 邮箱命中率
  - 详细信息

### 3. 邮箱验证 (`/email`)
- 单个邮箱验证
- 批量邮箱验证
- 粘贴邮箱列表
- 显示验证结果：
  - 邮箱有效性
  - 黑名单状态
  - 置信度评分
  - 统计摘要

### 4. SEO 扫描 (`/seo`)
- 输入关键词进行 SEO 机会扫描
- 显示机会等级（A/B/C）
- 显示相关性评分
- 显示建议和行动方案
- 快速跳转到网站

### 5. 报告 (`/reports`)
- 生成三类报告：
  - 关键词复盘
  - SEO 分析
  - 邮箱验证
- 查看最近报告列表
- 下载报告文件

## 🔌 API 集成

所有 API 调用通过 `lib/api/vikpea.ts` 进行：

```typescript
import vikpeaAPI from '@/lib/api/vikpea';

// 异步使用
const result = await vikpeaAPI.analyzeKeyword('python', 'article');

// 获取统计
const stats = await vikpeaAPI.getStats();

// 生成报告
const report = await vikpeaAPI.generateReport('keyword_review');
```

## 🎨 UI 样式

使用 Tailwind CSS 进行样式设计，支持：
- 响应式设计
- 深色模式支持（可配置）
- 自定义颜色方案
- 平滑过渡和动画

## 📱 响应式设计

- **Mobile First**: 优先为移动设备设计
- **Breakpoints**:
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px

## 🔐 安全性

- 环境变量管理（敏感信息不提交到 Git）
- CORS 处理（由后端配置）
- 输入验证（邮箱格式、关键词长度等）
- 错误处理和用户反馈

## 📊 状态管理

使用 Zustand 进行轻量级状态管理：

```typescript
import { useApiStore } from '@/lib/store';

const { keywordResult, setKeywordResult, isLoading, setIsLoading } = useApiStore();
```

## 🧪 开发建议

1. **开发模式**: `npm run dev`
   - 热重新加载
   - 完整错误信息

2. **类型检查**: `npm run type-check`
   - TypeScript 验证

3. **代码格式化**: `npm run format`
   - 使用 Prettier

4. **构建测试**: `npm run build`
   - 检查生产构建

## 🚢 部署

### Vercel（推荐）

```bash
npm i -g vercel
vercel
```

### 其他平台

设置环境变量：
```
NEXT_PUBLIC_API_URL=https://api.example.com
```

然后运行：
```bash
npm run build
npm start
```

## 📚 可用脚本

- `npm run dev` - 启动开发服务器
- `npm run build` - 生产构建
- `npm start` - 启动生产服务器
- `npm run lint` - 代码检查
- `npm run type-check` - TypeScript 检查
- `npm run format` - 代码格式化

## 🤝 后端集成

前端通过以下端点与后端通信：

```
POST   /api/analyze/keyword         - 分析关键词
POST   /api/analyze/batch           - 批量分析
POST   /api/validate/email          - 验证邮箱
POST   /api/seo/scan                - SEO 扫描
POST   /api/report/generate         - 生成报告
GET    /api/stats                   - 获取统计
GET    /health                      - 健康检查
```

详见 [API 文档](../docs/WEB_API_GUIDE.md)

## 🐛 故障排查

### 无法连接到后端
1. 检查 `NEXT_PUBLIC_API_URL` 配置
2. 确保后端服务正在运行
3. 检查 CORS 配置

### 页面加载失败
1. 检查浏览器控制台错误
2. 查看网络请求（DevTools）
3. 检查后端服务是否正常

### 构建错误
1. 运行 `npm install`
2. 删除 `.next` 目录并重新构建
3. 检查 TypeScript 错误

## 📞 技术支持

- Next.js 文档: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- Zustand: https://github.com/pmndrs/zustand
- Axios: https://axios-http.com/docs

## 📝 版本信息

- Next.js: 14.0.0+
- React: 18.2.0+
- Node.js: 18.0.0+
- TypeScript: 5.0.0+

## ✅ 项目就绪

前端应用已经完整配置，可以：
- ✅ 立即开发
- ✅ 一键部署
- ✅ 接入后端 API
- ✅ 响应式设计
- ✅ 生产级质量

---

**最后更新**: 2024-01-15  
**版本**: 2.0.0  
**状态**: 🟢 生产就绪
