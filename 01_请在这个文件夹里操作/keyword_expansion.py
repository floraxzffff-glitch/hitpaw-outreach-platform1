#!/usr/bin/env python3
"""
关键词拓展模块 - 三个来源并行拓展
1. YouTube自动补全
2. DataForSEO related_keywords
3. DataForSEO keyword_ideas
"""

import time
import json
import urllib.request
import urllib.parse
import base64
from typing import List, Set, Dict


class KeywordExpander:
    def __init__(self, dataforseo_login: str = "", dataforseo_password: str = ""):
        self.dataforseo_login = dataforseo_login
        self.dataforseo_password = dataforseo_password
        self.blacklist = set()  # 关键词黑名单，后续可手动维护

    def expand_all(self, seed_keyword: str, max_keywords: int = 50, depth: int = 1) -> Dict[str, List[str]]:
        """
        并行从三个来源拓展关键词
        返回: {"youtube": [...], "related": [...], "ideas": [...]}
        """
        print(f"\n🔍 开始拓展关键词: {seed_keyword}")

        results = {
            "youtube": [],
            "related": [],
            "ideas": []
        }

        # 1. YouTube自动补全
        print("  → YouTube自动补全...")
        results["youtube"] = self._expand_youtube(seed_keyword, max_per_source=max_keywords//3)
        print(f"    ✓ 获得 {len(results['youtube'])} 个关键词")

        # 2. DataForSEO related_keywords
        if self.dataforseo_login and self.dataforseo_password:
            print("  → DataForSEO related_keywords...")
            results["related"] = self._expand_dataforseo_related(seed_keyword, depth=depth)
            print(f"    ✓ 获得 {len(results['related'])} 个关键词")

            # 3. DataForSEO keyword_ideas
            print("  → DataForSEO keyword_ideas...")
            results["ideas"] = self._expand_dataforseo_ideas(seed_keyword)
            print(f"    ✓ 获得 {len(results['ideas'])} 个关键词")
        else:
            print("  ⚠️  未配置DataForSEO凭据，跳过DataForSEO拓展")

        return results

    def merge_and_deduplicate(self, results: Dict[str, List[str]]) -> List[Dict]:
        """
        合并三个来源的结果，去重，记录来源
        返回: [{"keyword": "...", "sources": ["youtube", "related"]}]
        """
        keyword_map = {}  # {keyword_lower: {"keyword": original, "sources": [...]}}

        for source, keywords in results.items():
            for kw in keywords:
                kw_clean = kw.strip().lower()
                if not kw_clean or kw_clean in self.blacklist:
                    continue

                if kw_clean not in keyword_map:
                    keyword_map[kw_clean] = {
                        "keyword": kw.strip(),
                        "sources": []
                    }

                if source not in keyword_map[kw_clean]["sources"]:
                    keyword_map[kw_clean]["sources"].append(source)

        merged = list(keyword_map.values())
        print(f"\n✓ 合并后共 {len(merged)} 个去重关键词")
        return merged

    def _expand_youtube(self, seed: str, max_per_source: int = 20) -> List[str]:
        """YouTube自动补全"""
        keywords = set()

        # 基础请求
        suggestions = self._fetch_youtube_suggestions(seed)
        keywords.update(suggestions)

        # 加常见后缀再请求
        suffixes = ["how to", "review", "tutorial", "vs", "alternative", "best"]
        for suffix in suffixes:
            if len(keywords) >= max_per_source:
                break
            query = f"{seed} {suffix}"
            suggestions = self._fetch_youtube_suggestions(query)
            keywords.update(suggestions)
            time.sleep(0.5)  # 避免限流

        return list(keywords)[:max_per_source]

    def _fetch_youtube_suggestions(self, query: str) -> List[str]:
        """获取YouTube自动补全建议"""
        try:
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })

            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list) and len(data) > 1:
                    return data[1] if isinstance(data[1], list) else []
        except Exception as e:
            print(f"    ⚠️  YouTube建议获取失败: {e}")

        return []

    def _expand_dataforseo_related(self, seed: str, depth: int = 1) -> List[str]:
        """DataForSEO related_keywords"""
        if not self._check_dataforseo_auth():
            return []

        try:
            url = "https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live"
            payload = [{
                "keyword": seed,
                "location_code": 2840,  # United States
                "language_code": "en",
                "depth": min(depth, 3),  # 限制最大深度
                "limit": 50
            }]

            data = self._call_dataforseo_api(url, payload)

            keywords = []
            if data and "tasks" in data:
                for task in data["tasks"]:
                    if task.get("status_code") == 20000:
                        result = task.get("result", [])
                        if result:
                            items = result[0].get("items", [])
                            for item in items:
                                kw = item.get("keyword")
                                if kw:
                                    keywords.append(kw)

            return keywords

        except Exception as e:
            print(f"    ⚠️  DataForSEO related_keywords失败: {e}")
            return []

    def _expand_dataforseo_ideas(self, seed: str) -> List[str]:
        """DataForSEO keyword_ideas"""
        if not self._check_dataforseo_auth():
            return []

        try:
            url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live"
            payload = [{
                "keywords": [seed],
                "location_code": 2840,  # United States
                "language_code": "en",
                "limit": 50
            }]

            data = self._call_dataforseo_api(url, payload)

            keywords = []
            if data and "tasks" in data:
                for task in data["tasks"]:
                    if task.get("status_code") == 20000:
                        result = task.get("result", [])
                        if result:
                            items = result[0].get("items", [])
                            for item in items:
                                kw = item.get("keyword")
                                if kw:
                                    keywords.append(kw)

            return keywords

        except Exception as e:
            print(f"    ⚠️  DataForSEO keyword_ideas失败: {e}")
            return []

    def _call_dataforseo_api(self, url: str, payload: list, retry: int = 2) -> dict:
        """调用DataForSEO API（带重试）"""
        auth_str = f"{self.dataforseo_login}:{self.dataforseo_password}"
        auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")

        headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json"
        }

        for attempt in range(retry):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))

            except Exception as e:
                if attempt < retry - 1:
                    wait = 2 * (attempt + 1)
                    print(f"    ↳ 重试中（{wait}s）...")
                    time.sleep(wait)
                else:
                    raise e

        return {}

    def _check_dataforseo_auth(self) -> bool:
        """检查DataForSEO凭据"""
        return bool(self.dataforseo_login and self.dataforseo_password)


def estimate_dataforseo_cost(num_tasks: int, avg_results_per_task: int = 50) -> float:
    """
    预估DataForSEO成本
    - 任务费：$0.012/task
    - 结果费：$0.00012/result
    """
    task_cost = num_tasks * 0.012
    result_cost = num_tasks * avg_results_per_task * 0.00012
    return round(task_cost + result_cost, 4)
