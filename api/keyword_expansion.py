"""
关键词拓展模块 - 整合到主YouTube搜索流程中

从三个来源拓展关键词：
1. YouTube自动补全 (Autocomplete API)
2. DataForSEO related_keywords (如果配置)
3. DataForSEO keyword_ideas (如果配置)

然后通过AI相关度筛选过滤掉不相关的关键词
"""

import logging
import asyncio
from typing import List, Dict, Any, Set, Tuple
import urllib.parse
import requests

logger = logging.getLogger(__name__)

# YouTube自动补全API端点
YOUTUBE_AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"


def expand_from_youtube_autocomplete(seed_keyword: str) -> List[str]:
    """
    通过YouTube自动补全API拓展关键词

    Args:
        seed_keyword: 种子关键词

    Returns:
        拓展出的关键词列表
    """
    try:
        params = {
            "client": "youtube",
            "ds": "yt",
            "q": seed_keyword,
            "hl": "en",
        }

        response = requests.get(
            YOUTUBE_AUTOCOMPLETE_URL,
            params=params,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if response.status_code != 200:
            logger.warning(f"YouTube自动补全API返回状态码 {response.status_code}")
            return []

        # 返回格式: ["query", [["suggestion1", 0], ["suggestion2", 0], ...]]
        data = response.json()
        if len(data) < 2:
            return []

        suggestions = data[1]
        keywords = []
        for item in suggestions:
            if isinstance(item, list) and len(item) > 0:
                keyword = str(item[0]).strip()
                if keyword and keyword.lower() != seed_keyword.lower():
                    keywords.append(keyword)

        logger.info(f"YouTube自动补全拓展出 {len(keywords)} 个关键词")
        return keywords

    except Exception as e:
        logger.error(f"YouTube自动补全拓展失败: {e}")
        return []


def expand_from_dataforseo_related(seed_keyword: str, limit: int = 50) -> List[str]:
    """
    通过DataForSEO related_keywords API拓展关键词

    目前未实现，返回空列表
    将来可以接入DataForSEO API

    Args:
        seed_keyword: 种子关键词
        limit: 最多返回多少个关键词

    Returns:
        拓展出的关键词列表
    """
    # TODO: 实现DataForSEO related_keywords接口
    logger.info("DataForSEO related_keywords 暂未实现")
    return []


def expand_from_dataforseo_ideas(seed_keyword: str, limit: int = 50) -> List[str]:
    """
    通过DataForSEO keyword_ideas API拓展关键词

    目前未实现，返回空列表
    将来可以接入DataForSEO API

    Args:
        seed_keyword: 种子关键词
        limit: 最多返回多少个关键词

    Returns:
        拓展出的关键词列表
    """
    # TODO: 实现DataForSEO keyword_ideas接口
    logger.info("DataForSEO keyword_ideas 暂未实现")
    return []


def merge_and_deduplicate(
    autocomplete_results: List[str],
    related_results: List[str],
    ideas_results: List[str]
) -> List[str]:
    """
    合并三个来源的关键词并去重

    保持顺序：YouTube自动补全 -> DataForSEO related -> DataForSEO ideas
    """
    seen: Set[str] = set()
    merged: List[str] = []

    for keyword in autocomplete_results + related_results + ideas_results:
        # 标准化：转小写比较，但保留原始大小写
        normalized = keyword.lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            merged.append(keyword)

    return merged


def expand_keywords(
    seed_keyword: str,
    use_autocomplete: bool = True,
    use_related: bool = False,
    use_ideas: bool = False,
    max_results: int = 100
) -> Tuple[List[str], Dict[str, Any]]:
    """
    拓展关键词（三个来源并行）

    Args:
        seed_keyword: 种子关键词
        use_autocomplete: 是否使用YouTube自动补全
        use_related: 是否使用DataForSEO related_keywords
        use_ideas: 是否使用DataForSEO keyword_ideas
        max_results: 最多返回多少个关键词

    Returns:
        (expanded_keywords, stats)
        expanded_keywords: 拓展出的关键词列表
        stats: 统计信息 {source: count}
    """
    autocomplete_results = []
    related_results = []
    ideas_results = []

    # 并行调用三个来源（这里简化为顺序调用，实际可以用异步）
    if use_autocomplete:
        autocomplete_results = expand_from_youtube_autocomplete(seed_keyword)

    if use_related:
        related_results = expand_from_dataforseo_related(seed_keyword)

    if use_ideas:
        ideas_results = expand_from_dataforseo_ideas(seed_keyword)

    # 合并去重
    merged = merge_and_deduplicate(
        autocomplete_results,
        related_results,
        ideas_results
    )

    # 限制数量
    if len(merged) > max_results:
        merged = merged[:max_results]

    stats = {
        "total": len(merged),
        "autocomplete": len(autocomplete_results),
        "related": len(related_results),
        "ideas": len(ideas_results),
        "seed_keyword": seed_keyword
    }

    logger.info(f"关键词拓展完成: {seed_keyword} -> {len(merged)} 个关键词")

    return merged, stats


def expand_keywords_with_ai_filter(
    seed_keyword: str,
    use_autocomplete: bool = True,
    use_related: bool = False,
    use_ideas: bool = False,
    max_results: int = 100,
    enable_ai_filter: bool = True
) -> Dict[str, Any]:
    """
    拓展关键词并通过AI筛选

    这是完整的流程：拓展 -> AI筛选 -> 返回结果

    Args:
        seed_keyword: 种子关键词
        use_autocomplete: 是否使用YouTube自动补全
        use_related: 是否使用DataForSEO related_keywords
        use_ideas: 是否使用DataForSEO keyword_ideas
        max_results: 拓展时最多返回多少个关键词
        enable_ai_filter: 是否启用AI相关度筛选

    Returns:
        {
            "seed_keyword": str,
            "expanded_keywords": List[str],  # 拓展出的所有关键词
            "relevant_keywords": List[str],  # AI判断为相关的关键词
            "ai_details": List[Dict],        # AI判断详情
            "stats": Dict,                   # 统计信息
            "ai_enabled": bool               # 是否启用了AI筛选
        }
    """
    from ai_relevance_filter import filter_expanded_keywords

    # 第一步：拓展关键词
    expanded, stats = expand_keywords(
        seed_keyword,
        use_autocomplete=use_autocomplete,
        use_related=use_related,
        use_ideas=use_ideas,
        max_results=max_results
    )

    # 第二步：AI筛选
    if enable_ai_filter and expanded:
        relevant_keywords, ai_details = filter_expanded_keywords(
            seed_keyword,
            expanded
        )
    else:
        # 不启用AI筛选时，所有关键词都通过
        relevant_keywords = expanded
        ai_details = []

    result = {
        "seed_keyword": seed_keyword,
        "expanded_keywords": expanded,
        "relevant_keywords": relevant_keywords,
        "ai_details": ai_details,
        "stats": {
            **stats,
            "relevant_count": len(relevant_keywords),
            "filtered_count": len(expanded) - len(relevant_keywords)
        },
        "ai_enabled": enable_ai_filter
    }

    logger.info(
        f"关键词拓展+AI筛选完成: {seed_keyword} -> "
        f"{len(expanded)} 拓展 -> {len(relevant_keywords)} 相关"
    )

    return result
