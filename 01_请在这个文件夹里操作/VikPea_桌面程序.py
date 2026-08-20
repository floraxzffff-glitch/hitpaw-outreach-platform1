"""
VikPea_桌面程序.py — Tkinter desktop shell for the outreach workspace.

Run:
  python3 VikPea_桌面程序.py
"""

import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import signal

from VikPea_common import (
    create_default_workbooks,
    log_event,
    CONFIG_PATH,
    CONFIG_VKP_PATH,
    CONFIG_FP_PATH,
)


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

QUICK_FILES = [
    ("通用配置", CONFIG_PATH),
    ("VKP配置", CONFIG_VKP_PATH),
    ("FP配置", CONFIG_FP_PATH),
    ("黑名单", os.path.join(SCRIPT_DIR, "VikPea_黑名单.xlsx")),
    ("额外去重", os.path.join(SCRIPT_DIR, "VikPea_额外已联络去重.xlsx")),
    ("发信名单", os.path.join(SCRIPT_DIR, "VikPea_发信名单.xlsx")),
    ("邮件追踪", os.path.join(SCRIPT_DIR, "VikPea_邮件开发追踪.xlsx")),
    ("无邮箱候选", os.path.join(SCRIPT_DIR, "VikPea_无邮箱候选.xlsx")),
    ("待确认邮箱", os.path.join(SCRIPT_DIR, "VikPea_待确认邮箱.xlsx")),
    ("SEO机会扫描", os.path.join(SCRIPT_DIR, "VikPea_SEO渠道机会扫描.xlsx")),
    ("关键词聚类", os.path.join(SCRIPT_DIR, "VikPea_关键词聚类.xlsx")),
    ("YouTube关键词", os.path.join(SCRIPT_DIR, "VikPea_搜索关键词.xlsx")),
    ("文章关键词", os.path.join(SCRIPT_DIR, "VikPea_文章搜索关键词.xlsx")),
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


def open_path(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(path)
    if sys.platform == "darwin":
        subprocess.Popen(["open", path], cwd=SCRIPT_DIR)
    elif os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", path], cwd=SCRIPT_DIR)


class VikPeaDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VikPea 外联桌面程序")
        self.root.geometry("1280x820")
        self.root.minsize(1080, 720)

        create_default_workbooks()
        self.python_exec = preferred_python()
        self.proc = None
        self.output_queue = queue.Queue()
        self.selected_script = tk.StringVar(value=MENU[0][2])
        self.selected_label = tk.StringVar(value=MENU[0][1])
        self.status_var = tk.StringVar(value=f"准备就绪 | Python: {self.python_exec}")

        self._build_ui()
        self.root.after(120, self._drain_output_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.log("VikPea 桌面程序已启动。")
        self.log(f"当前运行 Python: {self.python_exec}")
        self.log("建议流程：先开配置表/关键词表，确认内容后，再点左侧模块运行。")

    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=12)
        left.grid(row=0, column=0, sticky="nsw")
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(self.root, padding=(0, 12, 12, 12))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        ttk.Label(left, text="运行模块", font=("", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        for i, (_key, label, script) in enumerate(MENU, start=1):
            ttk.Button(
                left,
                text=label,
                command=lambda s=script, l=label: self.set_selected_script(s, l),
                width=26,
            ).grid(row=i, column=0, sticky="ew", pady=3)

        controls = ttk.LabelFrame(left, text="当前操作", padding=10)
        controls.grid(row=len(MENU) + 1, column=0, sticky="ew", pady=(12, 0))
        controls.columnconfigure(0, weight=1)
        ttk.Label(controls, textvariable=self.selected_label, wraplength=220).grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(controls, text="运行当前模块", command=self.run_selected).grid(row=1, column=0, sticky="ew", pady=3)
        ttk.Button(controls, text="停止当前运行", command=self.stop_current).grid(row=2, column=0, sticky="ew", pady=3)
        ttk.Button(controls, text="清空日志", command=self.clear_log).grid(row=3, column=0, sticky="ew", pady=3)

        files = ttk.LabelFrame(left, text="常用文件", padding=10)
        files.grid(row=len(MENU) + 2, column=0, sticky="ew", pady=(12, 0))
        for idx, (label, path) in enumerate(QUICK_FILES):
            ttk.Button(files, text=label, command=lambda p=path: self.open_file(p), width=26).grid(
                row=idx, column=0, sticky="ew", pady=2
            )

        top = ttk.Frame(right)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="当前模块：", font=("", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(top, textvariable=self.selected_label).grid(row=0, column=1, sticky="w")

        tips = ttk.LabelFrame(right, text="输入提示", padding=10)
        tips.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        tips.columnconfigure(0, weight=1)
        tips_text = (
            "脚本运行中如果提示输入内容，可以在底部输入框里发送。\n"
            "常见输入：\n"
            "  p  -> 开启最近视频标题定制\n"
            "  y  -> 确认预览/继续\n"
            "  send / SEND  -> 正式发送\n"
            "  1 / 2 / 3 -> 选择配置表或菜单项"
        )
        ttk.Label(tips, text=tips_text, justify="left").grid(row=0, column=0, sticky="w")

        log_frame = ttk.LabelFrame(right, text="运行日志", padding=8)
        log_frame.grid(row=2, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap="word", bg="#111827", fg="#e5e7eb", insertbackground="#e5e7eb")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scroll.set)

        bottom = ttk.Frame(right)
        bottom.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(bottom)
        self.input_entry.grid(row=0, column=0, sticky="ew")
        self.input_entry.bind("<Return>", lambda _e: self.send_input())
        ttk.Button(bottom, text="发送输入", command=self.send_input).grid(row=0, column=1, padx=(8, 0))

        status = ttk.Label(self.root, textvariable=self.status_var, anchor="w", relief="sunken")
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def set_selected_script(self, script, label):
        self.selected_script.set(script)
        self.selected_label.set(label)
        self.status_var.set(f"已选择模块：{label}")

    def log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.delete("1.0", "end")
        self.status_var.set("日志已清空")

    def open_file(self, path):
        try:
            open_path(path)
            self.status_var.set(f"已打开：{os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("打开失败", f"无法打开文件：\n{path}\n\n原因：{exc}")

    def _enqueue_output(self, text):
        self.output_queue.put(text)

    def _reader_thread(self, stream, prefix=""):
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break
                self._enqueue_output(prefix + line.rstrip("\n"))
        except Exception as exc:
            self._enqueue_output(f"[读取输出失败] {exc}")
        finally:
            try:
                stream.close()
            except Exception:
                pass

    def _wait_thread(self):
        code = None
        try:
            code = self.proc.wait()
        except Exception:
            pass
        self.output_queue.put(("__DONE__", code))

    def run_selected(self):
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("已有任务在运行", "请先停止当前任务，或等它运行完。")
            return
        script = self.selected_script.get()
        label = self.selected_label.get()
        path = os.path.join(SCRIPT_DIR, script)
        if not os.path.exists(path):
            messagebox.showerror("找不到脚本", path)
            return
        cmd = [self.python_exec, "-u", path]
        self.log("\n" + "=" * 70)
        self.log(f"运行模块：{label}")
        self.log("命令：" + " ".join(cmd))
        self.log("=" * 70)
        log_event("桌面程序", f"运行 {script}")
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            self.proc = subprocess.Popen(
                cmd,
                cwd=SCRIPT_DIR,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                start_new_session=True,
            )
        except Exception as exc:
            messagebox.showerror("启动失败", str(exc))
            self.proc = None
            return

        self.status_var.set(f"运行中：{label}")
        threading.Thread(target=self._reader_thread, args=(self.proc.stdout,), daemon=True).start()
        threading.Thread(target=self._wait_thread, daemon=True).start()

    def send_input(self):
        text = self.input_entry.get().rstrip("\n")
        self.input_entry.delete(0, "end")
        if not text:
            return
        if not self.proc or self.proc.poll() is not None or not self.proc.stdin:
            self.log(f"> {text}")
            self.log("[提示] 当前没有正在等待输入的脚本。")
            return
        try:
            self.proc.stdin.write(text + "\n")
            self.proc.stdin.flush()
            self.log(f"> {text}")
            self.status_var.set("已发送输入")
        except Exception as exc:
            self.log(f"[发送输入失败] {exc}")

    def stop_current(self):
        if not self.proc or self.proc.poll() is not None:
            self.status_var.set("当前没有运行中的任务")
            return
        try:
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
            except Exception:
                self.proc.terminate()
            self.log("[系统] 已请求停止当前任务。")
            self.status_var.set("已停止当前任务")
        except Exception as exc:
            self.log(f"[停止失败] {exc}")

    def _drain_output_queue(self):
        try:
            while True:
                item = self.output_queue.get_nowait()
                if isinstance(item, tuple) and item and item[0] == "__DONE__":
                    code = item[1]
                    self.log(f"[系统] 任务结束，退出码：{code}")
                    self.status_var.set(f"任务结束，退出码：{code}")
                    self.proc = None
                else:
                    self.log(item)
        except queue.Empty:
            pass
        self.root.after(120, self._drain_output_queue)

    def _on_close(self):
        if self.proc and self.proc.poll() is None:
            if not messagebox.askyesno("确认退出", "当前还有任务在运行，确定要退出桌面程序吗？"):
                return
            try:
                try:
                    os.killpg(self.proc.pid, signal.SIGTERM)
                except Exception:
                    self.proc.terminate()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    app = VikPeaDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
