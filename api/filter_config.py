"""
KOL 过滤配置管理
支持视频负关键词、竞品站点、竞品邮箱后缀、Affiliate名单等过滤规则
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
import openpyxl

WORKSPACE_DIR = os.environ.get(
    "VIKPEA_WORKSPACE_DIR",
    "/Users/xuzifu/Downloads/VikPea工作台/VikPea工作台_Mac试用包_2026-08-12/01_请在这个文件夹里操作",
)

# 过滤配置文件路径
NEGATIVE_KEYWORDS_PATH = os.path.join(WORKSPACE_DIR, "VikPea_视频负关键词.xlsx")
COMPETITOR_SITES_PATH = os.path.join(WORKSPACE_DIR, "VikPea_竞品站点黑名单.xlsx")
COMPETITOR_EMAILS_PATH = os.path.join(WORKSPACE_DIR, "VikPea_竞品邮箱后缀.xlsx")
AFFILIATE_BLACKLIST_PATH = os.path.join(WORKSPACE_DIR, "VikPea_Affiliate黑名单.xlsx")
LONGTERM_PARTNERS_PATH = os.path.join(WORKSPACE_DIR, "VikPea_长期合作名单.xlsx")


def _load_excel_column(path: str, column_name: str, sheet: Optional[str] = None) -> List[str]:
    """从Excel文件加载指定列的所有值"""
    if not os.path.exists(path):
        return []

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet and sheet in wb.sheetnames else wb.active

    if ws.max_row < 1:
        return []

    # 找到列索引
    headers = [str(cell.value or "").strip() for cell in ws[1]]
    if column_name not in headers:
        return []

    col_idx = headers.index(column_name)
    values = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if col_idx < len(row) and row[col_idx]:
            val = str(row[col_idx]).strip()
            if val:
                values.append(val)

    return values


def _load_excel_rows(path: str, sheet: Optional[str] = None) -> List[Dict[str, Any]]:
    """加载Excel所有行为字典列表"""
    if not os.path.exists(path):
        return []

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet and sheet in wb.sheetnames else wb.active

    if ws.max_row < 1:
        return []

    headers = [str(cell.value or "").strip() for cell in ws[1]]
    rows = []

    for values in ws.iter_rows(min_row=2, values_only=True):
        row = dict(zip(headers, values))
        if any(v not in (None, "") for v in row.values()):
            rows.append(row)

    return rows


class FilterConfig:
    """过滤配置加载器"""

    def __init__(self):
        self.reload()

    def reload(self):
        """重新加载所有过滤配置"""
        self._load_negative_keywords()
        self._load_competitor_sites()
        self._load_competitor_email_suffixes()
        self._load_blacklists()

    def _load_negative_keywords(self):
        """加载视频负关键词配置
        Excel格式：关键词 | 合作时间阈值(天)
        """
        self.negative_keywords = {}
        rows = _load_excel_rows(NEGATIVE_KEYWORDS_PATH)

        for row in rows:
            keyword = str(row.get("关键词", "")).strip().lower()
            threshold_days = row.get("合作时间阈值(天)", 90)

            if keyword:
                try:
                    self.negative_keywords[keyword] = int(threshold_days)
                except (ValueError, TypeError):
                    self.negative_keywords[keyword] = 90  # 默认90天

    def _load_competitor_sites(self):
        """加载竞品站点黑名单
        Excel格式：站点域名
        """
        self.competitor_sites = set()
        sites = _load_excel_column(COMPETITOR_SITES_PATH, "站点域名")
        self.competitor_sites = {s.lower() for s in sites if s}

    def _load_competitor_email_suffixes(self):
        """加载竞品邮箱后缀
        Excel格式：邮箱后缀
        """
        self.competitor_email_suffixes = set()
        suffixes = _load_excel_column(COMPETITOR_EMAILS_PATH, "邮箱后缀")
        self.competitor_email_suffixes = {s.lower() for s in suffixes if s}

    def _load_blacklists(self):
        """加载Affiliate黑名单和长期合作名单
        Excel格式：频道名 | 邮箱 | 备注
        """
        self.affiliate_blacklist = set()
        self.longterm_partners = set()

        # 加载Affiliate黑名单
        rows = _load_excel_rows(AFFILIATE_BLACKLIST_PATH)
        for row in rows:
            channel = str(row.get("频道名", "")).strip()
            email = str(row.get("邮箱", "")).strip().lower()
            if channel:
                self.affiliate_blacklist.add(channel)
            if email:
                self.affiliate_blacklist.add(email)

        # 加载长期合作名单
        rows = _load_excel_rows(LONGTERM_PARTNERS_PATH)
        for row in rows:
            channel = str(row.get("频道名", "")).strip()
            email = str(row.get("邮箱", "")).strip().lower()
            if channel:
                self.longterm_partners.add(channel)
            if email:
                self.longterm_partners.add(email)

    def check_negative_keywords(
        self,
        title: str,
        description: str,
        last_collab_date: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """检查视频标题和简介中的负关键词

        Args:
            title: 视频标题
            description: 视频简介
            last_collab_date: 最后合作日期 (YYYY-MM-DD格式)

        Returns:
            (should_exclude, matched_keyword, days_since_collab)
            - should_exclude: 是否应该排除
            - matched_keyword: 匹配到的关键词
            - days_since_collab: 距离上次合作的天数
        """
        text = (title + " " + description).lower()

        for keyword, threshold_days in self.negative_keywords.items():
            if keyword in text:
                # 匹配到负关键词
                if not last_collab_date:
                    # 没有合作日期，直接排除
                    return (True, keyword, None)

                try:
                    collab_date = datetime.strptime(last_collab_date, "%Y-%m-%d")
                    days_diff = (datetime.now() - collab_date).days

                    if days_diff < threshold_days:
                        # 合作时间小于阈值，排除
                        return (True, keyword, days_diff)
                    else:
                        # 合作时间大于阈值，不排除但需标注
                        return (False, keyword, days_diff)
                except (ValueError, TypeError):
                    # 日期格式错误，直接排除
                    return (True, keyword, None)

        return (False, None, None)

    def check_competitor_site(self, video_url: str, channel_url: str) -> Tuple[bool, Optional[str]]:
        """检查是否推广竞品站点

        Args:
            video_url: 视频链接
            channel_url: 频道主页链接

        Returns:
            (is_competitor, matched_site)
        """
        text = (video_url + " " + channel_url).lower()

        for site in self.competitor_sites:
            if site in text:
                return (True, site)

        return (False, None)

    def check_competitor_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """检查是否为竞品邮箱

        Args:
            email: 邮箱地址

        Returns:
            (is_competitor, matched_suffix)
        """
        if not email:
            return (False, None)

        email_lower = email.lower()

        for suffix in self.competitor_email_suffixes:
            if email_lower.endswith(suffix):
                return (True, suffix)

        return (False, None)

    def check_blacklist(self, channel_name: str, email: str) -> Tuple[bool, str]:
        """检查是否在黑名单中

        Args:
            channel_name: 频道名
            email: 邮箱地址

        Returns:
            (is_blacklisted, reason)
            reason: "affiliate" 或 "longterm"
        """
        email_lower = email.lower() if email else ""

        if channel_name in self.affiliate_blacklist or email_lower in self.affiliate_blacklist:
            return (True, "affiliate")

        if channel_name in self.longterm_partners or email_lower in self.longterm_partners:
            return (True, "longterm")

        return (False, "")


# 全局配置实例
_filter_config: Optional[FilterConfig] = None


def get_filter_config() -> FilterConfig:
    """获取全局过滤配置实例"""
    global _filter_config
    if _filter_config is None:
        _filter_config = FilterConfig()
    return _filter_config


def reload_filter_config():
    """重新加载过滤配置"""
    global _filter_config
    _filter_config = FilterConfig()
