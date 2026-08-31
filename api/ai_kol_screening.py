"""
AI KOL 智能筛选 - 后端API模块

完整流程：
1. 功能点输入 → AI生成关键词
2. 关键词搜索 → 候选视频池
3. 按频道聚合 → 门槛过滤
4. AI相关性判断 → AI适配度判断
5. 结果导出
"""

import os
import sys
import json
import time
import subprocess
import shutil
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

# 添加workspace到路径
workspace_path = os.path.join(os.path.dirname(__file__), '../01_请在这个文件夹里操作')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

try:
    from ai_video_relevance import AIVideoRelevanceJudge, KeywordQuery, RelevanceVerdict
    from ai_kol_scorer import AIKOLScorer, FitVerdict
except ImportError:
    print("⚠️ 无法导入AI模块，部分功能可能不可用")
    AIVideoRelevanceJudge = None
    AIKOLScorer = None


class ScreeningStatus(str, Enum):
    """筛选状态"""
    IDLE = "idle"
    GENERATING_KEYWORDS = "generating_keywords"
    SEARCHING_VIDEOS = "searching_videos"
    AGGREGATING_CHANNELS = "aggregating_channels"
    FILTERING_THRESHOLDS = "filtering_thresholds"
    JUDGING_RELEVANCE = "judging_relevance"
    FETCHING_CHANNEL_DETAILS = "fetching_channel_details"
    SCORING_FIT = "scoring_fit"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScreeningProgress:
    """筛选进度"""
    status: ScreeningStatus
    message: str
    current: int = 0
    total: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class KeywordVariant:
    """关键词变体"""
    keyword: str
    enabled: bool = True


@dataclass
class ChannelCandidate:
    """频道候选"""
    channel_id: str
    channel_name: str
    channel_url: str
    subscriber_count: int
    matched_videos: List[Dict[str, Any]]  # 命中的视频列表
    channel_description: str = ""
    recent_videos: List[Dict[str, Any]] = None
    recent_avg_views: int = 0
    relevance_verdict: str = ""
    relevance_reason: str = ""
    fit_score: int = 0
    fit_verdict: str = ""
    fit_reason: str = ""
    suggested_angle: str = ""
    excluded_by_threshold: bool = False
    exclusion_reason: str = ""

    def __post_init__(self):
        if self.recent_videos is None:
            self.recent_videos = []


class AIKOLScreeningEngine:
    """AI KOL智能筛选引擎"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_base = os.getenv("ANTHROPIC_API_BASE")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")

        # 初始化AI客户端
        if self.api_key and Anthropic:
            if self.api_base:
                base = self.api_base[:-3] if self.api_base.endswith('/v1') else self.api_base
                self.client = Anthropic(api_key=self.api_key, base_url=base)
            else:
                self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

        # 查找yt-dlp
        self.ytdlp_cmd = self._find_ytdlp()

    def _find_ytdlp(self) -> List[str]:
        """查找yt-dlp可执行文件"""
        try:
            subprocess.run([sys.executable, "-m", "yt_dlp", "--version"],
                         capture_output=True, check=True)
            return [sys.executable, "-m", "yt_dlp"]
        except Exception:
            pass

        p = shutil.which("yt-dlp")
        if p:
            return [p]

        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        user_bin = os.path.expanduser(f"~/Library/Python/{ver}/bin/yt-dlp")
        if os.path.exists(user_bin):
            return [user_bin]

        return []

    def generate_keywords(self, feature_description: str, count: int = 10) -> List[str]:
        """
        AI生成差异化关键词

        Args:
            feature_description: 功能点描述
            count: 生成数量

        Returns:
            关键词列表
        """
        if not self.client:
            raise ValueError("AI客户端未初始化")

        prompt = f"""基于以下产品功能，生成 {count} 个差异化的YouTube搜索关键词。

产品：HitPaw VikPea（视频增强软件）
功能点：{feature_description}

要求：
1. 关键词需要覆盖不同角度：教程、评测、对比、问题解决等
2. 包含不同的表达方式和同义词
3. 适合YouTube搜索
4. 每个关键词长度适中（2-5个词）
5. 关键词要有一定的搜索量，避免过于冷门

请直接返回JSON格式：
{{"keywords": ["keyword1", "keyword2", ...]}}

