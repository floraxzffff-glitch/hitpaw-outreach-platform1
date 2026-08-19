#!/usr/bin/env python3
"""
YouTube视频搜索模块 - 使用YouTube Data API v3
包含配额管理、断点续跑、数据补全
"""

import time
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional
import os


class YouTubeSearcher:
    def __init__(self, api_key: str, quota_limit: int = 9500):
        self.api_key = api_key
        self.quota_limit = quota_limit
        self.quota_used = 0
        self.quota_file = "youtube_quota.json"
        self._load_quota()

    def _load_quota(self):
        """加载今日已用配额"""
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                    today = datetime.now().strftime("%Y-%m-%d")
                    if data.get("date") == today:
                        self.quota_used = data.get("used", 0)
                        print(f"  📊 今日已用配额: {self.quota_used}/{self.quota_limit}")
                    else:
                        # 新的一天，重置配额
                        self.quota_used = 0
                        self._save_quota()
            except Exception as e:
                print(f"  ⚠️  配额文件读取失败: {e}")

    def _save_quota(self):
        """保存配额使用情况"""
        try:
            with open(self.quota_file, 'w') as f:
                json.dump({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "used": self.quota_used
                }, f)
        except Exception as e:
            print(f"  ⚠️  配额文件保存失败: {e}")

    def check_quota_available(self, cost: int) -> bool:
        """检查配额是否充足"""
        return (self.quota_used + cost) <= self.quota_limit

    def search_videos(self, keyword: str, max_results: int = 25, order: str = "viewCount") -> List[Dict]:
        """
        搜索视频（消耗100 units）
        order: viewCount 或 relevance
        """
        cost = 100
        if not self.check_quota_available(cost):
            print(f"  ⚠️  配额不足！今日已用 {self.quota_used}，需要 {cost}，上限 {self.quota_limit}")
            return []

        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": order,
                "maxResults": min(max_results, 50),
                "key": self.api_key
            }

            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(full_url, headers={
                "User-Agent": "Mozilla/5.0"
            })

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # 消耗配额
            self.quota_used += cost
            self._save_quota()

            videos = []
            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})

                if video_id:
                    videos.append({
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "channel_id": snippet.get("channelId", ""),
                        "channel_title": snippet.get("channelTitle", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "video_url": f"https://www.youtube.com/watch?v={video_id}",
                        "channel_url": f"https://www.youtube.com/channel/{snippet.get('channelId', '')}"
                    })

            return videos

        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")
            return []

    def enrich_videos(self, video_ids: List[str]) -> Dict[str, Dict]:
        """
        补全视频统计数据（每次消耗1 unit，批量最多50个）
        返回: {video_id: {viewCount, publishedAt, channelId, channelTitle}}
        """
        if not video_ids:
            return {}

        cost = 1
        if not self.check_quota_available(cost):
            print(f"  ⚠️  配额不足，跳过数据补全")
            return {}

        try:
            # 批量查询，最多50个
            batch_ids = video_ids[:50]
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,statistics",
                "id": ",".join(batch_ids),
                "key": self.api_key
            }

            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(full_url, headers={
                "User-Agent": "Mozilla/5.0"
            })

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # 消耗配额
            self.quota_used += cost
            self._save_quota()

            result = {}
            for item in data.get("items", []):
                video_id = item.get("id")
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})

                result[video_id] = {
                    "view_count": int(stats.get("viewCount", 0)),
                    "published_at": snippet.get("publishedAt", ""),
                    "channel_id": snippet.get("channelId", ""),
                    "channel_title": snippet.get("channelTitle", "")
                }

            return result

        except Exception as e:
            print(f"  ❌ 数据补全失败: {e}")
            return {}

    def get_remaining_quota(self) -> int:
        """获取剩余配额"""
        return max(0, self.quota_limit - self.quota_used)

    def estimate_search_quota(self, num_keywords: int) -> int:
        """预估搜索需要的配额"""
        return num_keywords * 100 + num_keywords  # search(100) + enrich(1)


class QuotaManager:
    """配额管理和断点续跑"""

    def __init__(self, checkpoint_file: str = "search_checkpoint.json"):
        self.checkpoint_file = checkpoint_file

    def save_checkpoint(self, processed_keywords: List[str], remaining_keywords: List[str]):
        """保存断点"""
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    "date": datetime.now().isoformat(),
                    "processed": processed_keywords,
                    "remaining": remaining_keywords
                }, f, ensure_ascii=False, indent=2)
            print(f"\n💾 断点已保存: {len(processed_keywords)} 个已完成，{len(remaining_keywords)} 个待处理")
        except Exception as e:
            print(f"  ⚠️  断点保存失败: {e}")

    def load_checkpoint(self) -> Optional[Dict]:
        """加载断点"""
        if not os.path.exists(self.checkpoint_file):
            return None

        try:
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                print(f"\n📂 发现断点: {len(data.get('processed', []))} 个已完成，{len(data.get('remaining', []))} 个待处理")
                return data
        except Exception as e:
            print(f"  ⚠️  断点加载失败: {e}")
            return None

    def clear_checkpoint(self):
        """清除断点"""
        if os.path.exists(self.checkpoint_file):
            try:
                os.remove(self.checkpoint_file)
                print("  ✓ 断点已清除")
            except Exception as e:
                print(f"  ⚠️  断点清除失败: {e}")


def search_with_both_orders(searcher: YouTubeSearcher, keyword: str, max_results: int = 25) -> List[Dict]:
    """
    用两种排序方式搜索，合并结果去重
    - viewCount: 按播放量排序
    - relevance: 按相关性排序
    """
    print(f"\n  🔍 搜索: {keyword}")

    videos = []
    seen_ids = set()

    # 方式1: 按播放量
    print(f"    → 按播放量排序...")
    view_results = searcher.search_videos(keyword, max_results=max_results//2, order="viewCount")
    for video in view_results:
        if video["video_id"] not in seen_ids:
            seen_ids.add(video["video_id"])
            videos.append(video)

    # 方式2: 按相关性
    print(f"    → 按相关性排序...")
    rel_results = searcher.search_videos(keyword, max_results=max_results//2, order="relevance")
    for video in rel_results:
        if video["video_id"] not in seen_ids:
            seen_ids.add(video["video_id"])
            videos.append(video)

    print(f"    ✓ 找到 {len(videos)} 个独特视频")

    # 补全统计数据
    if videos:
        print(f"    → 补全统计数据...")
        video_ids = [v["video_id"] for v in videos]
        enriched = searcher.enrich_videos(video_ids)

        for video in videos:
            vid = video["video_id"]
            if vid in enriched:
                video.update(enriched[vid])

    return videos
