"""
AI相关度筛选模块 - 使用Claude API判断关键词和视频的相关性

需求：
1. 关键词层面：拓展出的关键词批量判断是否与种子词相关
2. 视频/频道层面：通过阈值的候选视频判断是否适合合作

配置：
- 环境变量 ANTHROPIC_API_KEY
- 支持批量调用减少API次数
- 失败时不阻塞流程，标记为"需人工复查"
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

# 从环境变量或配置文件读取
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
MAX_RETRIES = 3
BATCH_SIZE_KEYWORDS = 50  # 每次批量判断的关键词数量
BATCH_SIZE_VIDEOS = 20    # 每次批量判断的视频数量


class AIRelevanceFilter:
    """AI相关度筛选器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化AI筛选器"""
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            logger.warning("未配置 ANTHROPIC_API_KEY，AI相关度筛选将被跳过")
            self.client = None
        else:
            if anthropic is None:
                raise ImportError("需要安装 anthropic: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def is_available(self) -> bool:
        """检查AI筛选是否可用"""
        return self.client is not None

    def filter_keywords_batch(
        self,
        seed_keyword: str,
        candidate_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        批量判断关键词相关性

        Args:
            seed_keyword: 种子关键词
            candidate_keywords: 候选关键词列表

        Returns:
            List[Dict]: [
                {
                    "keyword": "...",
                    "relevant": True/False,
                    "reason": "一句话理由",
                    "confidence": "high/medium/low",
                    "ai_status": "success/failed/skipped"
                },
                ...
            ]
        """
        if not self.is_available():
            return [{
                "keyword": kw,
                "relevant": True,  # 无AI时默认通过
                "reason": "AI筛选未启用，默认保留",
                "confidence": "unknown",
                "ai_status": "skipped"
            } for kw in candidate_keywords]

        results = []

        # 分批处理
        for i in range(0, len(candidate_keywords), BATCH_SIZE_KEYWORDS):
            batch = candidate_keywords[i:i + BATCH_SIZE_KEYWORDS]
            batch_results = self._judge_keywords_batch(seed_keyword, batch)
            results.extend(batch_results)

        return results

    def _judge_keywords_batch(
        self,
        seed_keyword: str,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """调用Claude API批量判断关键词相关性"""

        prompt = f"""你是一个YouTube KOL关键词筛选助手。

种子关键词："{seed_keyword}"

以下是从种子词拓展出的候选关键词列表，请判断每个候选词是否与种子词相关，是否适合用来搜索同类型的YouTube视频/博主。

候选关键词：
{json.dumps(keywords, ensure_ascii=False, indent=2)}

判断标准：
- 相关：主题一致、搜索意图相同、目标受众重叠
- 不相关：完全无关的主题、不同的产品类别、垃圾词

请以JSON格式返回结果，格式如下：
{{
  "results": [
    {{
      "keyword": "候选词1",
      "relevant": true,
      "reason": "一句话说明为什么相关或不相关",
      "confidence": "high"
    }},
    ...
  ]
}}

confidence取值：high（明确相关/不相关）、medium（需要进一步判断）、low（难以判断）

只返回JSON，不要其他解释。"""

        try:
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=4096,
                        temperature=0.3,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )

                    content = response.content[0].text

                    # 尝试解析JSON
                    # 提取JSON部分（可能包含markdown代码块）
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()

                    data = json.loads(content)
                    results = data.get("results", [])

                    # 标准化结果
                    standardized = []
                    for item in results:
                        standardized.append({
                            "keyword": item.get("keyword", ""),
                            "relevant": item.get("relevant", False),
                            "reason": item.get("reason", ""),
                            "confidence": item.get("confidence", "medium"),
                            "ai_status": "success"
                        })

                    # 确保所有关键词都有结果
                    result_keywords = {r["keyword"] for r in standardized}
                    for kw in keywords:
                        if kw not in result_keywords:
                            standardized.append({
                                "keyword": kw,
                                "relevant": True,
                                "reason": "AI未返回判断结果，默认保留",
                                "confidence": "unknown",
                                "ai_status": "partial"
                            })

                    logger.info(f"AI关键词筛选成功：{len(standardized)}个结果")
                    return standardized

                except anthropic.APIError as e:
                    logger.error(f"Claude API错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt == MAX_RETRIES - 1:
                        raise
                    continue

        except Exception as e:
            logger.error(f"AI关键词筛选失败: {e}")
            # 失败时返回默认结果（全部标记为需人工复查）
            return [{
                "keyword": kw,
                "relevant": True,  # 失败时默认保留，交给人工决策
                "reason": f"AI判断失败: {str(e)[:100]}",
                "confidence": "unknown",
                "ai_status": "failed"
            } for kw in keywords]

    def filter_videos_batch(
        self,
        seed_keyword: str,
        videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量判断视频/频道相关性

        Args:
            seed_keyword: 种子关键词
            videos: 视频列表，每个包含 title, description, channel_name

        Returns:
            List[Dict]: 原视频信息 + AI判断结果
            {
                ...原始视频信息,
                "ai_relevance": "relevant/uncertain/irrelevant",
                "ai_reason": "判断理由",
                "ai_status": "success/failed/skipped"
            }
        """
        if not self.is_available():
            for video in videos:
                video["ai_relevance"] = "uncertain"
                video["ai_reason"] = "AI筛选未启用，需人工确认"
                video["ai_status"] = "skipped"
            return videos

        results = []

        # 分批处理
        for i in range(0, len(videos), BATCH_SIZE_VIDEOS):
            batch = videos[i:i + BATCH_SIZE_VIDEOS]
            batch_results = self._judge_videos_batch(seed_keyword, batch)
            results.extend(batch_results)

        return results

    def _judge_videos_batch(
        self,
        seed_keyword: str,
        videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """调用Claude API批量判断视频相关性"""

        # 构建视频信息列表
        video_info = []
        for idx, video in enumerate(videos):
            video_info.append({
                "index": idx,
                "channel_name": video.get("channel_name", video.get("频道名", "")),
                "title": video.get("title", video.get("视频标题", "")),
                "description": (video.get("description", video.get("视频描述", "")) or "")[:500]  # 限制描述长度
            })

        prompt = f"""你是一个YouTube KOL合作筛选助手。

种子关键词："{seed_keyword}"

以下是通过这个关键词搜索到的视频/博主候选，请判断每个是否适合做insert-link或Dedicated合作。

判断标准：
- relevant（相关）：视频主题与种子词对齐，博主是真实创作者，适合合作
- uncertain（待确认）：有一定相关性但需要人工进一步判断
- irrelevant（不相关）：只是蹭关键词流量，主题不符，或明显不适合合作

视频列表：
{json.dumps(video_info, ensure_ascii=False, indent=2)}

请以JSON格式返回结果：
{{
  "results": [
    {{
      "index": 0,
      "relevance": "relevant",
      "reason": "一句话说明判断依据"
    }},
    ...
  ]
}}

只返回JSON，不要其他解释。"""

        try:
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=4096,
                        temperature=0.3,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )

                    content = response.content[0].text

                    # 提取JSON
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()

                    data = json.loads(content)
                    ai_results = {r["index"]: r for r in data.get("results", [])}

                    # 合并AI结果到原始视频数据
                    for idx, video in enumerate(videos):
                        ai_result = ai_results.get(idx, {})
                        video["ai_relevance"] = ai_result.get("relevance", "uncertain")
                        video["ai_reason"] = ai_result.get("reason", "AI未返回判断")
                        video["ai_status"] = "success" if ai_result else "partial"

                    logger.info(f"AI视频筛选成功：{len(videos)}个结果")
                    return videos

                except anthropic.APIError as e:
                    logger.error(f"Claude API错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt == MAX_RETRIES - 1:
                        raise
                    continue

        except Exception as e:
            logger.error(f"AI视频筛选失败: {e}")
            # 失败时标记为需人工复查
            for video in videos:
                video["ai_relevance"] = "uncertain"
                video["ai_reason"] = f"AI判断失败: {str(e)[:100]}"
                video["ai_status"] = "failed"
            return videos


# 全局实例
_ai_filter = None


def get_ai_filter() -> AIRelevanceFilter:
    """获取AI筛选器单例"""
    global _ai_filter
    if _ai_filter is None:
        _ai_filter = AIRelevanceFilter()
    return _ai_filter


def filter_expanded_keywords(
    seed_keyword: str,
    expanded_keywords: List[str]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    筛选拓展出的关键词

    Returns:
        (relevant_keywords, all_results)
        relevant_keywords: 相关的关键词列表（用于后续搜索）
        all_results: 所有关键词的判断详情（用于日志）
    """
    ai_filter = get_ai_filter()

    if not ai_filter.is_available():
        logger.info("AI筛选未启用，所有拓展关键词将被保留")
        return expanded_keywords, []

    results = ai_filter.filter_keywords_batch(seed_keyword, expanded_keywords)

    # 提取相关的关键词
    relevant = [r["keyword"] for r in results if r["relevant"]]

    logger.info(f"关键词AI筛选完成：{len(relevant)}/{len(expanded_keywords)} 通过")

    return relevant, results


def filter_candidate_videos(
    seed_keyword: str,
    videos: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    为候选视频添加AI相关度判断

    Returns:
        videos: 原视频列表，每个添加了 ai_relevance, ai_reason, ai_status 字段
    """
    ai_filter = get_ai_filter()

    if not ai_filter.is_available():
        logger.info("AI筛选未启用，视频将标记为待人工确认")
        for video in videos:
            video["ai_relevance"] = "uncertain"
            video["ai_reason"] = "AI筛选未启用"
            video["ai_status"] = "skipped"
        return videos

    results = ai_filter.filter_videos_batch(seed_keyword, videos)

    logger.info(f"视频AI筛选完成：{len(results)}个结果")

    return results
