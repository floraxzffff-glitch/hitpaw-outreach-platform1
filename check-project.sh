#!/bin/bash

# VikPea 2.0 项目完成总结
# 生成项目统计和文档

echo "========================================"
echo "📊 VikPea 2.0 项目完成统计"
echo "========================================"
echo ""

# 统计代码行数
echo "📈 代码统计："
echo ""

echo "后端代码:"
find api -name "*.py" -type f | xargs wc -l | tail -1

echo ""
echo "前端代码:"
find frontend -name "*.tsx" -o -name "*.ts" -o -name "*.js" | xargs wc -l 2>/dev/null | tail -1

echo ""
echo "文档:"
find docs -name "*.md" | xargs wc -l | tail -1

echo ""
echo "========================================"
echo "📁 项目文件清单"
echo "========================================"
echo ""

echo "✅ 后端文件:"
ls -la api/ | grep -E "\.py$|requirements|Dockerfile"
echo ""

echo "✅ 前端文件:"
ls -la frontend/app/ | head -10
echo ""

echo "✅ 配置和脚本:"
ls -la | grep -E "\.sh$|\.yml$"
echo ""

echo "✅ 文档:"
ls -la docs/
echo ""

echo "========================================"
echo "🚀 快速验证"
echo "========================================"
echo ""

# 检查关键文件
files=(
  "api/app.py"
  "api/models.py"
  "api/config.py"
  "frontend/app/layout.tsx"
  "frontend/app/dashboard/page.tsx"
  "frontend/app/analyze/page.tsx"
  "frontend/app/email/page.tsx"
  "frontend/app/seo/page.tsx"
  "frontend/app/reports/page.tsx"
  "frontend/lib/api/vikpea.ts"
  "docker-compose.yml"
  "GETTING_STARTED.md"
  "docs/WEB_API_GUIDE.md"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✓ $file"
  else
    echo "✗ $file (缺失)"
  fi
done

echo ""
echo "========================================"
echo "✨ 项目准备就绪！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 阅读 GETTING_STARTED.md"
echo "2. 运行 ./setup.sh 进行初始配置"
echo "3. 使用 ./start-backend.sh 和 ./start-frontend.sh 启动"
echo "4. 访问 http://localhost:3000"
echo ""
