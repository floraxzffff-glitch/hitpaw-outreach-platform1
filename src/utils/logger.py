"""
日志记录工具
"""

import os
import logging
from datetime import datetime


def setup_logger(name, log_file=None, level=logging.INFO):
    """配置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_format = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_event(action, message, log_path=None):
    """记录事件到日志和控制台"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{ts}] {action}: {message}"
    print(log_msg)
    
    if log_path:
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except Exception:
            pass
