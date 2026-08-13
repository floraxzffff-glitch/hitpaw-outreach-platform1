"""
FastAPI 应用配置管理
支持环境变量和 .env 文件
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """应用设置"""
    
    # 基础设置
    app_name: str = "VikPea SEO API"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # 服务器设置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"
    
    # 前端设置
    frontend_url: str = "http://localhost:3000"
    
    # 数据库设置
    database_url: Optional[str] = None
    database_echo: bool = False  # 打印 SQL 日志
    
    # Redis 缓存
    redis_url: Optional[str] = "redis://localhost:6379/0"
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    
    # 邮箱配置（来自 VikPea 原配置）
    smtp_server: str = "smtp.qiye.aliyun.com"
    smtp_port: int = 465
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # IMAP 配置
    imap_server: str = "imap.qiye.aliyun.com"
    imap_port: int = 993
    
    # 搜索配置
    youtube_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    serpapi_key: Optional[str] = None
    
    # 文件上传配置
    upload_dir: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_extensions: list = [".xlsx", ".csv", ".xls", ".txt"]
    
    # 安全设置
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS 设置
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # 日志设置
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"
    
    # 后台任务配置
    enable_background_tasks: bool = True
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # 速率限制
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # 每个时间窗口的请求数
    rate_limit_period: int = 60  # 时间窗口（秒）
    
    # Sentry 错误追踪（可选）
    sentry_dsn: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用设置（单例模式）
    
    使用示例：
        from config import get_settings
        settings = get_settings()
        print(settings.api_port)
    """
    return Settings()


# 预设环境
SETTINGS_BY_ENV = {
    "development": {
        "debug": True,
        "cors_origins": ["*"],  # 允许所有来源
        "log_level": "DEBUG",
    },
    "staging": {
        "debug": False,
        "cors_origins": [
            "https://staging.example.com",
            "https://staging-admin.example.com",
        ],
        "log_level": "INFO",
    },
    "production": {
        "debug": False,
        "cors_origins": [
            "https://example.com",
            "https://app.example.com",
        ],
        "log_level": "WARNING",
    },
}
