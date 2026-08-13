#!/bin/bash
# VikPea 运行脚本 - macOS CLI 工作台

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 运行 CLI 工作台
python -m src.ui.cli_menu
