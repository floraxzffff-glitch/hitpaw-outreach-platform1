#!/bin/bash

# VikPea 2.0 项目最终验证检查清单
# 运行此脚本验证项目完整性

set -e

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  VikPea 2.0 项目最终验证检查               ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
TOTAL=0
PASSED=0
FAILED=0

# 检查函数
check_file() {
    local file=$1
    local description=$2
    TOTAL=$((TOTAL + 1))
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description ($file)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $description ($file)"
        FAILED=$((FAILED + 1))
    fi
}

check_dir() {
    local dir=$1
    local description=$2
    TOTAL=$((TOTAL + 1))
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description ($dir)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $description ($dir)"
        FAILED=$((FAILED + 1))
    fi
}

# ============ 后端检查 ============
echo -e "${BLUE}📦 后端文件${NC}"

check_dir "api" "后端目录"
check_file "api/app.py" "主应用文件"
check_file "api/models.py" "数据模型"
check_file "api/config.py" "配置管理"
check_file "api/client.py" "Python 客户端"
check_file "api/requirements.txt" "Python 依赖"
check_file "api/.env.example" "环境变量模板"
check_file "api/Dockerfile" "后端 Docker"
check_file "api/README.md" "后端文档"

# ============ 前端检查 ============
echo ""
echo -e "${BLUE}🎨 前端文件${NC}"

check_dir "frontend" "前端目录"
check_dir "frontend/app" "App Router 目录"
check_file "frontend/app/layout.tsx" "根布局"
check_file "frontend/app/page.tsx" "首页"
check_file "frontend/app/dashboard/page.tsx" "仪表板"
check_file "frontend/app/analyze/page.tsx" "关键词分析"
check_file "frontend/app/email/page.tsx" "邮箱验证"
check_file "frontend/app/seo/page.tsx" "SEO 扫描"
check_file "frontend/app/reports/page.tsx" "报告管理"
check_dir "frontend/app/components" "组件目录"
check_file "frontend/app/components/Navbar.tsx" "导航栏"
check_file "frontend/app/components/LoadingSpinner.tsx" "加载动画"
check_file "frontend/app/components/ErrorAlert.tsx" "错误提示"
check_file "frontend/app/components/SuccessAlert.tsx" "成功提示"
check_file "frontend/app/components/StatsCard.tsx" "统计卡片"
check_dir "frontend/lib" "库目录"
check_file "frontend/lib/api/vikpea.ts" "API 客户端"
check_file "frontend/lib/utils/helpers.ts" "工具函数"
check_file "frontend/lib/store.ts" "状态管理"
check_file "frontend/package.json" "前端依赖"
check_file "frontend/tsconfig.json" "TypeScript 配置"
check_file "frontend/tailwind.config.js" "Tailwind 配置"
check_file "frontend/postcss.config.js" "PostCSS 配置"
check_file "frontend/next.config.js" "Next.js 配置"
check_file "frontend/.env.local.example" "环境变量"
check_file "frontend/Dockerfile" "前端 Docker"
check_file "frontend/README.md" "前端文档"
check_file "frontend/.gitignore" "Git 忽略"

# ============ 部署文件检查 ============
echo ""
echo -e "${BLUE}🐳 部署文件${NC}"

check_file "docker-compose.yml" "Docker Compose 配置"
check_file "setup.sh" "自动配置脚本"
check_file "docker-start.sh" "Docker 启动脚本"
check_file "start-backend.sh" "后端启动脚本"
check_file "start-frontend.sh" "前端启动脚本"

# ============ 文档检查 ============
echo ""
echo -e "${BLUE}📚 文档文件${NC}"

check_file "README.md" "项目主文档"
check_file "GETTING_STARTED.md" "启动指南"
check_file "DOCUMENTATION_INDEX.md" "文档索引"
check_file "PROJECT_COMPLETION_CHECKLIST.md" "完成清单"
check_file "API_STRUCTURE.md" "项目结构说明"
check_dir "docs" "文档目录"
check_file "docs/WEB_API_GUIDE.md" "API 完整文档"
check_file "examples/api_integration.py" "集成示例"

# ============ 配置文件检查 ============
echo ""
echo -e "${BLUE}⚙️  配置文件${NC}"

check_file ".gitignore" "Git 忽略规则"
check_file "generate-stats.py" "统计脚本"

# ============ 统计摘要 ============
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  检查结果摘要                              ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "检查项总数：$TOTAL"
echo -e "${GREEN}通过：$PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}失败：$FAILED${NC}"
else
    echo -e "${GREEN}失败：0${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有文件检查通过！项目完整性验证成功！${NC}"
    echo ""
    echo "📊 项目统计："
    echo "  后端代码文件：4 个"
    echo "  前端代码文件：15+ 个"
    echo "  配置文件：10+ 个"
    echo "  文档文件：8 个"
    echo "  脚本文件：5 个"
    echo ""
    echo "🚀 下一步："
    echo "  1. 运行配置脚本：./setup.sh"
    echo "  2. 启动后端：./start-backend.sh"
    echo "  3. 启动前端：./start-frontend.sh"
    echo "  4. 访问应用：http://localhost:3000"
    echo ""
else
    echo -e "${RED}❌ 项目文件缺失，请检查上面的失败项${NC}"
    exit 1
fi

echo "════════════════════════════════════════════"
echo ""
