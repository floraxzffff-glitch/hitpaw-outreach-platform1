#!/bin/bash
# VikPea 项目初始化脚本（macOS）

echo "=========================================="
echo "VikPea 外联工作台 - 项目初始化"
echo "=========================================="

# 检查 Python 版本
PYTHON_CMD=""
for py in python3.12 python3.11 python3.10 python3; do
    if command -v $py &> /dev/null; then
        VERSION=$($py -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
        if [[ $VERSION > "3.9" ]]; then
            PYTHON_CMD=$py
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ 需要 Python 3.10 或更高版本"
    exit 1
fi

echo "✓ 使用 Python: $PYTHON_CMD"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo "正在升级 pip..."
pip install --upgrade pip setuptools wheel

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 创建配置目录
mkdir -p config data logs

# 复制配置模板
if [ ! -f "config/config.xlsx" ]; then
    echo "✓ 请在 config/ 目录中创建 config.xlsx（参考 config_template.xlsx）"
fi

if [ ! -f "config/blacklist.xlsx" ]; then
    echo "✓ 请在 config/ 目录中创建 blacklist.xlsx"
fi

echo ""
echo "=========================================="
echo "✓ 初始化完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. source venv/bin/activate  (激活虚拟环境)"
echo "2. python -m src.ui.cli_menu  (启动工作台)"
echo ""
