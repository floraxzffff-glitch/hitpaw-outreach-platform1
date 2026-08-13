"""
VikPea 项目初始化模块
"""

import sys
from pathlib import Path

# 确保可以导入 src 包
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .init_project import main

__all__ = ["main"]
