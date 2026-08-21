"""
AI KOL 适配度判断模块

核心逻辑：
1. 按频道聚合候选人（同一频道通过多个关键词命中时合并）
2. AI 轻量初筛（快速筛掉明显不相关的频道）
3. 拉取频道完整信息（仅对通过初筛的频道）
4. AI 综合适配度判断（最终决策）

配置：
- 使用自定义 Claude API endpoint: https://api.vectorengine.ai/v1
- AI 调用失败时不阻塞流程，标记为"未筛选"
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ======================== 配置 ========================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_BASE = os.environ.get("ANTHROPIC_API_BASE", "https://api.vectorengine.ai/v1")
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

AI_RETRY_TIMES = 3
AI_RETRY_DELAYS = [1, 2, 4]


class Verdict(str, Enum):
    """判断结果"""
    RECOMMENDED = "推荐"
    UNCERTAIN = "待确认"
    NOT_RECOMMENDED = "不推荐"
    NOT_SCREENED = "未筛选"


@dataclass
class ChannelCandidate:
    """频道候选人（聚合后的）"""
    channel_id: str
    channel_name: str
    channel_url: str
    subscriber_count: Optional[int] = None
    hit_keywords: List[str] = field(default_factory=list)
    hit_videos: List[Dict[str, Any]] = field(default_factory=list)
    channel_description: str = ""
    recent_videos: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FitScoreResult:
    """适配度判断结果"""
    fit_score: int
    verdict: Verdict
    reason: str
    suggested_angle: str
    ai_error: Optional[str] = None


def call_claude_api(prompt: str, system_prompt: str = "", max_tokens: int = 1000) -> Optional[str]:
    """调用 Claude API，失败时自动重试"""
    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY 未配置")
        return None

    try:
        import anthropic
    except ImportError:
        logger.error("anthropic 包未安装，请运行: pip install anthropic")
        return None

    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        base_url=ANTHROPIC_API_BASE
    )

    for attempt in range(AI_RETRY_TIMES):
        try:
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                system=system_prompt if system_prompt else anthropic.NOT_GIVEN,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.warning(f"Claude API 调用失败 (尝试 {attempt + 1}/{AI_RETRY_TIMES}): {e}")
            if attempt < AI_RETRY_TIMES - 1:
                time.sleep(AI_RETRY_DELAYS[attempt])
    
    logger.error(f"Claude API 调用失败，已重试 {AI_RETRY_TIMES} 次")
    return None


def aggregate_by_channel(raw_candidates: List[Dict[str, Any]]) -> List[ChannelCandidate]:
    """按频道聚合候选人"""
    channel_map: Dict[str, ChannelCandidate] = {}

    for item in raw_candidates:
        channel_id = item.get("channel_id")
        if not channel_id:
            continue

        if channel_id not in channel_map:
            channel_map[channel_id] = ChannelCandidate(
                channel_id=channel_id,
                channel_name=item.get("channel_name", ""),
                channel_url=item.get("channel_url", ""),
                subscriber_count=item.get("subscriber_count"),
            )

        candidate = channel_map[channel_id]
        keyword = item.get("keyword", "")
        if keyword and keyword not in candidate.hit_keywords:
            candidate.hit_keywords.append(keyword)

        video_info = {
            "title": item.get("video_title", ""),
            "url": item.get("video_url", ""),
            "views": item.get("view_count", 0),
            "keyword": keyword
        }
        candidate.hit_videos.append(video_info)

    return list(channel_map.values())


def lightweight_screening(candidate: ChannelCandidate, product_feature: str) -> bool:
    """AI 轻量初筛"""
    video_titles = "\n".join([f"- {v['title']}" for v in candidate.hit_videos[:10]])

    prompt = f"""请判断这个 YouTube 频道是否值得进一步评估（用于推广 HitPaw VikPea 的「{product_feature}」功能）。

频道名称：{candidate.channel_name}
命中视频标题：
{video_titles}

只需回答"是"或"否"，并给出简要理由（1句话）。

格式：
是/否
理由：xxx"""

    system_prompt = """你是一个专业的 KOL 筛选助手。你的任务是快速判断一个 YouTube 频道是否与视频编辑、视频增强、AI 工具等主题相关。
如果频道明显是搞笑、生活、游戏等完全不相关的领域，判"否"；如果有一定相关性或不确定，判"是"。"""

    response = call_claude_api(prompt, system_prompt, max_tokens=200)
    if response is None:
        logger.warning(f"频道 {candidate.channel_name} 初筛失败（AI 调用失败），标记为通过")
        return True

    first_line = response.strip().split("\n")[0].strip()
    passed = "是" in first_line
    logger.info(f"频道 {candidate.channel_name} {'通过' if passed else '未通过'}初筛")
    return passed


def comprehensive_fit_scoring(candidate: ChannelCandidate, product_feature: str) -> FitScoreResult:
    """AI 综合适配度判断"""
    hit_videos_text = "\n".join([f"- {v['title']} (播放量: {v.get('views', 0):,})" for v in candidate.hit_videos[:10]])
    recent_videos_text = "\n".join([f"- {v.get('title', '')} (播放量: {v.get('views', 0):,})" for v in candidate.recent_videos[:10]])

    subs_display = f"{candidate.subscriber_count:,}" if candidate.subscriber_count else "未知"

    prompt = f"""请评估这个 YouTube 博主是否适合自然地推广 HitPaw VikPea 的「{product_feature}」功能。

