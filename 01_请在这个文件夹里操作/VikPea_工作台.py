"""
VikPea_工作台.py — colleague-friendly menu for the outreach scripts.

Run:
  python VikPea_工作台.py
"""

import os
import subprocess
import sys
import shutil

from VikPea_common import create_default_workbooks, log_event


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MENU = [
    ("1", "交付前自检 / 今日状态", "VikPea_交付前自检.py"),
    ("2", "搜索 YouTube KOL", "VikPea_YouTube批量搜索.py"),
    ("3", "搜索文章站点", "VikPea_文章批量搜索.py"),
    ("4", "深度找邮箱", "VikPea_深度找邮箱.py"),
    ("5", "邮箱体检", "VikPea_邮箱体检.py"),
    ("6", "发送首封开发信", "VikPea_读表发信.py"),
    ("7", "读取邮箱回复", "VikPea_读取回复.py"),
    ("8", "自动跟进", "VikPea_自动跟进.py"),
    ("9", "关键词复盘", "VikPea_关键词复盘.py"),
    ("10", "补录最近已发送邮件", "VikPea_补录已发送邮件.py"),
    ("11", "补录最近回复状态", "VikPea_补录回复状态.py"),
    ("12", "SEO渠道机会扫描", "VikPea_SEO渠道机会扫描.py"),
    ("13", "关键词聚类", "VikPea_关键词聚类.py"),
]


def preferred_python():
    candidates = []
    if sys.version_info >= (3, 10):
        return sys.executable
    for path in [
        "/usr/local/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
        "/opt/homebrew/bin/python3",
        shutil.which("python3") or "",
    ]:
        if path and path not in candidates and os.path.exists(path):
            candidates.append(path)
    for path in candidates:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=SCRIPT_DIR,
            )
            text = (result.stdout or result.stderr or "").strip()
            if "Python " not in text:
                continue
            version = text.replace("Python ", "").split()[0]
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            if (major, minor) >= (3, 10):
                return path
        except Exception:
            continue
    return sys.executable


def run_script(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(path):
        print(f"找不到脚本: {path}")
        return
    print(f"\n运行: {filename}\n{'-' * 60}")
    log_event("工作台", f"运行 {filename}")
    python_exec = preferred_python()
    subprocess.run([python_exec, path], cwd=SCRIPT_DIR)


def main():
    create_default_workbooks()
    python_exec = preferred_python()
    if sys.executable != python_exec:
        print(f"已自动切换子脚本到新版 Python: {python_exec}")
    else:
        print(f"当前工作台 Python: {python_exec}")
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
        if not matched:
            print("无效选择")
            continue
        run_script(matched[0][2])


if __name__ == "__main__":
    main()
