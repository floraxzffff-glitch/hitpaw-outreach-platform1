#!/usr/bin/env python3
"""
VikPea 外联工作台 - 项目配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vikpea",
    version="2.0.0",
    author="HitPaw Team",
    description="自动化邮箱开发工具：搜索KOL、提取邮箱、批量发信、追踪回复",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hitpaw/vikpea",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Communications :: Email",
        "Topic :: Internet",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openpyxl>=3.10.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "yt-dlp>=2024.1.1",
        "certifi>=2023.7.22",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "vikpea=src.ui.cli_menu:main",
            "vikpea-gui=src.ui.gui_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.xlsx", "*.txt", "*.md"],
    },
)
