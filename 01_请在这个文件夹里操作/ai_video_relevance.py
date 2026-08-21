"""
AI视频相关性判断模块 - 候选池扩大阶段

核心功能：
1. 获取视频的完整元数据（标题+简介+tags）
2. 基于标题/简介/tags综合判断视频是否与关键词真正相关
3. 扩大候选池：即使关键词只出现在简介或tag里，也能被识别为相关

架构预留：
- 支持关键词变体扩展（keyword_variants字段预留为列表）
- 数据结构可扩展，方便后续接入关键词变体生成逻辑
"""

import os
import json
import time
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ 请安装 anthropic: pip3 install anthropic")
    Anthropic = None


class RelevanceVerdict(str, Enum):
    """视频相关性判断结果"""
    RELEVANT = "相关"  # 视频内容与关键词真正相关
    IRRELEVANT = "不相关"  # 视频内容与关键词无关
    UNCERTAIN = "待确认"  # AI无法明确判断或调用失败


@dataclass
class VideoRelevanceResult:
    """视频相关性判断结果"""
    video_url: str
    video_title: str
    verdict: RelevanceVerdict
    reason: str  # 判断理由
    matched_fields: List[str]  # 关键词出现在哪些字段：title/description/tags
    ai_error: Optional[str] = None


@dataclass
class KeywordQuery:
    """
    关键词查询结构（架构预留）

    支持未来扩展：一个核心关键词对应多个变体
    例如：primary_keyword = "screen recording"
         variants = ["screen recorder", "record screen", "screen capture"]
    """
    primary_keyword: str  # 核心关键词
    variants: List[str]  # 关键词变体（当前为空列表，预留扩展）

    def all_keywords(self) -> List[str]:
        """返回所有关键词（核心词+变体）"""
        return [self.primary_keyword] + self.variants

    @classmethod
    def from_string(cls, keyword: str) -> "KeywordQuery":
        """从单个字符串创建（当前用法，变体为空）"""
        return cls(primary_keyword=keyword, variants=[])


class AIVideoRelevanceJudge:
    """AI视频相关性判断器"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        if not Anthropic:
            raise ImportError("anthropic 库未安装")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def judge_video_relevance(
        self,
        video_url: str,
        video_title: str,
        video_description: str,
        video_tags: List[str],
        keyword_query: KeywordQuery,
        max_retries: int = 3
    ) -> VideoRelevanceResult:
        """
        判断视频是否与关键词真正相关

        Args:
            video_url: 视频URL
            video_title: 视频标题
            video_description: 视频简介
            video_tags: 视频标签列表
            keyword_query: 关键词查询对象（支持变体）
            max_retries: 最大重试次数

        Returns:
            VideoRelevanceResult: 判断结果
        """
        # 检查关键词出现在哪些字段
        matched_fields = []
        all_keywords = keyword_query.all_keywords()

        for kw in all_keywords:
            kw_lower = kw.lower()
            if kw_lower in video_title.lower():
                if "title" not in matched_fields:
                    matched_fields.append("title")
            if kw_lower in video_description.lower():
                if "description" not in matched_fields:
                    matched_fields.append("description")
            for tag in video_tags:
                if kw_lower in tag.lower():
                    if "tags" not in matched_fields:
                        matched_fields.append("tags")
                    break

        # 如果关键词完全没出现，直接判定为不相关
        if not matched_fields:
            return VideoRelevanceResult(
                video_url=video_url,
                video_title=video_title,
                verdict=RelevanceVerdict.IRRELEVANT,
                reason="关键词未在标题、简介、标签中出现",
                matched_fields=[]
            )

        # 调用AI进行深度判断
        for attempt in range(max_retries):
            try:
                result = self._call_ai_judge(
                    video_title=video_title,
                    video_description=video_description,
                    video_tags=video_tags,
                    keyword_query=keyword_query,
                    matched_fields=matched_fields
                )
                return VideoRelevanceResult(
                    video_url=video_url,
                    video_title=video_title,
                    verdict=result["verdict"],
                    reason=result["reason"],
                    matched_fields=matched_fields
                )
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    # 所有重试失败，返回"待确认"
                    return VideoRelevanceResult(
                        video_url=video_url,
                        video_title=video_title,
                        verdict=RelevanceVerdict.UNCERTAIN,
                        reason="AI调用失败，需要人工确认",
                        matched_fields=matched_fields,
                        ai_error=str(e)
                    )

    def _call_ai_judge(
        self,
        video_title: str,
        video_description: str,
        video_tags: List[str],
        keyword_query: KeywordQuery,
        matched_fields: List[str]
    ) -> Dict:
        """调用AI API进行判断"""

        all_keywords = keyword_query.all_keywords()
        keywords_display = ", ".join([f'"{kw}"' for kw in all_keywords])

        prompt = f"""你是一个YouTube视频内容分析专家。请判断以下视频是否与关键词真正相关。