## 频道信息
频道名称：{candidate.channel_name}
订阅数：{subs_display} 人
频道简介：{candidate.channel_description or "未提供"}

## 命中视频（通过关键词搜索找到）
{hit_videos_text}

## 近期视频（反映频道整体内容风格）
{recent_videos_text or "暂无近期视频数据"}

## 判断标准
基于这个博主的：
1. 内容风格（是否与视频编辑/增强相关）
2. 受众定位（观众是否需要视频质量提升工具）
3. 专业程度（是否有能力自然地展示技术工具）

请给出：
1. 适配度评分（0-100）
2. 判断结果（推荐/待确认/不推荐）
3. 理由（2-3句话）
4. 建议的合作切入角度（1-2句话，给 outreach 团队参考）

## 输出格式（严格JSON）
{{
  "fit_score": 85,
  "verdict": "推荐",
  "reason": "xxx",
  "suggested_angle": "xxx"
}}

注意：
- 只在明确适合或明确不适合时判"推荐"/"不推荐"
- 如果内容质量好但频道定位模糊、或信号矛盾时，才判"待确认"
- suggested_angle 要具体可操作，不要空泛"""

    system_prompt = """你是一个专业的 KOL 合作评估专家。你的任务是判断一个 YouTube 博主是否适合推广视频增强工具。
不要只看关键词匹配，要综合考虑博主的内容风格、受众和专业度。"""

    response = call_claude_api(prompt, system_prompt, max_tokens=500)

    if response is None:
        return FitScoreResult(
            fit_score=0,
            verdict=Verdict.NOT_SCREENED,
            reason="AI评分调用失败",
            suggested_angle="",
            ai_error="AI调用失败，已重试3次"
        )

    try:
        if "```json" in response:
            json_text = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_text = response.split("```")[1].split("```")[0].strip()
        else:
            json_text = response.strip()

        result = json.loads(json_text)
        return FitScoreResult(
            fit_score=result.get("fit_score", 0),
            verdict=Verdict(result.get("verdict", "待确认")),
            reason=result.get("reason", ""),
            suggested_angle=result.get("suggested_angle", "")
        )
    except Exception as e:
        logger.error(f"解析 AI 返回结果失败: {e}\n原始返回: {response}")
        return FitScoreResult(
            fit_score=0,
            verdict=Verdict.NOT_SCREENED,
            reason="AI返回格式解析失败",
            suggested_angle="",
            ai_error=f"解析失败: {str(e)}"
        )


def process_candidates_with_ai_scoring(
    raw_candidates: List[Dict[str, Any]],
    product_feature: str,
    fetch_channel_info_func: Optional[callable] = None
) -> List[Dict[str, Any]]:
    """完整的 AI KOL 适配度判断流程"""
    logger.info(f"开始 AI KOL 适配度判断，原始候选数: {len(raw_candidates)}")

    aggregated = aggregate_by_channel(raw_candidates)
    logger.info(f"频道聚合完成，去重后: {len(aggregated)} 个频道")

    results = []
    for candidate in aggregated:
        logger.info(f"处理频道: {candidate.channel_name} ({len(candidate.hit_videos)} 条命中视频)")

        if not lightweight_screening(candidate, product_feature):
            result = {
                "channel_id": candidate.channel_id,
                "channel_name": candidate.channel_name,
                "channel_url": candidate.channel_url,
                "subscriber_count": candidate.subscriber_count,
                "hit_keywords": ";".join(candidate.hit_keywords),
                "hit_video_count": len(candidate.hit_videos),
                "hit_video_urls": ";".join([v["url"] for v in candidate.hit_videos]),
                "fit_score": 0,
                "verdict": Verdict.NOT_RECOMMENDED.value,
                "reason": "AI初筛判断：频道内容与推广产品相关性低",
                "suggested_angle": "",
            }
            results.append(result)
            continue

        if fetch_channel_info_func:
            try:
                channel_info = fetch_channel_info_func(candidate.channel_id)
                candidate.channel_description = channel_info.get("description", "")
                candidate.recent_videos = channel_info.get("recent_videos", [])
            except Exception as e:
                logger.error(f"拉取频道信息失败: {e}")

        score_result = comprehensive_fit_scoring(candidate, product_feature)
        result = {
            "channel_id": candidate.channel_id,
            "channel_name": candidate.channel_name,
            "channel_url": candidate.channel_url,
            "subscriber_count": candidate.subscriber_count,
            "hit_keywords": ";".join(candidate.hit_keywords),
            "hit_video_count": len(candidate.hit_videos),
            "hit_video_urls": ";".join([v["url"] for v in candidate.hit_videos]),
            "fit_score": score_result.fit_score,
            "verdict": score_result.verdict.value,
            "reason": score_result.reason,
            "suggested_angle": score_result.suggested_angle,
        }
        if score_result.ai_error:
            result["ai_error"] = score_result.ai_error

        results.append(result)
        logger.info(f"  → 判断结果: {score_result.verdict.value} (评分: {score_result.fit_score})")

    logger.info(f"AI 判断完成，共处理 {len(results)} 个频道")
    return results
