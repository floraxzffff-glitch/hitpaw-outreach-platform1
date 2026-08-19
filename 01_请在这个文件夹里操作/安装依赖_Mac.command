#!/bin/zsh
cd "$(dirname "$0")"
echo "正在检查 Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "没有找到 python3。请先安装 Python 3.10+：https://www.python.org/downloads/macos/"
  echo "安装后重新双击本文件。"
  read -k 1 "?按任意键退出..."
  exit 1
fi
python3 --version
echo
echo "正在安装依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install openpyxl requests beautifulsoup4 yt-dlp certifi
echo
echo "依赖安装完成。下一步双击 运行桌面程序_Mac.command"
read -k 1 "?按任意键退出..."
