"""
AI KOL适配度判断模块 - 深度评估阶段

在视频相关性初筛通过后，对频道进行深度适配度评估
判断该KOL是否适合进行商业合作
"""

import os
import json
import time
from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ 请安装 anthropic: pip3 install anthropic")
    Anthropic = None


class FitVerdict(str, Enum):
    """KOL适配度判断结果（三状态）"""
    RECOMMENDED = "推荐"  # 高度适配，推荐合作
    UNCERTAIN = "待确认"  # 需要人工判断，或AI调用失败
    NOT_RECOMMENDED = "不推荐"  # 明确不适合合作


@dataclass
class KOLFitScoreResult:
    """KOL适配度评分结果"""
    channel_name: str
    channel_url: str
    fit_score: int  # 0-100分
    verdict: FitVerdict
    reason: str  # 判断理由
    suggested_angle: str  # 建议的合作切入角度
    ai_error: Optional[str] = None


class AIKOLScorer:
    """AI KOL适配度评分器"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        if not Anthropic:
            raise ImportError("anthropic 库未安装")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def score_kol_fit(
        self,
        channel_name: str,
        channel_url: str,
        channel_description: str,
        recent_videos: List[Dict],  # [{title, description, views, upload_date}, ...]
        subscriber_count: int,
        product_name: str = "HitPaw",
        product_category: str = "视频编辑软件",
        max_retries: int = 3
    ) -> KOLFitScoreResult:
        """
        评估KOL与产品的适配度

        Args:
            channel_name: 频道名称
            channel_url: 频道URL
            channel_description: 频道简介
            recent_videos: 最近视频列表
            subscriber_count: 订阅数
            product_name: 产品名称
            product_category: 产品类别
            max_retries: 最大重试次数

        Returns:
            KOLFitScoreResult: 适配度评分结果
        """
        for attempt in range(max_retries):
            try:
                result = self._call_ai_scorer(
                    channel_name=channel_name,
                    channel_description=channel_description,
                    recent_videos=recent_videos,
                    subscriber_count=subscriber_count,
                    product_name=product_name,
                    product_category=product_category
                )
                return KOLFitScoreResult(
                    channel_name=channel_name,
                    channel_url=channel_url,
                    fit_score=result["fit_score"],
                    verdict=result["verdict"],
                    reason=result["reason"],
                    suggested_angle=result["suggested_angle"]
                )
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    # 所有重试失败，返回"待确认"
                    return KOLFitScoreResult(
                        channel_name=channel_name,
                        channel_url=channel_url,
                        fit_score=0,
                        verdict=FitVerdict.UNCERTAIN,
                        reason="AI评分调用失败",
                        suggested_angle="",
                        ai_error=str(e)
                    )

    def _call_ai_scorer(
        self,
        channel_name: str,
        channel_description: str,
        recent_videos: List[Dict],
        subscriber_count: int,
        product_name: str,
        product_category: str
    ) -> Dict:
        """调用AI API进行适配度评分"""

        # 构建最近视频摘要
        videos_summary = []
        for v in recent_videos[:5]:  # 只看最近5个视频
            videos_summary.append(
                f"- {v.get('title', 'Unknown')} (观看: {v.get('views', 0):,})"
            )
        videos_text = "\n".join(videos_summary) if videos_summary else "无最近视频数据"

        prompt = f"""你是一个KOL营销专家。请评估以下YouTube频道是否适合推广"{product_name}"（{product_category}）。

**频道信息**:
- 频道名: {channel_name}
- 订阅数: {subscriber_count:,}
- 频道简介: {channel_description[:300]}{"..." if len(channel_description) > 300 else ""}

**最近视频**:
{videos_text}

**评估维度**:
1. 内容相关性：频道内容是否与{product_category}相关
2. 受众匹配度：观众是否是{product_name}的潜在用户
3. 合作可行性：频道规模和内容风格是否适合商业合作
4. 影响力质量：观看量/订阅数比例是否健康

**评分标准**:
- 80-100分 → "推荐"（高度适配）
- 40-79分 → "待确认"（需人工判断）
- 0-39分 → "不推荐"（明确不适合）

请严格按照以下JSON格式返回（不要有任何额外文字）：
{{
  "fit_score": 0-100的整数,
  "verdict": "推荐" 或 "待确认" 或 "不推荐",
  "reason": "简短说明评分理由（2-3句话）",
  "suggested_angle": "如果推荐或待确认，建议的合作切入角度（1句话）；如果不推荐则留空"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # 解析JSON响应
        try:
            result = json.loads(response_text)
            fit_score = int(result.get("fit_score", 0))
            verdict_str = result.get("verdict", "待确认")

            # 映射到枚举
            verdict_map = {
                "推荐": FitVerdict.RECOMMENDED,
                "待确认": FitVerdict.UNCERTAIN,
                "不推荐": FitVerdict.NOT_RECOMMENDED
            }
            verdict = verdict_map.get(verdict_str, FitVerdict.UNCERTAIN)

            return {
                "fit_score": fit_score,
                "verdict": verdict,
                "reason": result.get("reason", "AI未提供理由"),
                "suggested_angle": result.get("suggested_angle", "")
            }
        except (json.JSONDecodeError, ValueError):
            # 解析失败，尝试简单模式
            if "推荐" in response_text and "不推荐" not in response_text:
                return {
                    "fit_score": 75,
                    "verdict": FitVerdict.RECOMMENDED,
                    "reason": response_text[:100],
                    "suggested_angle": ""
                }
            elif "不推荐" in response_text:
                return {
                    "fit_score": 30,
                    "verdict": FitVerdict.NOT_RECOMMENDED,
                    "reason": response_text[:100],
                    "suggested_angle": ""
                }
            else:
                return {
                    "fit_score": 50,
                    "verdict": FitVerdict.UNCERTAIN,
                    "reason": "AI返回格式异常",
                    "suggested_angle": ""
                }


def batch_score_kol_fit(
    channels: List[Dict],
    product_name: str = "HitPaw",
    product_category: str = "视频编辑软件",
    api_key: Optional[str] = None,
    progress_callback=None
) -> List[KOLFitScoreResult]:
    """
    批量评估KOL适配度

    Args:
        channels: 频道列表，每个包含 {channel_name, channel_url, channel_description, recent_videos, subscriber_count}
        product_name: 产品名称
        product_category: 产品类别
        api_key: Anthropic API密钥
        progress_callback: 进度回调 callback(current, total, channel_name)

    Returns:
        评分结果列表
    """
    scorer = AIKOLScorer(api_key=api_key)
    results = []
    total = len(channels)

    for idx, channel in enumerate(channels, 1):
        if progress_callback:
            progress_callback(idx, total, channel.get("channel_name", "Unknown"))

        result = scorer.score_kol_fit(
            channel_name=channel.get("channel_name", ""),
            channel_url=channel.get("channel_url", ""),
            channel_description=channel.get("channel_description", ""),
            recent_videos=channel.get("recent_videos", []),
            subscriber_count=channel.get("subscriber_count", 0),
            product_name=product_name,
            product_category=product_category
        )
        results.append(result)

    return results
