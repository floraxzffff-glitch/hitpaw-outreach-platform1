"""
核心工具库 - 邮箱验证、黑名单、日志等
"""

import re
import os
from datetime import datetime

EMAIL_RE = re.compile(r"[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}")
URL_ENCODED_FRAGMENT_RE = re.compile(r"%(?:22|20|2b|40|2e|2d|5f|[0-9a-f]{2})", re.I)

BAD_DOMAIN_FRAGMENTS = {
    "random", "duckduckgo", "google", "youtube", "sentry", "schema", "cloudflare",
    "googleapis", "googleusercontent", "googlevideo", "gstatic", "ytimg",
    "hitpaw", "tenorshare", "topaz", "topazlabs", "vanceai", "avclabs",
    "wondershare", "aiarty", "patreon", "invideo", "openshot", "envato", "pxf.io",
}

BAD_TLDS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "avif", "css", "js", "json", "xml"}

LOW_VALUE_EMAILS = {
    "error-lite@duckduckgo.com", "support@wix.com", "abuse@cloudflare.com",
    "privacy@youtube.com", "support@linktr.ee",
}

PLACEHOLDER_LOCAL_PARTS = {
    "john.smith", "jane.smith", "test", "testing", "example", "demo",
}

PUBLIC_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
}


def normalize_email(email):
    """规范化邮箱地址"""
    return str(email or "").strip().lower()


def classify_bad_email(email):
    """判断邮箱是否为垃圾/假邮箱，返回理由或空字符串"""
    e = normalize_email(email)
    if not e:
        return "空邮箱"
    if e in LOW_VALUE_EMAILS:
        return "平台/错误邮箱"
    if e.count("@") != 1 or not EMAIL_RE.fullmatch(e):
        return "邮箱格式异常"
    
    local, domain = e.split("@", 1)
    parts = domain.split(".")
    tld = parts[-1] if parts else ""
    
    if len(local) < 2 or len(local) > 64 or len(domain) > 80:
        return "邮箱格式可疑"
    if any(ch in e for ch in {'"', "'", " "}) or URL_ENCODED_FRAGMENT_RE.search(e):
        return "URL编码碎片误判邮箱"
    if "%" in e or local.startswith("-") or local.startswith("."):
        return "邮箱格式可疑"
    if tld in BAD_TLDS or re.search(r"\d+x\.", domain) or "compressed" in domain:
        return "资源文件误判"
    if any(fragment in domain for fragment in BAD_DOMAIN_FRAGMENTS):
        return "平台/竞品域名邮箱"
    
    return ""


def log_event(action, message, log_path=None):
    """记录事件到日志文件"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{ts}] {action}: {message}"
    print(log_msg)
    
    if log_path:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except Exception:
            pass


def root_domain(value: str) -> str:
    """提取域名的主体部分（如 example.com from www.example.com）"""
    domain = str(value or "").strip().lower().replace("www.", "")
    if "@" in domain:
        domain = domain.split("@", 1)[1]
    parts = [part for part in domain.split(".") if part]
    if len(parts) <= 2:
        return domain
    
    special_suffixes = {
        "co.uk", "org.uk", "ac.uk", "com.au", "net.au", "org.au",
        "co.jp", "com.cn", "com.hk", "com.sg", "com.br", "co.in",
    }
    suffix = ".".join(parts[-2:])
    suffix3 = ".".join(parts[-3:])
    
    if suffix3 in special_suffixes and len(parts) >= 4:
        return ".".join(parts[-4:])
    if suffix in special_suffixes and len(parts) >= 3:
        return ".".join(parts[-3:])
    
    return ".".join(parts[-2:])
