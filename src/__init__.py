"""
VikPea 外联工作台 - 自动化邮箱开发工具
"""

__version__ = "2.0.0"
__author__ = "HitPaw Team"

import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
