#!/usr/bin/env python3
"""
筛选打分模块 - VPH计算和数据过滤
"""

from datetime import datetime
from typing import List, Dict, Optional


def parse_published_at(published_at: str) -> Optional[datetime]:
    """解析YouTube API返回的时间格式: 2024-08-15T10:30:00Z"""
    if not published_at:
        return None
    try:
        # 移除Z后缀，解析为datetime
        if published_at.endswith('Z'):
            published_at = published_at[:-1]
        return datetime.fromisoformat(published_at)
    except Exception:
        return None


def calculate_vph(view_count: int, published_at: str) -> float:
    """
    计算VPH (Views Per Hour)
    VPH = viewCount / ((now - publishedAt)小时数)
    """
    if not published_at or view_count <= 0:
        return 0.0

    pub_time = parse_published_at(published_at)
    if not pub_time:
        return 0.0

    now = datetime.utcnow()
    hours_passed = (now - pub_time).total_seconds() / 3600

    if hours_passed <= 0:
        return 0.0

    return view_count / hours_passed


def filter_videos(videos: List[Dict], vph_threshold: float = 20.0) -> List[Dict]:
    """
    过滤视频，只保留VPH >= threshold的
    会自动为每个视频添加vph字段
    """
    filtered = []

    for video in videos:
        view_count = video.get("view_count", 0)
        published_at = video.get("published_at", "")

        vph = calculate_vph(view_count, published_at)
        video["vph"] = round(vph, 2)

        if vph >= vph_threshold:
            filtered.append(video)

    return filtered


def score_and_rank(videos: List[Dict], keyword: str) -> List[Dict]:
    """
    对视频打分排序
    评分维度：
    1. VPH高低
    2. 标题相关性（包含关键词）
    3. 观看量绝对值
    """
    for video in videos:
        score = 0.0

        # VPH得分（占50%）
        vph = video.get("vph", 0)
        score += vph * 0.5

        # 标题相关性（占30%）
        title = video.get("title", "").lower()
        keyword_lower = keyword.lower()
        if keyword_lower in title:
            score += 30

        # 观看量绝对值得分（占20%，按万为单位）
        view_count = video.get("view_count", 0)
        score += (view_count / 10000) * 0.2

        video["score"] = round(score, 2)

    # 按score降序排序
    videos.sort(key=lambda x: x.get("score", 0), reverse=True)

    return videos


def deduplicate_by_channel(videos: List[Dict]) -> List[Dict]:
    """
    按频道去重，每个频道只保留得分最高的一个视频
    """
    channel_best = {}  # {channel_id: video}

    for video in videos:
        channel_id = video.get("channel_id")
        if not channel_id:
            continue

        if channel_id not in channel_best:
            channel_best[channel_id] = video
        else:
            # 保留得分更高的
            current_score = channel_best[channel_id].get("score", 0)
            new_score = video.get("score", 0)
            if new_score > current_score:
                channel_best[channel_id] = video

    return list(channel_best.values())


def format_video_for_output(video: Dict, keyword: str) -> Dict:
    """
    格式化视频数据用于输出
    """
    pub_time = parse_published_at(video.get("published_at", ""))
    pub_date_str = pub_time.strftime("%Y-%m-%d %H:%M") if pub_time else "Unknown"

    return {
        "关键词来源": keyword,
        "视频标题": video.get("title", ""),
        "视频链接": video.get("video_url", ""),
        "频道名": video.get("channel_title", ""),
        "频道链接": video.get("channel_url", ""),
        "观看数": video.get("view_count", 0),
        "发布时间": pub_date_str,
        "VPH": video.get("vph", 0),
        "得分": video.get("score", 0)
    }


def aggregate_by_channel(videos: List[Dict]) -> List[Dict]:
    """
    按频道汇总
    返回: [{"频道名", "频道链接", "命中视频数", "最高VPH", "平均VPH"}]
    """
    channel_stats = {}  # {channel_id: {videos: [], vphs: []}}

    for video in videos:
        channel_id = video.get("channel_id")
        if not channel_id:
            continue

        if channel_id not in channel_stats:
            channel_stats[channel_id] = {
                "channel_title": video.get("channel_title", ""),
                "channel_url": video.get("channel_url", ""),
                "videos": [],
                "vphs": []
            }

        channel_stats[channel_id]["videos"].append(video)
        vph = video.get("vph", 0)
        if vph > 0:
            channel_stats[channel_id]["vphs"].append(vph)

    # 汇总
    result = []
    for channel_id, data in channel_stats.items():
        vphs = data["vphs"]
        result.append({
            "频道名": data["channel_title"],
            "频道链接": data["channel_url"],
            "命中视频数": len(data["videos"]),
            "最高VPH": round(max(vphs), 2) if vphs else 0,
            "平均VPH": round(sum(vphs) / len(vphs), 2) if vphs else 0
        })

    # 按平均VPH降序
    result.sort(key=lambda x: x["平均VPH"], reverse=True)

    return result


def print_video_stats(videos: List[Dict]):
    """打印视频统计信息"""
    if not videos:
        print("  📊 无视频数据")
        return

    total = len(videos)
    vphs = [v.get("vph", 0) for v in videos]
    views = [v.get("view_count", 0) for v in videos]

    print(f"\n  📊 视频统计:")
    print(f"    总数: {total}")
    print(f"    VPH范围: {min(vphs):.1f} ~ {max(vphs):.1f}")
    print(f"    平均VPH: {sum(vphs)/len(vphs):.1f}")
    print(f"    观看数范围: {min(views):,} ~ {max(views):,}")
    print(f"    平均观看: {sum(views)//len(views):,}")
