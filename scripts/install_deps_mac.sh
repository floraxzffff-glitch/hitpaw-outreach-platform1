#!/bin/bash
# VikPea 安装依赖脚本 - macOS

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "VikPea 外联工作台 - macOS 安装"
echo "=========================================="

# 检查 Python 版本
echo ""
echo "✓ 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  当前 Python: $PYTHON_VERSION"

# 创建虚拟环境
echo ""
echo "✓ 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  虚拟环境已创建"
else
    echo "  虚拟环境已存在"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo ""
echo "✓ 升级 pip..."
pip install --upgrade pip setuptools wheel

# 安装依赖
echo ""
echo "✓ 安装依赖包..."
pip install -r requirements.txt

# 可选：安装开发依赖
read -p "是否安装开发依赖? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install pytest pytest-cov black flake8
fi

# 创建配置文件目录
echo ""
echo "✓ 创建配置目录..."
mkdir -p config data logs

# 初始化配置文件
if [ ! -f "config/config.xlsx" ]; then
    echo "  📝 请在 config/config.xlsx 中填入邮箱配置"
fi

if [ ! -f "config/blacklist.xlsx" ]; then
    echo "  📝 请在 config/blacklist.xlsx 中配置黑名单"
fi

echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "后续步骤:"
echo "  1. 编辑配置文件:"
echo "     nano config/config.xlsx"
echo ""
echo "  2. 激活虚拟环境:"
echo "     source venv/bin/activate"
echo ""
echo "  3. 运行工作台:"
echo "     python -m src.ui.cli_menu"
echo ""
