#!/bin/bash
# GUI 应用启动脚本（macOS）

if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: bash scripts/init_project.sh"
    exit 1
fi

source venv/bin/activate
python -m src.ui.gui_app
