"""
把网页 API 接到 VikPea 原始工作台的真实脚本/数据上。

原则：
- 不修改原工作台脚本（同事仍在用桌面版），只 import 其中的纯函数/常量。
- 所有读操作直接读原工作台目录下的真实 xlsx 文件，不复制、不建镜像数据。
- 重活（深度找邮箱批量跑、SEO 实时扫描）不在这里做同步调用，留给后续的后台任务方案。
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

WORKSPACE_DIR = os.environ.get(
    "VIKPEA_WORKSPACE_DIR",
    "/Users/xuzifu/Downloads/VikPea工作台/VikPea工作台_Mac试用包_2026-08-12/01_请在这个文件夹里操作",
)

if not os.path.isdir(WORKSPACE_DIR):
    raise RuntimeError(f"找不到 VikPea 工作台目录: {WORKSPACE_DIR}")

if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

import openpyxl  # noqa: E402

import VikPea_common as vikpea_common  # noqa: E402
from VikPea_关键词聚类 import (  # noqa: E402
    load_keywords as _load_article_keywords,
    cluster_keywords as _cluster_keywords,
    ARTICLE_KEYWORD_PATH,
)
import VikPea_关键词复盘 as keyword_review  # noqa: E402

SEO_SCAN_OUTPUT = os.path.join(WORKSPACE_DIR, "VikPea_SEO渠道机会扫描.xlsx")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _workbook_rows(path: str, sheet: Optional[str] = None) -> List[Dict[str, Any]]:
    """按第一行表头把 xlsx 读成 list[dict]，文件不存在时返回空列表。"""
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


def _parse_date_to_iso(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        return datetime.now().isoformat()
    try:
        return datetime.strptime(text, "%Y-%m-%d").isoformat()
    except ValueError:
        return datetime.now().isoformat()


# ======================== 关键词分析（历史搜索/发信复盘数据） ========================

def get_keyword_review_data() -> Dict[str, dict]:
    data = keyword_review.load_search_metrics()
    data = keyword_review.load_tracker_metrics(data)
    return data


def lookup_keyword(keyword: str) -> Dict[str, Any]:
    keyword = keyword.strip()
    data = get_keyword_review_data()
    item = data.get(keyword)
    if not item:
        return {
            "found": False,
            "total_found": 0,
            "eligible_count": 0,
            "email_found_count": 0,
            "email_rate": 0.0,
            "details": {"说明": "该关键词在历史搜索/发信记录里还没有数据（不是实时抓取，只复盘已跑过的关键词）"},
        }
    added = item.get("new_email", 0) + item.get("new_no_email", 0)
    return {
        "found": True,
        "total_found": item.get("found_channels", 0),
        "eligible_count": item.get("eligible_channels", 0),
        "email_found_count": item.get("new_email", 0),
        "email_rate": keyword_review.pct(item.get("new_email", 0), added),
        "details": {
            "搜索次数": item.get("search_runs", 0),
            "已发送": item.get("sent", 0),
            "已回复": item.get("replied", 0),
            "A级": item.get("grade_a", 0),
            "B级": item.get("grade_b", 0),
            "C级": item.get("grade_c", 0),
            "建议动作": keyword_review.suggest(item),
            "最近搜索日期": item.get("last_search_date", ""),
        },
    }


def list_keyword_reviews() -> List[Dict[str, Any]]:
    data = get_keyword_review_data()
    rows = []
    for keyword, item in data.items():
        added = item.get("new_email", 0) + item.get("new_no_email", 0)
        rows.append({
            "keyword": keyword,
            "search_runs": item.get("search_runs", 0),
            "found_channels": item.get("found_channels", 0),
            "eligible_channels": item.get("eligible_channels", 0),
            "new_email": item.get("new_email", 0),
            "email_rate": keyword_review.pct(item.get("new_email", 0), added),
            "sent": item.get("sent", 0),
            "replied": item.get("replied", 0),
            "reply_rate": keyword_review.pct(item.get("replied", 0), item.get("sent", 0)),
            "grade_a": item.get("grade_a", 0),
            "suggestion": keyword_review.suggest(item),
            "last_search_date": item.get("last_search_date", ""),
        })
    rows.sort(key=lambda r: (-r["grade_a"], -r["sent"], -r["new_email"], r["keyword"]))
    return rows


def cluster_article_keywords() -> List[Dict[str, Any]]:
    rows = _load_article_keywords(ARTICLE_KEYWORD_PATH)
    clusters = []
    for theme, representative, count, top_tokens, items in _cluster_keywords(rows):
        clusters.append({
            "theme": theme,
            "representative": representative,
            "count": count,
            "top_tokens": top_tokens,
            "keywords": [item[0] for item in items],
        })
    return clusters


# ======================== 邮箱验证 ========================

def validate_email_address(email: str, check_blacklist: bool = True) -> Dict[str, Any]:
    format_reason = vikpea_common.classify_bad_email(email)
    is_blacklisted = False
    blacklist_reason_text = ""
    if check_blacklist and not format_reason:
        blacklist_reason_text = vikpea_common.blacklist_reason("", email, "")
        is_blacklisted = bool(blacklist_reason_text)

    reason = format_reason or blacklist_reason_text or None
    is_valid = not format_reason
    confidence_score = 1.0 if (is_valid and not is_blacklisted) else (0.5 if is_blacklisted else 0.0)

    return {
        "email": email,
        "is_valid": is_valid,
        "is_blacklisted": is_blacklisted,
        "confidence_score": confidence_score,
        "reason": reason,
    }


# ======================== SEO 机会（读取上一次扫描结果） ========================

def get_seo_opportunities(keyword: Optional[str] = None, min_score: float = 0) -> List[Dict[str, Any]]:
    rows = _workbook_rows(SEO_SCAN_OUTPUT)
    results = []
    for row in rows:
        url = str(row.get("URL") or "").strip()
        title = str(row.get("标题") or "").strip()
        if not url and not title:
            continue  # 跳过占位/说明行（表头版本和脚本实际输出不一致时会出现）
        raw_score = row.get("站点分") or 0
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0
        if score < min_score:
            continue
        if keyword and keyword.strip().lower() not in str(row.get("关键词") or "").lower():
            continue
        results.append({
            "url": row.get("URL") or "",
            "title": row.get("标题") or "",
            "relevance_score": score,
            "level": row.get("机会等级") or "C",
            "opportunity_type": row.get("机会类型") or "",
            "action": row.get("建议动作") or "",
            "timestamp": _parse_date_to_iso(row.get("扫描日期")),
            "keyword": row.get("关键词") or "",
        })
    return results


def has_seo_scan_data() -> bool:
    return os.path.exists(SEO_SCAN_OUTPUT)


# ======================== 报告 / 仪表盘统计 ========================

def get_dashboard_stats() -> Dict[str, Any]:
    today = _today()

    keyword_data = get_keyword_review_data()
    total_keywords_analyzed = len(keyword_data)
    keywords_today = sum(
        1 for item in keyword_data.values() if str(item.get("last_search_date") or "") == today
    )

    tracker_rows = _workbook_rows(vikpea_common.TRACKER_PATH, "邮件追踪")
    total_emails_validated = len(tracker_rows)
    emails_today = sum(1 for row in tracker_rows if str(row.get("日期") or "").strip() == today)

    seo_rows = get_seo_opportunities()
    total_opportunities_found = len(seo_rows)
    opportunities_today = sum(
        1 for row in seo_rows if str(row.get("timestamp") or "").startswith(today)
    )

    return {
        "total_keywords_analyzed": total_keywords_analyzed,
        "total_emails_validated": total_emails_validated,
        "total_opportunities_found": total_opportunities_found,
        "today_activities": {
            "keywords_analyzed": keywords_today,
            "emails_validated": emails_today,
            "opportunities_found": opportunities_today,
        },
    }


def get_keyword_review_report() -> Dict[str, Any]:
    rows = list_keyword_reviews()
    return {
        "keyword_count": len(rows),
        "top_keywords": rows[:20],
    }


def get_seo_analysis_report() -> Dict[str, Any]:
    rows = get_seo_opportunities()
    level_counts = {"A": 0, "B": 0, "C": 0}
    for row in rows:
        level_counts[row["level"]] = level_counts.get(row["level"], 0) + 1
    return {
        "total_opportunities": len(rows),
        "level_counts": level_counts,
        "has_scan_data": has_seo_scan_data(),
        "top_opportunities": sorted(rows, key=lambda r: -r["relevance_score"])[:20],
    }


def get_email_validation_report() -> Dict[str, Any]:
    queue_rows = _workbook_rows(vikpea_common.QUEUE_PATH)
    emails = [str(row.get("邮箱") or "").strip() for row in queue_rows]
    emails = [e for e in emails if e]
    results = [validate_email_address(e) for e in emails]
    return {
        "total_checked": len(results),
        "valid": sum(1 for r in results if r["is_valid"] and not r["is_blacklisted"]),
        "blacklisted": sum(1 for r in results if r["is_blacklisted"]),
        "invalid": sum(1 for r in results if not r["is_valid"]),
        "source": "VikPea_发信名单.xlsx",
    }
