"""
DataForSEO API 客户端 - 多渠道KOL发现工具

功能：
1. 关键词研究（DataForSEO Labs）- 找到高价值关键词
2. Google搜索博主网站（SERP API）- 发现KOL个人网站
3. YouTube视频搜索（SERP API）- 通过视频找到频道
"""

import base64
import httpx
from typing import Dict, List, Any, Optional


class DataForSEOClient:
    """DataForSEO API 客户端 - 用于关键词研究和KOL发现"""

    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.auth_header = self._make_auth_header()

    def _make_auth_header(self) -> str:
        """生成 Basic Auth 头"""
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def _request(self, endpoint: str, data: List[Dict] = None) -> Dict:
        """发送 API 请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            if data:
                response = await client.post(url, json=data, headers=headers)
            else:
                response = await client.get(url, headers=headers)

            response.raise_for_status()
            return response.json()

    # ==================== 1. 关键词研究功能 ====================

    async def keyword_research(
        self,
        seed_keyword: str,
        language_code: str = "en",
        location_code: int = 2840,  # 2840=美国, 2156=中国
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        关键词研究 - 找到相关的高价值关键词
        用这些关键词去YouTube API搜索频道

        Args:
            seed_keyword: 种子关键词，如 "tech review"
            language_code: 语言代码，如 "en", "zh-CN"
            location_code: 地区代码
            limit: 返回数量

        Returns:
            关键词列表，按搜索量排序
        """
        data = [{
            "keyword": seed_keyword,
            "language_code": language_code,
            "location_code": location_code,
            "limit": limit,
            "filters": [
                ["keyword_info.search_volume", ">", 100]  # 至少100搜索量
            ],
            "order_by": ["keyword_info.search_volume,desc"]
        }]

        try:
            result = await self._request("dataforseo_labs/google/keyword_suggestions/live", data)

            if result.get("tasks") and result["tasks"][0].get("result"):
                items = result["tasks"][0]["result"][0].get("items", [])
                return [
                    {
                        "keyword": item.get("keyword"),
                        "search_volume": item.get("keyword_info", {}).get("search_volume", 0),
                        "competition": item.get("keyword_info", {}).get("competition", 0),
                        "cpc": item.get("keyword_info", {}).get("cpc", 0),
                    }
                    for item in items
                ]
        except Exception as e:
            print(f"Keyword research error: {e}")
            return []

        return []

    async def get_related_keywords(
        self,
        keyword: str,
        language_code: str = "en",
        location_code: int = 2840,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取相关关键词 - 发现更多搜索词
        """
        data = [{
            "keyword": keyword,
            "language_code": language_code,
            "location_code": location_code,
            "limit": limit
        }]

        try:
            result = await self._request("dataforseo_labs/google/related_keywords/live", data)

            if result.get("tasks") and result["tasks"][0].get("result"):
                items = result["tasks"][0]["result"][0].get("items", [])
                return [
                    {
                        "keyword": item.get("keyword"),
                        "search_volume": item.get("keyword_data", {}).get("keyword_info", {}).get("search_volume", 0),
                        "relevance": item.get("relevance", 0),
                    }
                    for item in items
                ]
        except Exception as e:
            print(f"Related keywords error: {e}")
            return []

        return []

    # ==================== 2. Google搜索KOL网站 ====================

    async def search_influencer_websites(
        self,
        niche: str,
        language_code: str = "en",
        location_code: int = 2840,
        depth: int = 20
    ) -> List[Dict[str, Any]]:
        """
        在Google上搜索博主/KOL的网站
        搜索策略：niche + "youtube" OR "blog" OR "contact"

        Args:
            niche: 领域，如 "tech review", "gaming"
            depth: 搜索深度（返回前N个结果）

        Returns:
            网站列表，可能包含博主个人网站、YouTube频道等
        """
        # 优化搜索查询，增加找到KOL的概率
        search_query = f'{niche} (youtube OR blogger OR influencer OR "contact me")'

        data = [{
            "keyword": search_query,
            "language_code": language_code,
            "location_code": location_code,
            "device": "desktop",
            "os": "windows",
            "depth": depth
        }]

        try:
            result = await self._request("serp/google/organic/live/advanced", data)

            if result.get("tasks") and result["tasks"][0].get("result"):
                items = result["tasks"][0]["result"][0].get("items", [])

                websites = []
                for item in items:
                    if item.get("type") in ["organic", "video"]:
                        url = item.get("url", "")
                        # 提取YouTube频道ID（如果是YouTube链接）
                        youtube_channel_id = None
                        if "youtube.com/channel/" in url:
                            youtube_channel_id = url.split("/channel/")[1].split("/")[0].split("?")[0]
                        elif "youtube.com/@" in url:
                            youtube_channel_id = url.split("/@")[1].split("/")[0].split("?")[0]

                        websites.append({
                            "title": item.get("title"),
                            "url": url,
                            "domain": item.get("domain"),
                            "description": item.get("description", ""),
                            "type": item.get("type"),
                            "youtube_channel_id": youtube_channel_id,  # 如果是YouTube链接
                        })

                return websites
        except Exception as e:
            print(f"Google search error: {e}")
            return []

        return []

    # ==================== 3. YouTube视频搜索（通过视频找频道）====================

    async def search_youtube_videos(
        self,
        keyword: str,
        language_code: str = "en",
        location_code: int = 2840,
        depth: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索YouTube视频，从视频中提取频道信息
        这是一个间接方法：视频 → 频道ID → 用YouTube API获取频道详情

        Returns:
            频道列表（去重），包含channel_id可以传给YouTube API
        """
        data = [{
            "keyword": keyword,
            "language_code": language_code,
            "location_code": location_code,
            "depth": depth
        }]

        try:
            result = await self._request("serp/youtube/organic/live/advanced", data)

            if result.get("tasks") and result["tasks"][0].get("result"):
                items = result["tasks"][0]["result"][0].get("items", [])

                # 提取唯一的频道（一个频道可能有多个视频在结果中）
                channels_map = {}
                for item in items:
                    if item.get("type") == "youtube_video":
                        channel_info = item.get("channel", {})
                        channel_id = channel_info.get("id")

                        if channel_id and channel_id not in channels_map:
                            channels_map[channel_id] = {
                                "channel_id": channel_id,
                                "channel_name": channel_info.get("name"),
                                "channel_url": f"https://www.youtube.com/channel/{channel_id}",
                                "example_video_title": item.get("title"),
                                "example_video_url": item.get("url"),
                                "example_video_views": item.get("video_info", {}).get("views", 0),
                            }

                return list(channels_map.values())
        except Exception as e:
            print(f"YouTube video search error: {e}")
            return []

        return []


async def test_dataforseo_connection(login: str, password: str) -> Dict[str, Any]:
    """测试 DataForSEO API 连接和余额"""
    client = DataForSEOClient(login, password)

    try:
        result = await client._request("appendix/user_data")

        if result.get("tasks"):
            user_data = result["tasks"][0].get("result", [{}])[0]

            return {
                "success": True,
                "balance": user_data.get("money", {}).get("balance", 0),
                "currency": user_data.get("money", {}).get("currency", "USD"),
                "limits": user_data.get("limits", {}),
                "message": "连接成功"
            }

        return {"success": False, "message": "无法获取账户信息"}

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"success": False, "message": "认证失败：用户名或密码错误"}
        return {"success": False, "message": f"HTTP 错误：{e.response.status_code}"}

    except Exception as e:
        return {"success": False, "message": f"连接失败：{str(e)}"}
