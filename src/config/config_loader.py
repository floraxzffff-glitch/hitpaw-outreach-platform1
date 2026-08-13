"""
配置加载器 - 从 Excel/环境变量/默认值读取配置
"""

import os
from datetime import datetime

try:
    import openpyxl
except ImportError:
    openpyxl = None


DEFAULT_CONFIG = {
    "SMTP_SERVER": "smtp.qiye.aliyun.com",
    "SMTP_PORT": 465,
    "SMTP_TIMEOUT": 25,
    "SMTP_ALLOW_INSECURE_SSL": True,
    "IMAP_SERVER": "imap.qiye.aliyun.com",
    "IMAP_PORT": 993,
    "FROM_EMAIL": "hannah@hitpaw.com",
    "FROM_NAME": "Hannah",
    "PASSWORD": "",
    "PRODUCT_NAME": "HitPaw VikPea",
    "PRODUCT_TEAM": "HitPaw Team",
    "PRODUCT_URL": "https://www.hitpaw.com/hitpaw-video-enhancer.html",
    "OUTREACH_SUBJECT_YOUTUBE": "Possible collaboration with {product_name}",
    "OUTREACH_SUBJECT_ARTICLE": "Possible collaboration with {product_name}",
    "OUTREACH_TEMPLATE_YOUTUBE": "{opening}\n\nI'm {from_name} from {product_name}.\n\nWe'd love to explore a collaboration with you. If it feels like a fit, we're open to either:\n1. adding {product_name} as a relevant tool or link mention in your existing content, or\n2. collaborating on a dedicated review or tutorial.\n\nIf you're open to this, please feel free to share your rate card or usual collaboration pricing.\n\nBest,\n{from_name}\n{product_team}\n{product_url}",
    "OUTREACH_TEMPLATE_ARTICLE": "{opening}\n\nI'm {from_name} from {product_name}.\n\nWe'd love to explore a collaboration with you. If it feels like a fit, we're open to either:\n1. adding {product_name} as a relevant tool or link mention in an existing article, or\n2. collaborating on a dedicated review or tutorial.\n\nIf you're open to this, please feel free to share your rate card or usual collaboration pricing.\n\nBest,\n{from_name}\n{product_team}\n{product_url}",
    "DELAY_SEC": 8,
    "DAILY_SEND_LIMIT": 80,
    "FOLLOWUP_DAILY_LIMIT": 50,
    "FOLLOWUP1_AFTER_DAYS": 5,
    "FOLLOWUP2_AFTER_DAYS": 7,
    "DEEP_EMAIL_MAX_ROWS": 80,
    "ARTICLE_RESULTS_PER_QUERY": 30,
    "ARTICLE_MIN_SITE_SCORE": 3,
    "RESPECT_ROBOTS_TXT": True,
    "CRAWL_DELAY_PER_DOMAIN": 1.5,
    "SEO_OPPORTUNITY_RESULTS_PER_KEYWORD": 30,
    "SEO_OPPORTUNITY_MIN_SCORE": 3,
    "SERP_PROVIDER": "",
    "SERPER_API_KEY": "",
    "SERPAPI_KEY": "",
    "DATAFORSEO_LOGIN": "",
    "DATAFORSEO_PASSWORD": "",
    "YOUTUBE_RESULTS_PER_KEYWORD": 35,
    "YOUTUBE_MIN_VIDEO_VIEWS": 800,
    "YOUTUBE_MIN_SHORTS_VIEWS": 2500,
    "YOUTUBE_MIN_RECENT_AVG_VIEWS": 1000,
    "YOUTUBE_RECENT_VIDEO_COUNT": 5,
    "YOUTUBE_ACTIVE_WITHIN_DAYS": 30,
    "YOUTUBE_VIDEO_METRICS_TIMEOUT": 15,
    "YOUTUBE_RECENT_CHANNEL_TIMEOUT": 20,
    "YOUTUBE_API_KEY": "",
    "YOUTUBE_API_DELAY_SEC": 0.5,
    "YOUTUBE_API_RETRY_TIMES": 3,
    "YOUTUBE_API_429_COOLDOWN": 10,
    "YTDLP_COOKIES_FROM_BROWSER": "",
    "YTDLP_RETRY_TIMES": 2,
    "USE_SEMRUSH_FOR_YOUTUBE": False,
    "YOUTUBE_KEYWORD_FILTER": True,
    "REQUIRE_SEND_CODE": "SEND",
    "PERSONALIZE_RECENT_VIDEOS": True,
}


def coerce_value(value):
    """将字符串/布尔值转换为适当的 Python 类型"""
    if isinstance(value, str):
        text = value.strip()
        if text.lower() in {"true", "yes", "y", "是"}:
            return True
        if text.lower() in {"false", "no", "n", "否"}:
            return False
        if text.isdigit():
            return int(text)
    return value


def build_default_config(profile=""):
    """构建默认配置（支持不同的profile: VKP/FP等）"""
    config = dict(DEFAULT_CONFIG)
    profile = str(profile or "").strip().lower()
    
    if profile == "vkp":
        config["PRODUCT_NAME"] = "HitPaw VikPea"
        config["PRODUCT_URL"] = "https://www.hitpaw.com/hitpaw-video-enhancer.html"
    elif profile == "fp":
        config["PRODUCT_NAME"] = "FotorPea"
        config["PRODUCT_URL"] = "https://www.hitpaw.com/fotorpea-photo-enhancer.html"
    
    return config


def load_config(config_path=None, profile=""):
    """从 Excel 配置文件加载配置"""
    config = build_default_config(profile)
    
    if not config_path or not openpyxl:
        return config
    
    if not os.path.exists(config_path):
        return config
    
    try:
        wb = openpyxl.load_workbook(config_path, data_only=True)
        ws = wb.active
        for row in ws.iter_rows(min_row=2, values_only=True):
            key = str((row[0] if row else "") or "").strip()
            if not key:
                continue
            value = row[1] if len(row) > 1 else None
            if value is not None and str(value).strip() != "":
                config[key] = coerce_value(value)
    except Exception as exc:
        print(f"⚠️  读取配置文件失败，使用默认值: {exc}")
    
    return config


def apply_config(globals_dict, mapping, config_path=None, profile=""):
    """将配置应用到全局变量字典"""
    config = load_config(config_path=config_path, profile=profile)
    for config_key, global_name in mapping.items():
        value = config.get(config_key)
        if value is not None and value != "":
            globals_dict[global_name] = value
    return config