**关键词**: {keywords_display}
（注意：如果有多个关键词，它们是同一概念的不同表达形式）

**视频信息**:
- 标题: {video_title}
- 简介: {video_description[:500]}{"..." if len(video_description) > 500 else ""}
- 标签: {", ".join(video_tags[:20])}

**关键词出现位置**: {", ".join(matched_fields)}

**判断标准**:
1. "相关"：视频的核心内容确实是关于该关键词的主题（教程、评测、使用技巧等）
2. "不相关"：关键词只是偶然提及，或视频主题完全不同（例如关键词是"screen recording"但视频是游戏直播）
3. "待确认"：信息不足以明确判断

请严格按照以下JSON格式返回（不要有任何额外文字）：
{{
  "verdict": "相关" 或 "不相关" 或 "待确认",
  "reason": "简短说明判断理由（1-2句话）"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # 解析JSON响应
        try:
            result = json.loads(response_text)
            verdict_str = result.get("verdict", "待确认")

            # 映射到枚举
            verdict_map = {
                "相关": RelevanceVerdict.RELEVANT,
                "不相关": RelevanceVerdict.IRRELEVANT,
                "待确认": RelevanceVerdict.UNCERTAIN
            }
            verdict = verdict_map.get(verdict_str, RelevanceVerdict.UNCERTAIN)

            return {
                "verdict": verdict,
                "reason": result.get("reason", "AI未提供理由")
            }
        except json.JSONDecodeError:
            # AI返回的不是有效JSON，尝试简单解析
            if "相关" in response_text and "不相关" not in response_text:
                return {
                    "verdict": RelevanceVerdict.RELEVANT,
                    "reason": response_text[:100]
                }
            elif "不相关" in response_text:
                return {
                    "verdict": RelevanceVerdict.IRRELEVANT,
                    "reason": response_text[:100]
                }
            else:
                return {
                    "verdict": RelevanceVerdict.UNCERTAIN,
                    "reason": "AI返回格式异常"
                }


def batch_judge_video_relevance(
    videos: List[Dict],
    keyword: str,
    api_key: Optional[str] = None,
    progress_callback=None
) -> List[VideoRelevanceResult]:
    """
    批量判断视频相关性

    Args:
        videos: 视频列表，每个包含 {video_url, title, description, tags}
        keyword: 关键词字符串
        api_key: Anthropic API密钥
        progress_callback: 进度回调函数 callback(current, total, video_title)

    Returns:
        判断结果列表
    """
    judge = AIVideoRelevanceJudge(api_key=api_key)
    keyword_query = KeywordQuery.from_string(keyword)

    results = []
    total = len(videos)

    for idx, video in enumerate(videos, 1):
        if progress_callback:
            progress_callback(idx, total, video.get("title", "Unknown"))

        result = judge.judge_video_relevance(
            video_url=video.get("video_url", ""),
            video_title=video.get("title", ""),
            video_description=video.get("description", ""),
            video_tags=video.get("tags", []),
            keyword_query=keyword_query
        )
        results.append(result)

    return results