只返回JSON，不要其他说明。"""

        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )

                text = response.content[0].text.strip()
                # 提取JSON
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                data = json.loads(text)
                keywords = data.get("keywords", [])

                if keywords and len(keywords) > 0:
                    return keywords[:count]

            except Exception as e:
                if attempt == 2:
                    raise Exception(f"AI关键词生成失败: {str(e)}")
                time.sleep(2 ** attempt)

        return []

    def search_videos_by_keyword(
        self,
        keyword: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        使用yt-dlp搜索YouTube视频

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            视频列表
        """
        if not self.ytdlp_cmd:
            raise ValueError("yt-dlp未安装")

        try:
            cmd = self.ytdlp_cmd + [
                f"ytsearch{max_results}:{keyword}",
                "--dump-json",
                "--no-warnings",
                "--ignore-errors"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            videos = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    videos.append({
                        'video_id': data.get('id', ''),
                        'title': data.get('title', ''),
                        'description': data.get('description', '')[:5000],  # 限制长度
                        'channel_id': data.get('channel_id', ''),
                        'channel': data.get('channel', ''),
                        'channel_url': data.get('channel_url', ''),
                        'view_count': data.get('view_count', 0),
                        'tags': data.get('tags', []),
                        'url': f"https://www.youtube.com/watch?v={data.get('id', '')}",
                        'source_keyword': keyword
                    })
                except json.JSONDecodeError:
                    continue

            return videos

        except subprocess.TimeoutExpired:
            raise Exception(f"搜索超时: {keyword}")
        except Exception as e:
            raise Exception(f"搜索失败 ({keyword}): {str(e)}")

    def aggregate_by_channel(
        self,
        videos: List[Dict[str, Any]]
    ) -> Dict[str, ChannelCandidate]:
        """
        按频道聚合视频

        Args:
            videos: 视频列表

        Returns:
            频道候选字典 {channel_id: ChannelCandidate}
        """
        channels = {}

        for video in videos:
            channel_id = video.get('channel_id')
            if not channel_id:
                continue

            if channel_id not in channels:
                channels[channel_id] = ChannelCandidate(
                    channel_id=channel_id,
                    channel_name=video.get('channel', ''),
                    channel_url=video.get('channel_url', ''),
                    subscriber_count=0,  # 稍后获取
                    matched_videos=[]
                )

            # 添加命中视频
            channels[channel_id].matched_videos.append({
                'video_id': video.get('video_id'),
                'title': video.get('title'),
                'description': video.get('description'),
                'url': video.get('url'),
                'view_count': video.get('view_count', 0),
                'tags': video.get('tags', []),
                'source_keyword': video.get('source_keyword')
            })

        return channels

    def apply_threshold_filters(
        self,
        candidates: Dict[str, ChannelCandidate],
        min_subscribers: int,
        max_subscribers: int,
        min_video_views: int,
        min_recent_avg_views: int
    ) -> Dict[str, ChannelCandidate]:
        """
        应用门槛过滤

        Args:
            candidates: 候选字典
            min_subscribers: 最小粉丝数
            max_subscribers: 最大粉丝数
            min_video_views: 最小视频播放量
            min_recent_avg_views: 最小近期平均播放量

        Returns:
            过滤后的候选字典
        """
        for channel_id, candidate in candidates.items():
            # 第一轮：粉丝数和视频播放量
            if candidate.subscriber_count < min_subscribers:
                candidate.excluded_by_threshold = True
                candidate.exclusion_reason = f"粉丝数 {candidate.subscriber_count} < {min_subscribers}"
                continue

            if candidate.subscriber_count > max_subscribers:
                candidate.excluded_by_threshold = True
                candidate.exclusion_reason = f"粉丝数 {candidate.subscriber_count} > {max_subscribers}"
                continue

            # 检查命中视频播放量
            max_views = max([v.get('view_count', 0) for v in candidate.matched_videos], default=0)
            if max_views < min_video_views:
                candidate.excluded_by_threshold = True
                candidate.exclusion_reason = f"最高播放量 {max_views} < {min_video_views}"
                continue

            # 第二轮：近期平均播放量（需要先获取频道详情）
            if candidate.recent_avg_views > 0 and candidate.recent_avg_views < min_recent_avg_views:
                candidate.excluded_by_threshold = True
                candidate.exclusion_reason = f"近期均播 {candidate.recent_avg_views} < {min_recent_avg_views}"

        return candidates

    def fetch_channel_details(self, channel_id: str) -> Dict[str, Any]:
        """
        获取频道详细信息（使用yt-dlp）

        Args:
            channel_id: 频道ID

        Returns:
            频道信息字典
        """
        if not self.ytdlp_cmd:
            return {}

        try:
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            cmd = self.ytdlp_cmd + [
                channel_url,
                "--dump-json",
                "--playlist-end", "10",
                "--no-warnings"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            videos = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    videos.append({
                        'title': data.get('title', ''),
                        'view_count': data.get('view_count', 0),
                        'upload_date': data.get('upload_date', '')
                    })
                except json.JSONDecodeError:
                    continue

            # 计算近期平均播放量
            recent_avg = 0
            if videos:
                recent_views = [v['view_count'] for v in videos[:5]]
                recent_avg = sum(recent_views) // len(recent_views) if recent_views else 0

            return {
                'recent_videos': videos[:10],
                'recent_avg_views': recent_avg,
                'subscriber_count': 0  # yt-dlp不返回订阅数，需要YouTube API
            }

        except Exception:
            return {}

    def judge_relevance_batch(
        self,
        candidates: List[ChannelCandidate],
        feature_description: str
    ) -> List[ChannelCandidate]:
        """
        批量AI相关性判断

        Args:
            candidates: 候选列表
            feature_description: 功能点描述

        Returns:
            更新后的候选列表
        """
        if not AIVideoRelevanceJudge:
            # 如果没有AI模块，默认全部相关
            for candidate in candidates:
                candidate.relevance_verdict = RelevanceVerdict.RELEVANT.value
                candidate.relevance_reason = "AI模块未加载，默认相关"
            return candidates

        judge = AIVideoRelevanceJudge(api_key=self.api_key)

        for candidate in candidates:
            if candidate.excluded_by_threshold:
                continue

            # 综合所有命中视频的信息
            all_titles = [v['title'] for v in candidate.matched_videos]
            all_descriptions = [v['description'] for v in candidate.matched_videos]
            all_tags = []
            for v in candidate.matched_videos:
                all_tags.extend(v.get('tags', []))

            combined_title = " | ".join(all_titles[:3])  # 取前3个
            combined_desc = "\n\n".join(all_descriptions[:2])  # 取前2个

            keyword_query = KeywordQuery.from_string(feature_description)

            try:
                result = judge.judge_video_relevance(
                    video_url=candidate.channel_url,
                    video_title=combined_title,
                    video_description=combined_desc[:3000],
                    video_tags=list(set(all_tags))[:20],
                    keyword_query=keyword_query,
                    max_retries=3
                )

                candidate.relevance_verdict = result.verdict.value
                candidate.relevance_reason = result.reason

            except Exception as e:
                candidate.relevance_verdict = RelevanceVerdict.UNCERTAIN.value
                candidate.relevance_reason = f"AI判断失败: {str(e)}"

        return candidates

    def score_fit_batch(
        self,
        candidates: List[ChannelCandidate],
        feature_description: str
    ) -> List[ChannelCandidate]:
        """
        批量AI适配度评分

        Args:
            candidates: 候选列表
            feature_description: 功能点描述

        Returns:
            更新后的候选列表
        """
        if not AIKOLScorer:
            # 如果没有AI模块，默认待确认
            for candidate in candidates:
                candidate.fit_verdict = FitVerdict.UNCERTAIN.value
                candidate.fit_reason = "AI模块未加载"
                candidate.fit_score = 50
            return candidates

        scorer = AIKOLScorer(api_key=self.api_key)

        for candidate in candidates:
            if candidate.excluded_by_threshold:
                continue
            if candidate.relevance_verdict == RelevanceVerdict.IRRELEVANT.value:
                continue

            try:
                result = scorer.score_kol_fit(
                    channel_name=candidate.channel_name,
                    channel_url=candidate.channel_url,
                    channel_description=candidate.channel_description,
                    recent_videos=candidate.recent_videos,
                    subscriber_count=candidate.subscriber_count,
                    product_name="HitPaw VikPea",
                    product_category=feature_description,
                    max_retries=3
                )

                candidate.fit_score = result.fit_score
                candidate.fit_verdict = result.verdict.value
                candidate.fit_reason = result.reason
                candidate.suggested_angle = result.suggested_angle

            except Exception as e:
                candidate.fit_verdict = FitVerdict.UNCERTAIN.value
                candidate.fit_reason = f"AI评分失败: {str(e)}"
                candidate.fit_score = 50

        return candidates


# 全局引擎实例
_screening_engine: Optional[AIKOLScreeningEngine] = None

def get_screening_engine() -> AIKOLScreeningEngine:
    """获取筛选引擎单例"""
    global _screening_engine
    if _screening_engine is None:
        _screening_engine = AIKOLScreeningEngine()
    return _screening_engine
