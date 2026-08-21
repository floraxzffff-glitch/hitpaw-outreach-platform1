"""
job_runner.py - 后台任务管理模块

为 VikPea 同步脚本提供异步执行能力，避免 HTTP 请求超时。
支持 Python 函数后台执行和子进程任务管理。
"""

import threading
import time
import uuid
import subprocess
from datetime import datetime
from typing import Dict, Optional, Callable, List, Any


class Job:
    """单个后台任务"""
    def __init__(self, job_id: str, resource: str, label: str = ""):
        self.job_id = job_id
        self.resource = resource
        self.label = label or resource
        self.status = "running"
        self.created_at = datetime.now()
        self.finished_at: Optional[datetime] = None
        self.result: Any = None
        self.error: Optional[str] = None
        self.log: List[str] = []
        self.thread: Optional[threading.Thread] = None
        self.process: Optional[subprocess.Popen] = None


# 全局任务存储
_jobs: Dict[str, Job] = {}
_jobs_lock = threading.Lock()


def _generate_job_id() -> str:
    """生成唯一任务 ID"""
    return f"job_{uuid.uuid4().hex[:12]}"


def start_job(resource: str, func: Callable, label: str = "", *args, **kwargs) -> str:
    """
    启动一个 Python 函数作为后台任务

    Args:
        resource: 资源类型（如 "email_send", "youtube_search"）
        func: 要执行的函数
        label: 任务标签
        *args, **kwargs: 传给函数的参数

    Returns:
        job_id: 任务 ID
    """
    job_id = _generate_job_id()
    job = Job(job_id, resource, label)

    def run_wrapper():
        try:
            result = func(*args, **kwargs)
            with _jobs_lock:
                job.status = "completed"
                job.result = result
                job.finished_at = datetime.now()
        except Exception as e:
            with _jobs_lock:
                job.status = "failed"
                job.error = str(e)
                job.finished_at = datetime.now()

    thread = threading.Thread(target=run_wrapper, daemon=True)
    job.thread = thread

    with _jobs_lock:
        _jobs[job_id] = job

    thread.start()
    return job_id


def start_subprocess_job(resource: str, cmd: List[str], label: str = "", cwd: str = None) -> str:
    """
    启动一个子进程作为后台任务

    Args:
        resource: 资源类型
        cmd: 命令行参数列表
        label: 任务标签
        cwd: 工作目录

    Returns:
        job_id: 任务 ID
    """
    job_id = _generate_job_id()
    job = Job(job_id, resource, label)

    def run_wrapper():
        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            job.process = process

            for line in process.stdout:
                with _jobs_lock:
                    job.log.append(line.rstrip("\n"))

            process.wait()

            with _jobs_lock:
                output = "\n".join(job.log)
                if process.returncode == 0:
                    job.status = "completed"
                    job.result = {"stdout": output, "returncode": 0}
                else:
                    job.status = "failed"
                    job.error = f"进程退出码 {process.returncode}"
                    job.result = {"stdout": output, "returncode": process.returncode}
                job.finished_at = datetime.now()
        except Exception as e:
            with _jobs_lock:
                job.status = "failed"
                job.error = str(e)
                job.finished_at = datetime.now()

    thread = threading.Thread(target=run_wrapper, daemon=True)
    job.thread = thread

    with _jobs_lock:
        _jobs[job_id] = job

    thread.start()
    return job_id


def stop_job(job_id: str) -> bool:
    """
    停止一个正在运行的任务

    Args:
        job_id: 任务 ID

    Returns:
        是否成功停止
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return False

        if job.status != "running":
            return False

        # 如果是子进程，终止进程
        if job.process:
            try:
                job.process.terminate()
                job.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                job.process.kill()

        job.status = "stopped"
        job.finished_at = datetime.now()
        return True


def get_job(job_id: str) -> Optional[Dict]:
    """
    获取任务状态

    Args:
        job_id: 任务 ID

    Returns:
        任务信息字典，如果任务不存在返回 None
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return None

        return {
            "job_id": job.job_id,
            "resource": job.resource,
            "label": job.label,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "result": job.result,
            "error": job.error,
            "log": job.log,
        }


def list_jobs(resource: Optional[str] = None) -> List[Dict]:
    """
    列出所有任务或指定资源的任务

    Args:
        resource: 资源类型过滤（可选）

    Returns:
        任务列表
    """
    with _jobs_lock:
        jobs = _jobs.values()
        if resource:
            jobs = [j for j in jobs if j.resource == resource]

        return [
            {
                "job_id": job.job_id,
                "resource": job.resource,
                "label": job.label,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "finished_at": job.finished_at.isoformat() if job.finished_at else None,
                "log": job.log,
            }
            for job in jobs
        ]


def is_resource_busy(resource: str) -> bool:
    """
    检查指定资源是否有正在运行的任务

    Args:
        resource: 资源类型

    Returns:
        是否有任务正在运行
    """
    with _jobs_lock:
        return any(
            job.resource == resource and job.status == "running"
            for job in _jobs.values()
        )


def cleanup_old_jobs(max_age_seconds: int = 3600):
    """
    清理超过指定时间的已完成任务

    Args:
        max_age_seconds: 最大保留时间（秒）
    """
    now = datetime.now()
    with _jobs_lock:
        to_delete = []
        for job_id, job in _jobs.items():
            if job.status in ("completed", "failed", "stopped") and job.finished_at:
                age = (now - job.finished_at).total_seconds()
                if age > max_age_seconds:
                    to_delete.append(job_id)

        for job_id in to_delete:
            del _jobs[job_id]
