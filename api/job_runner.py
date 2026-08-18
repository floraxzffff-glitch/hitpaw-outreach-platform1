"""
跑原工作台里那些"重活"脚本（网络抓取、耗时几分钟到几十分钟）的后台任务壳子。

设计取舍：
- 不重写这些脚本的业务逻辑（风险太高，容易跟桌面版行为不一致）。
- 两种任务方式：
  1. start_subprocess_job：真正开一个子进程跑脚本（`python3 脚本.py`），跟桌面工作台
     用 subprocess 拉起脚本是同一种方式。能真正"停止"（杀进程），页面刷新/离开也能
     通过任务列表找回来，因为任务状态在服务端进程里，不依赖前端页面。
  2. start_job：在后台线程里直接调用一个 Python 函数（用于 email_send 这种需要复用
     内存里已经算好的 session 对象、不方便拆成独立脚本进程的场景）。这种任务不支持停止。
- 每种资源（youtube_search / article_search / deep_email / email_send）同一时间只允许
  跑一个任务，避免和桌面工作台或另一个网页任务同时写同一张 xlsx。
"""

import subprocess
import sys
import threading
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence

JOBS: Dict[str, Dict[str, Any]] = {}
_RESOURCE_LOCKS: Dict[str, threading.Lock] = {}
_LOG_LIMIT = 800


def _lock_for(resource: str) -> threading.Lock:
    if resource not in _RESOURCE_LOCKS:
        _RESOURCE_LOCKS[resource] = threading.Lock()
    return _RESOURCE_LOCKS[resource]


def _new_job_record(resource: str, label: str, stoppable: bool) -> Dict[str, Any]:
    return {
        "job_id": "",
        "resource": resource,
        "label": label,
        "status": "running",
        "log": [],
        "error": None,
        "started_at": datetime.now().isoformat(),
        "finished_at": None,
        "stoppable": stoppable,
    }


def _append_log(job_id: str, text: str) -> None:
    line = text.rstrip("\n")
    if not line.strip():
        return
    log = JOBS[job_id]["log"]
    log.append(line)
    if len(log) > _LOG_LIMIT:
        del log[: len(log) - _LOG_LIMIT]


def _public(job: Dict[str, Any]) -> Dict[str, Any]:
    """去掉内部字段（比如子进程对象），这样才能安全地序列化成 JSON 返回给前端。"""
    return {k: v for k, v in job.items() if not k.startswith("_")}


class _JobStdout:
    """把 print() 输出既转发到真实终端，又按行收进任务日志（给 start_job 用）。"""

    def __init__(self, job_id: str, real_stdout):
        self.job_id = job_id
        self._real = real_stdout
        self._buffer = ""

    def write(self, text: str):
        self._real.write(text)
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            _append_log(self.job_id, line)

    def flush(self):
        self._real.flush()


def is_resource_busy(resource: str) -> bool:
    return _lock_for(resource).locked()


def start_job(resource: str, fn: Callable[[], None], label: str = "") -> str:
    """在后台线程里跑一个 Python 函数。不支持停止（用于 email_send 这类内存态任务）。"""
    lock = _lock_for(resource)
    if lock.locked():
        raise RuntimeError(f"{resource} 已经有任务在跑，等它跑完再试")

    job_id = f"{resource}_{uuid.uuid4().hex[:8]}"
    record = _new_job_record(resource, label, stoppable=False)
    record["job_id"] = job_id
    JOBS[job_id] = record

    def runner():
        if not lock.acquire(blocking=False):
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = "资源被占用"
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            return

        old_stdout = sys.stdout
        sys.stdout = _JobStdout(job_id, old_stdout)
        try:
            fn()
            JOBS[job_id]["status"] = "completed"
        except SystemExit as exc:
            code = exc.code
            if code in (0, None):
                JOBS[job_id]["status"] = "completed"
            else:
                JOBS[job_id]["status"] = "failed"
                JOBS[job_id]["error"] = f"脚本以退出码 {code} 结束，看日志找原因"
        except Exception as exc:  # noqa: BLE001 - 后台任务需要兜住所有异常，转成任务状态
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = str(exc)
        finally:
            sys.stdout = old_stdout
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            lock.release()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return job_id


def start_subprocess_job(resource: str, cmd: Sequence[str], cwd: Optional[str] = None, label: str = "") -> str:
    """
    开一个真正的子进程跑脚本（python3 脚本.py），逐行读它的输出当日志。
    支持 stop_job() 真正杀掉；任务状态存在服务端，前端刷新/离开页面不会丢。
    """
    lock = _lock_for(resource)
    if lock.locked():
        raise RuntimeError(f"{resource} 已经有任务在跑，等它跑完再试")

    job_id = f"{resource}_{uuid.uuid4().hex[:8]}"
    record = _new_job_record(resource, label, stoppable=True)
    record["job_id"] = job_id
    JOBS[job_id] = record

    def runner():
        if not lock.acquire(blocking=False):
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = "资源被占用"
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            return
        try:
            process = subprocess.Popen(
                list(cmd),
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            JOBS[job_id]["_process"] = process
            for line in process.stdout:  # type: ignore[union-attr]
                _append_log(job_id, line)
            process.wait()

            if JOBS[job_id]["status"] == "stopping":
                JOBS[job_id]["status"] = "stopped"
            elif process.returncode == 0:
                JOBS[job_id]["status"] = "completed"
            else:
                JOBS[job_id]["status"] = "failed"
                JOBS[job_id]["error"] = f"进程退出码 {process.returncode}，看日志找原因"
        except Exception as exc:  # noqa: BLE001
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = str(exc)
        finally:
            JOBS[job_id].pop("_process", None)
            JOBS[job_id]["finished_at"] = datetime.now().isoformat()
            lock.release()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return job_id


def stop_job(job_id: str) -> bool:
    """尝试停止一个正在跑的子进程任务。返回是否成功发出停止信号。"""
    job = JOBS.get(job_id)
    if not job or job["status"] != "running":
        return False
    process = job.get("_process")
    if not process:
        return False  # 内存态任务（start_job）不支持停止
    job["status"] = "stopping"
    process.terminate()

    def force_kill_if_stuck():
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    threading.Thread(target=force_kill_if_stuck, daemon=True).start()
    return True


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    job = JOBS.get(job_id)
    return _public(job) if job else None


def list_jobs(resource: Optional[str] = None) -> List[Dict[str, Any]]:
    jobs = list(JOBS.values())
    if resource:
        jobs = [j for j in jobs if j["resource"] == resource]
    jobs = sorted(jobs, key=lambda j: j["started_at"], reverse=True)
    return [_public(j) for j in jobs]
