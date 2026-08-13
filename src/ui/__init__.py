"""
UI 模块 - CLI 和 GUI 入口
"""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MENU = [
    ("1", "交付前自检 / 今日状态", "src.inspection.pre_delivery_check"),
    ("2", "搜索 YouTube KOL", "src.searchers.youtube_search"),
    ("3", "搜索文章站点", "src.searchers.article_search"),
    ("4", "深度找邮箱", "src.email_finder.deep_finder"),
    ("5", "邮箱体检", "src.core.email_validator"),
    ("6", "发送首封开发信", "src.outreach.sender"),
    ("7", "读取邮箱回复", "src.email_tracking.reply_reader"),
    ("8", "自动跟进", "src.outreach.followup"),
    ("9", "关键词复盘", "src.analysis.keyword_review"),
    ("10", "补录最近已发送邮件", "src.email_tracking.sent_updater"),
    ("11", "补录最近回复状态", "src.email_tracking.status_recorder"),
    ("12", "SEO渠道机会扫描", "src.searchers.seo_scanner"),
    ("13", "关键词聚类", "src.analysis.keyword_clustering"),
]


def preferred_python():
    """查找最合适的 Python 3.10+ 版本"""
    if sys.version_info >= (3, 10):
        return sys.executable
    
    candidates = [
        "/usr/local/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
        "/opt/homebrew/bin/python3",
    ]
    
    for path in candidates:
        if os.path.exists(path):
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                version_text = (result.stdout or result.stderr or "").strip()
                if "Python " in version_text:
                    version = version_text.replace("Python ", "").split()[0]
                    parts = version.split(".")
                    major = int(parts[0])
                    minor = int(parts[1]) if len(parts) > 1 else 0
                    if (major, minor) >= (3, 10):
                        return path
            except Exception:
                continue
    
    return sys.executable


def run_module(module_name):
    """运行指定的 Python 模块"""
    python_exec = preferred_python()
    try:
        subprocess.run([python_exec, "-m", module_name], check=True)
    except Exception as e:
        print(f"❌ 运行失败: {e}")


def main():
    """CLI 工作台主菜单"""
    python_exec = preferred_python()
    if sys.executable != python_exec:
        print(f"✓ 已切换到 Python {python_exec}")
    
    while True:
        print("\n" + "=" * 64)
        print("  VikPea 外联工作台")
        print("=" * 64)
        for key, label, _ in MENU:
            print(f"  {key:>2}. {label}")
        print("   0. 退出")
        
        choice = input("\n请选择要运行的步骤: ").strip()
        if choice == "0":
            print("已退出")
            return
        
        matched = [item for item in MENU if item[0] == choice]
        if matched:
            _, label, module = matched[0]
            print(f"\n运行: {label}")
            print("-" * 60)
            run_module(module)
        else:
            print("❌ 选择无效")


if __name__ == "__main__":
    main()
