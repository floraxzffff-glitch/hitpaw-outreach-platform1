"""
VikPea SEO API - FastAPI 应用入口
自动化邮箱开发工具的 Web API 版本
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging

import vikpea_bridge
from dataforseo_client import DataForSEOClient, test_dataforseo_connection
import filter_config
import contact_threshold_config
import contacted_history_api
import keyword_expansion
from ai_relevance_filter import filter_candidate_videos

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(
    title="VikPea SEO API",
    description="VikPea 外联工作台 - 自动化 SEO 和邮箱开发工具",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# 配置 CORS - 允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],  # 开发环境允许所有，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================== 数据模型 ========================

class KeywordInput(BaseModel):
    """关键词输入模型"""
    keyword: str = Field(..., description="搜索关键词")
    source: str = Field("article", description="搜索源类型: youtube, article, seo")
    limit: int = Field(30, description="搜索结果数量限制", ge=1, le=100)
    min_score: float = Field(3.0, description="最低评分阈值", ge=0, le=10)


class EmailInput(BaseModel):
    """邮箱输入模型"""
    email: str = Field(..., description="要验证的邮箱地址")
    check_blacklist: bool = Field(True, description="是否检查黑名单")


class KeywordAnalysisResult(BaseModel):
    """关键词分析结果"""
    keyword: str
    source: str
    total_found: int
    eligible_count: int
    email_found_count: int
    email_rate: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class EmailValidationResult(BaseModel):
    """邮箱验证结果"""
    email: str
    is_valid: bool
    reason: Optional[str] = None
    is_blacklisted: bool = False
    confidence_score: float = Field(..., ge=0, le=1)


class SEOOpportunity(BaseModel):
    """SEO 机会对象"""
    url: str = Field(..., description="机会链接")
    title: str = Field(..., description="页面标题")
    relevance_score: float = Field(..., description="相关性评分", ge=0, le=10)
    level: str = Field(..., description="机会等级: A, B, C")
    opportunity_type: str = Field(..., description="机会类型")
    action: str = Field(..., description="建议行动")
    timestamp: datetime = Field(default_factory=datetime.now)


class ReportRequest(BaseModel):
    """报告生成请求"""
    report_type: str = Field(..., description="报告类型: keyword_review, seo_analysis, email_validation")
    date_range: Optional[tuple] = Field(None, description="日期范围")
    include_stats: bool = Field(True, description="是否包含统计数据")


class Report(BaseModel):
    """报告对象"""
    report_id: str
    report_type: str
    title: str
    generated_at: datetime
    data: Dict[str, Any]
    file_url: Optional[str] = None


# 生成过的报告 / 批量任务结果存进程内存（无数据库；重启服务会清空，符合当前规模）
REPORTS_STORE: Dict[str, Report] = {}
BATCH_TASKS_STORE: Dict[str, Dict[str, Any]] = {}


# ======================== 路由 - 健康检查 ========================

@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "VikPea SEO API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
    }


# ======================== 路由 - 关键词分析 ========================

@app.post("/api/analyze/keyword", response_model=KeywordAnalysisResult, tags=["Analysis"])
async def analyze_keyword(keyword_input: KeywordInput):
    """
    分析关键词的搜索潜力
    
    - **keyword**: 搜索关键词
    - **source**: 搜索源 (youtube, article, seo)
    - **limit**: 结果数量
    - **min_score**: 最低评分
    
    返回: 关键词分析结果（包括找到的邮箱数、邮箱命中率等）
    """
    try:
        logger.info(f"分析关键词: {keyword_input.keyword} (源: {keyword_input.source})")

        data = vikpea_bridge.lookup_keyword(keyword_input.keyword)

        result = KeywordAnalysisResult(
            keyword=keyword_input.keyword,
            source=keyword_input.source,
            total_found=data["total_found"],
            eligible_count=data["eligible_count"],
            email_found_count=data["email_found_count"],
            email_rate=data["email_rate"],
            timestamp=datetime.now(),
            details=data["details"],
        )
        return result
    except Exception as e:
        logger.error(f"关键词分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyze/keywords", tags=["Analysis"])
async def list_keyword_reviews():
    """
    列出所有有历史数据的关键词复盘结果（来自 VikPea_关键词搜索记录.xlsx + VikPea_邮件开发追踪.xlsx）
    """
    return {"keywords": vikpea_bridge.list_keyword_reviews()}


@app.get("/api/analyze/clusters", tags=["Analysis"])
async def get_keyword_clusters():
    """
    按主题对 VikPea_文章搜索关键词.xlsx 里启用的关键词做聚类（来自 VikPea_关键词聚类.py 的真实逻辑）
    """
    return {"clusters": vikpea_bridge.cluster_article_keywords()}


@app.post("/api/analyze/batch", tags=["Analysis"])
async def analyze_keywords_batch(keywords: List[KeywordInput], background_tasks: BackgroundTasks):
    """
    批量分析多个关键词（后台任务）
    
    返回: 任务 ID，可用于查询结果
    """
    task_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(f"批量分析关键词: {len(keywords)} 个 (任务ID: {task_id})")

    BATCH_TASKS_STORE[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "results": [],
        "error": None,
    }
    background_tasks.add_task(process_keywords_batch, task_id, keywords)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "keywords_count": len(keywords),
        "message": "后台任务已启动，请稍后查询结果"
    }


@app.get("/api/analyze/batch/{task_id}", tags=["Analysis"])
async def get_batch_result(task_id: str):
    """
    获取批量分析任务的结果
    """
    task = BATCH_TASKS_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


# ======================== 路由 - 邮箱验证 ========================

@app.post("/api/validate/email", response_model=EmailValidationResult, tags=["Validation"])
async def validate_email(email_input: EmailInput):
    """
    验证单个邮箱地址
    
    - **email**: 邮箱地址
    - **check_blacklist**: 是否检查黑名单
    
    返回: 邮箱验证结果（有效性、置信度、是否在黑名单等）
    """
    try:
        logger.info(f"验证邮箱: {email_input.email}")

        data = vikpea_bridge.validate_email_address(email_input.email, email_input.check_blacklist)
        return EmailValidationResult(**data)
    except Exception as e:
        logger.error(f"邮箱验证失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate/batch", tags=["Validation"])
async def validate_emails_batch(emails: List[str]):
    """
    批量验证邮箱列表（走 VikPea_common.py 里真实的 classify_bad_email + 黑名单规则）
    """
    logger.info(f"批量验证邮箱: {len(emails)} 个")

    results = [
        EmailValidationResult(**vikpea_bridge.validate_email_address(email))
        for email in emails[:100]  # 限制 100 个
    ]

    return {
        "total": len(emails),
        "processed": len(results),
        "results": results,
        "timestamp": datetime.now()
    }


# ======================== 路由 - SEO 机会扫描 ========================

@app.post("/api/seo/scan", response_model=List[SEOOpportunity], tags=["SEO"])
async def scan_seo_opportunities(keyword_input: KeywordInput):
    """
    扫描 SEO 机会
    
    - **keyword**: 搜索关键词
    - **min_score**: 最低评分（用于过滤）
    
    返回: SEO 机会列表（URL、评分、等级、建议等）
    """
    try:
        logger.info(f"查询 SEO 机会: {keyword_input.keyword}")

        # 注意：这里读取的是 VikPea_SEO渠道机会扫描.xlsx 里"上一次"跑桌面脚本产生的结果，
        # 按关键词做过滤，不是网页端实时发起新的抓取（实时扫描是后续的后台任务功能）。
        rows = vikpea_bridge.get_seo_opportunities(
            keyword=keyword_input.keyword, min_score=keyword_input.min_score
        )
        opportunities = [
            SEOOpportunity(
                url=row["url"],
                title=row["title"],
                relevance_score=row["relevance_score"],
                level=row["level"],
                opportunity_type=row["opportunity_type"],
                action=row["action"],
                timestamp=row["timestamp"],
            )
            for row in rows
        ]
        return opportunities
    except Exception as e:
        logger.error(f"SEO 扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================== 路由 - YouTube KOL 搜索 ========================
# 这一段直接跑真正的 VikPea_YouTube批量搜索.py（yt-dlp 抓取 + 找邮箱 + 写发信名单），
# 是分钟级的重活，所以是"提交任务 -> 轮询状态"模式，不是一次性返回结果。
# 同一时间只能有一个这样的任务在跑（跟桌面工作台共用同一批 xlsx，避免并发写冲突）。

class YoutubeKeywordToggle(BaseModel):
    keyword: str = Field(..., description="关键词（表里没有会新增一行）")
    enabled: bool = Field(..., description="是否启用")
    note: Optional[str] = Field(None, description="备注，不传则不改")


@app.get("/api/youtube/keywords", tags=["YouTube"])
async def list_youtube_keywords():
    """列出 VikPea_搜索关键词.xlsx 里的所有关键词及启用状态"""
    return {"keywords": vikpea_bridge.list_youtube_keywords()}


@app.post("/api/youtube/keywords/toggle", tags=["YouTube"])
async def toggle_youtube_keyword(payload: YoutubeKeywordToggle):
    """开关某个关键词（不存在则新增）；实际写入 VikPea_搜索关键词.xlsx"""
    try:
        vikpea_bridge.set_youtube_keyword(payload.keyword, payload.enabled, payload.note)
        return {"status": "ok", "keywords": vikpea_bridge.list_youtube_keywords()}
    except Exception as e:
        logger.error(f"更新关键词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class YoutubeKeywordsBatch(BaseModel):
    keywords: List[str] = Field(..., description="一批关键词，比如从 Excel 整列复制粘贴过来的")


@app.post("/api/youtube/keywords/batch", tags=["YouTube"])
async def add_youtube_keywords_batch(payload: YoutubeKeywordsBatch):
    """一次加一批关键词（粘贴多行时用），全部默认启用"""
    try:
        return vikpea_bridge.add_youtube_keywords_batch(payload.keywords)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量添加关键词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/youtube/keywords/{keyword}", tags=["YouTube"])
async def delete_youtube_keyword(keyword: str):
    """删除一个关键词"""
    try:
        return vikpea_bridge.delete_youtube_keyword(keyword)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除关键词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class KeywordExpansionRequest(BaseModel):
    seed_keyword: str = Field(..., description="种子关键词")
    use_autocomplete: bool = Field(True, description="是否使用YouTube自动补全")
    use_related: bool = Field(False, description="是否使用DataForSEO related_keywords")
    use_ideas: bool = Field(False, description="是否使用DataForSEO keyword_ideas")
    max_results: int = Field(100, description="拓展时最多返回多少个关键词", ge=10, le=200)
    enable_ai_filter: bool = Field(True, description="是否启用AI相关度筛选")


@app.post("/api/youtube/keywords/expand", tags=["YouTube"])
async def expand_youtube_keywords(payload: KeywordExpansionRequest):
    """
    关键词拓展（内嵌到主搜索流程中）

    从种子关键词拓展出相关关键词：
    1. YouTube自动补全
    2. DataForSEO related_keywords（可选）
    3. DataForSEO keyword_ideas（可选）

    然后通过AI相关度筛选（使用Claude API）过滤掉不相关的关键词

    返回：
    - expanded_keywords: 拓展出的所有关键词
    - relevant_keywords: AI判断为相关的关键词（用于后续搜索）
    - ai_details: AI判断详情（每个关键词的相关性、理由、置信度）
    """
    try:
        result = keyword_expansion.expand_keywords_with_ai_filter(
            seed_keyword=payload.seed_keyword,
            use_autocomplete=payload.use_autocomplete,
            use_related=payload.use_related,
            use_ideas=payload.use_ideas,
            max_results=payload.max_results,
            enable_ai_filter=payload.enable_ai_filter
        )
        return result
    except Exception as e:
        logger.error(f"关键词拓展失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/youtube/settings", tags=["YouTube"])
async def get_youtube_settings():
    """当前生效的搜索参数（粉丝数范围、最低播放量、活跃天数等），读的是 VikPea_配置.xlsx"""
    return vikpea_bridge.get_youtube_search_settings()


@app.put("/api/youtube/settings", tags=["YouTube"])
async def update_youtube_settings(updates: Dict[str, Any]):
    """
    改搜索参数，真实写回 VikPea_配置.xlsx。
    桌面版工作台读的是同一张表，改了这里桌面版跑出来的结果也会跟着变。
    """
    try:
        return vikpea_bridge.set_youtube_search_settings(updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新搜索参数失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/youtube/search/start", tags=["YouTube"])
async def start_youtube_search():
    """
    启动一次真实的 YouTube KOL 搜索（跑 VikPea_YouTube批量搜索.py 的 main()）。
    会真的用 yt-dlp 抓取、写入 VikPea_发信名单.xlsx / VikPea_待确认邮箱.xlsx，
    跟桌面工作台里点"2. 搜索 YouTube KOL"是同一件事。
    """
    if vikpea_bridge.is_youtube_search_running():
        raise HTTPException(status_code=409, detail="已经有一个 YouTube 搜索任务在跑，等它跑完再开始新的")
    try:
        job_id = vikpea_bridge.start_youtube_search_job()
        return {"job_id": job_id, "status": "running"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/api/youtube/search/jobs/{job_id}", tags=["YouTube"])
async def get_youtube_search_job(job_id: str):
    """轮询任务状态和实时日志（就是脚本原本会打印在终端上的那些行）"""
    job = vikpea_bridge.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job


@app.get("/api/youtube/search/jobs", tags=["YouTube"])
async def list_youtube_search_jobs():
    """列出最近的 YouTube 搜索任务（用来在刷新/重新进入页面后找回还在跑的任务）"""
    return {"jobs": vikpea_bridge.list_jobs("youtube_search")}


@app.post("/api/youtube/search/jobs/{job_id}/stop", tags=["YouTube"])
async def stop_youtube_search_job(job_id: str):
    """真正停止（杀掉）正在跑的搜索子进程"""
    ok = vikpea_bridge.stop_job(job_id)
    if not ok:
        raise HTTPException(status_code=400, detail="这个任务已经结束，或者不支持停止")
    return {"status": "stopping"}


@app.get("/api/email-templates", tags=["EmailTemplates"])
async def get_email_templates():
    """产品信息 + 开发信模板（主题/开头），读的是 VikPea_配置.xlsx。不含 SMTP 密码。"""
    return vikpea_bridge.get_email_template_settings()


@app.put("/api/email-templates", tags=["EmailTemplates"])
async def update_email_templates(updates: Dict[str, Any]):
    """
    改开发信内容，真实写回 VikPea_配置.xlsx。
    发信脚本（VikPea_读表发信.py）会用这里的内容生成邮件，桌面版和网页版共用。
    """
    try:
        return vikpea_bridge.set_email_template_settings(updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新邮件模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system-settings", tags=["Settings"])
async def get_system_settings():
    """
    SMTP/IMAP/搜索引擎API/发信节奏这些系统级配置。
    密钥类字段（密码、API Key）只返回"是否已设置"，不会把明文传出来。
    """
    return vikpea_bridge.get_system_settings()


@app.put("/api/system-settings", tags=["Settings"])
async def update_system_settings(updates: Dict[str, Any]):
    """
    改系统设置，真实写回 VikPea_配置.xlsx。
    密钥类字段留空表示不修改；只有填了新值才会覆盖已保存的密钥。
    注意：这只是存配置，不会触发任何真实发信或调用外部 API。
    """
    try:
        return vikpea_bridge.set_system_settings(updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新系统设置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send/preview", tags=["Send"])
async def preview_send(personalize: bool = False):
    """
    第一步：预览本次能发的邮件（跑真实的安全拦截/去重/主题生成逻辑），不会发送任何邮件。
    跟桌面版点发信脚本时看到的"待发 N 封"列表是同一套计算。
    """
    if vikpea_bridge.job_runner.is_resource_busy("email_send"):
        raise HTTPException(status_code=409, detail="有一批邮件正在发送中，等它跑完再预览")
    try:
        return vikpea_bridge.build_send_preview(should_personalize=personalize)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"发信预览失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SendConfirmRequest(BaseModel):
    preview_id: str = Field(..., description="/api/send/preview 返回的 preview_id")
    rownums: List[int] = Field(..., description="选中要发送的行号（来自预览结果里的 rownum）")


@app.post("/api/send/confirm", tags=["Send"])
async def confirm_send(payload: SendConfirmRequest):
    """
    第二步：明确勾选、明确点击后才会真正建立 SMTP 连接发送。
    这是唯一会真实发邮件的入口，前端必须先调用 /api/send/preview 拿到 preview_id。
    """
    try:
        job_id = vikpea_bridge.start_send_job(payload.preview_id, payload.rownums)
        return {"job_id": job_id, "status": "running"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/api/send/jobs/{job_id}", tags=["Send"])
async def get_send_job(job_id: str):
    """轮询发信任务状态和实时日志"""
    job = vikpea_bridge.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job


@app.get("/api/kol/candidates", tags=["YouTube"])
async def get_kol_candidates():
    """
    候选库：搜索出来的 KOL 都在这里。
    - confirmed: VikPea_发信名单.xlsx，高置信度，可以直接发信
    - pending: VikPea_待确认邮箱.xlsx，置信度不够高，要人工确认
    - no_email: VikPea_无邮箱候选.xlsx，暂时没找到邮箱
    这三张表是 YouTube 搜索和深度找邮箱共用的产出，不是网页独有的数据。
    """
    return {
        "confirmed": vikpea_bridge.get_confirmed_candidates(),
        "pending": vikpea_bridge.get_pending_candidates(),
        "no_email": vikpea_bridge.get_no_email_candidates(),
    }


class ConfirmedCandidateInput(BaseModel):
    频道名: Optional[str] = None
    邮箱: Optional[str] = None
    主页链接: Optional[str] = None
    视频链接: Optional[str] = None
    备注: Optional[str] = None
    类型: Optional[str] = None
    来源关键词: Optional[str] = None


@app.post("/api/kol/candidates/confirmed", tags=["YouTube"])
async def add_confirmed_candidate(payload: ConfirmedCandidateInput):
    """人工往「可直接发信」名单里加一条（比如自己搜到、已经确认能发信的博主）"""
    try:
        return vikpea_bridge.add_confirmed_candidate(payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加候选人失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/kol/candidates/confirmed/{rownum}", tags=["YouTube"])
async def update_confirmed_candidate(rownum: int, payload: ConfirmedCandidateInput):
    """编辑「可直接发信」名单里的一条（主页链接/视频链接这些）"""
    try:
        return vikpea_bridge.update_confirmed_candidate(rownum, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新候选人失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/kol/candidates/confirmed/{rownum}", tags=["YouTube"])
async def delete_confirmed_candidate(rownum: int):
    """删除「可直接发信」名单里的一条"""
    try:
        return vikpea_bridge.delete_confirmed_candidate(rownum)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除候选人失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================== 路由 - 发送追踪 ========================

@app.get("/api/tracker", tags=["Tracker"])
async def get_tracker():
    """已联络记录 + 回复/跟进进度，读的是 VikPea_邮件开发追踪.xlsx"""
    return {"rows": vikpea_bridge.get_tracker_rows()}


class TrackerUpdateInput(BaseModel):
    是否回复: Optional[str] = None
    回复摘要: Optional[str] = None
    当前状态: Optional[str] = None
    ABC分级: Optional[str] = None
    跟进1日期: Optional[str] = None
    跟进1状态: Optional[str] = None
    跟进2日期: Optional[str] = None
    跟进2状态: Optional[str] = None
    最近回复日期: Optional[str] = None


@app.put("/api/tracker/{rownum}", tags=["Tracker"])
async def update_tracker(rownum: int, payload: TrackerUpdateInput):
    """更新一条追踪记录的回复/跟进状态，真实写回 VikPea_邮件开发追踪.xlsx"""
    try:
        return vikpea_bridge.update_tracker_row(rownum, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新追踪记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================== 路由 - 报告生成 ========================

@app.post("/api/report/generate", response_model=Report, tags=["Reports"])
async def generate_report(report_request: ReportRequest):
    """
    生成分析报告
    
    - **report_type**: 报告类型
      - `keyword_review`: 关键词复盘
      - `seo_analysis`: SEO 分析
      - `email_validation`: 邮箱验证总结
    
    返回: 报告对象（包括 PDF 下载链接）
    """
    report_id = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(f"生成报告: {report_request.report_type} (ID: {report_id})")

    report_title_map = {
        "keyword_review": "关键词复盘报告",
        "seo_analysis": "SEO 机会分析报告",
        "email_validation": "邮箱验证总结报告",
    }
    report_data_builders = {
        "keyword_review": vikpea_bridge.get_keyword_review_report,
        "seo_analysis": vikpea_bridge.get_seo_analysis_report,
        "email_validation": vikpea_bridge.get_email_validation_report,
    }

    builder = report_data_builders.get(report_request.report_type)
    if not builder:
        raise HTTPException(status_code=400, detail=f"未知的报告类型: {report_request.report_type}")

    # 报告数据都来自当场读表聚合（秒级），不需要走后台任务；直接算出来存到内存里。
    data = builder()

    report = Report(
        report_id=report_id,
        report_type=report_request.report_type,
        title=report_title_map[report_request.report_type],
        generated_at=datetime.now(),
        data=data,
    )
    REPORTS_STORE[report_id] = report
    return report


@app.get("/api/report/{report_id}", tags=["Reports"])
async def get_report(report_id: str):
    """
    获取已生成的报告
    """
    logger.info(f"获取报告: {report_id}")

    report = REPORTS_STORE.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report


@app.get("/api/reports", tags=["Reports"])
async def list_reports(skip: int = 0, limit: int = 20):
    """
    列出所有报告（保存在进程内存里，重启服务会清空）
    """
    all_reports = sorted(REPORTS_STORE.values(), key=lambda r: r.generated_at, reverse=True)
    page = all_reports[skip: skip + limit]
    return {
        "total": len(all_reports),
        "reports": page,
        "skip": skip,
        "limit": limit,
    }


# ======================== 路由 - 数据上传 ========================

@app.post("/api/upload/keywords", tags=["Upload"])
async def upload_keywords(file: UploadFile = File(...)):
    """
    上传关键词文件（Excel/CSV）
    """
    logger.info(f"上传关键词文件: {file.filename}")
    
    if not file.filename.endswith(('.xlsx', '.csv', '.xls')):
        raise HTTPException(status_code=400, detail="只支持 Excel 或 CSV 文件")
    
    # TODO: 处理文件上传
    return {
        "filename": file.filename,
        "size": file.size,
        "status": "uploaded",
        "message": "文件已上传，等待处理"
    }


@app.post("/api/upload/emails", tags=["Upload"])
async def upload_emails(file: UploadFile = File(...)):
    """
    上传邮箱列表文件
    """
    logger.info(f"上传邮箱文件: {file.filename}")
    
    return {
        "filename": file.filename,
        "status": "uploaded",
        "message": "邮箱文件已上传"
    }


# ======================== 路由 - 配置管理 ========================

@app.get("/api/config", tags=["Config"])
async def get_config():
    """
    获取当前配置（不含敏感信息）
    """
    return {
        "app": "VikPea SEO API",
        "version": "2.0.0",
        "features": [
            "keyword_analysis",
            "email_validation",
            "seo_opportunity_scan",
            "report_generation",
            "batch_processing",
        ]
    }


@app.put("/api/config", tags=["Config"])
async def update_config(config: Dict[str, Any]):
    """
    更新配置
    """
    logger.info(f"更新配置")
    return {
        "status": "updated",
        "message": "配置已更新"
    }


# ======================== 路由 - 统计数据 ========================

@app.get("/api/stats", tags=["Stats"])
async def get_statistics():
    """
    获取统计数据（直接读 VikPea 工作台的真实 Excel 表聚合而来）
    """
    stats = vikpea_bridge.get_dashboard_stats()
    stats["last_updated"] = datetime.now()
    return stats


# ======================== 路由 - 过滤配置管理 ========================

@app.get("/api/filter-config", tags=["Filter"])
async def get_filter_config():
    """
    获取当前过滤配置统计信息
    """
    config = filter_config.get_filter_config()
    return {
        "negative_keywords": list(config.negative_keywords.keys()),
        "negative_keywords_count": len(config.negative_keywords),
        "competitor_sites_count": len(config.competitor_sites),
        "competitor_email_suffixes_count": len(config.competitor_email_suffixes),
        "affiliate_blacklist_count": len(config.affiliate_blacklist),
        "longterm_partners_count": len(config.longterm_partners),
        "contacted_history_count": len(config.contacted_history),
    }


@app.post("/api/filter-config/reload", tags=["Filter"])
async def reload_filter_config():
    """
    重新加载过滤配置（上传新的Excel后调用）
    """
    try:
        filter_config.reload_filter_config()
        return {
            "status": "success",
            "message": "过滤配置已重新加载"
        }
    except Exception as e:
        logger.error(f"重新加载过滤配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ContactedHistoryUpload(BaseModel):
    records: List[Dict[str, str]]


@app.post("/api/filter-config/contacted-history/upload", tags=["Filter"])
async def upload_contacted_history(payload: ContactedHistoryUpload):
    """
    上传已联络历史记录

    请求格式:
    {
        "records": [
            {"频道名": "xxx", "邮箱": "xxx@example.com", "联络日期": "2024-01-01", "备注": "xxx"},
            ...
        ]
    }
    """
    try:
        result = filter_config.upload_contacted_history(payload.records)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"上传已联络历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class NegativeKeywordThreshold(BaseModel):
    keyword: str
    threshold_days: int


@app.put("/api/filter-config/negative-keyword/threshold", tags=["Filter"])
async def update_negative_keyword_threshold(payload: NegativeKeywordThreshold):
    """
    更新负关键词的时间阈值

    小于阈值天数 = 直接排除
    大于阈值天数 = 不排除但标注
    """
    try:
        result = filter_config.update_negative_keyword_threshold(
            payload.keyword,
            payload.threshold_days
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新负关键词阈值失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ContactThreshold(BaseModel):
    threshold_days: int


@app.get("/api/filter-config/contact-threshold", tags=["Filter"])
async def get_contact_threshold():
    """
    获取联络历史时间阈值

    返回当前配置的时间阈值（天数）
    小于阈值 = 直接排除
    大于阈值 = 不排除但标注
    """
    try:
        threshold = contact_threshold_config.get_contact_threshold()
        return {
            "threshold_days": threshold,
            "message": f"当前联络历史时间阈值为 {threshold} 天"
        }
    except Exception as e:
        logger.error(f"获取联络历史阈值失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/filter-config/contact-threshold", tags=["Filter"])
async def update_contact_threshold(payload: ContactThreshold):
    """
    更新联络历史时间阈值

    小于阈值天数 = 直接排除（不出现在候选列表）
    大于阈值天数 = 不排除但标注"XX天前已联络"
    """
    try:
        result = contact_threshold_config.set_contact_threshold(payload.threshold_days)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新联络历史阈值失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/filter-config", tags=["Filter"])
async def upload_filter_config(
    file: UploadFile = File(...),
    config_type: str = "negative_keywords"
):
    """
    上传过滤配置Excel文件
    config_type: negative_keywords, competitor_sites, competitor_emails, affiliate_blacklist, longterm_partners, contacted_history
    """
    import shutil

    # 根据类型确定目标文件路径
    file_map = {
        "negative_keywords": filter_config.NEGATIVE_KEYWORDS_PATH,
        "competitor_sites": filter_config.COMPETITOR_SITES_PATH,
        "competitor_emails": filter_config.COMPETITOR_EMAILS_PATH,
        "affiliate_blacklist": filter_config.AFFILIATE_BLACKLIST_PATH,
        "longterm_partners": filter_config.LONGTERM_PARTNERS_PATH,
        "contacted_history": filter_config.CONTACTED_HISTORY_PATH,
    }

    if config_type not in file_map:
        raise HTTPException(status_code=400, detail=f"无效的配置类型: {config_type}")

    target_path = file_map[config_type]

    try:
        # 保存上传的文件
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 重新加载配置
        filter_config.reload_filter_config()

        return {
            "filename": file.filename,
            "config_type": config_type,
            "status": "uploaded",
            "message": f"{config_type} 配置已上传并加载"
        }
    except Exception as e:
        logger.error(f"上传过滤配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contacted-history", tags=["Filter"])
async def get_contacted_history():
    """
    获取所有已联络历史记录

    返回格式:
    [
        {
            "_row_index": 2,
            "频道名": "xxx",
            "邮箱": "xxx@example.com",
            "联络日期": "2024-01-01",
            "备注": "xxx"
        },
        ...
    ]
    """
    try:
        records = contacted_history_api.get_contacted_history_records()
        return {
            "records": records,
            "count": len(records)
        }
    except Exception as e:
        logger.error(f"获取已联络历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ContactedHistoryRecord(BaseModel):
    channel_name: str = Field(..., alias="频道名")
    email: str
    contact_date: str = Field(..., alias="联络日期")
    note: str = Field(default="", alias="备注")

    class Config:
        populate_by_name = True


@app.post("/api/contacted-history", tags=["Filter"])
async def add_contacted_history(payload: ContactedHistoryRecord):
    """
    添加单条已联络历史记录

    请求格式:
    {
        "频道名": "xxx",
        "email": "xxx@example.com",
        "联络日期": "2024-01-01",
        "备注": "xxx"
    }
    """
    try:
        result = contacted_history_api.add_contacted_history_record(
            channel_name=payload.channel_name,
            email=payload.email,
            contact_date=payload.contact_date,
            note=payload.note
        )

        # 重新加载过滤配置以应用新的联络历史
        filter_config.reload_filter_config()

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加已联络历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DeleteContactedHistoryRequest(BaseModel):
    row_index: int


@app.delete("/api/contacted-history", tags=["Filter"])
async def delete_contacted_history(payload: DeleteContactedHistoryRequest):
    """
    删除指定行的已联络历史记录

    请求格式:
    {
        "row_index": 2
    }
    """
    try:
        result = contacted_history_api.delete_contacted_history_record(payload.row_index)

        # 重新加载过滤配置以应用更新后的联络历史
        filter_config.reload_filter_config()

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除已联络历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================== DataForSEO API ========================

class DataForSEOTestRequest(BaseModel):
    """DataForSEO API 连接测试请求"""
    login: str = Field(..., description="DataForSEO API 用户名")
    password: str = Field(..., description="DataForSEO API 密码")


@app.post("/api/dataforseo/test", tags=["DataForSEO"])
async def test_dataforseo(payload: DataForSEOTestRequest):
    """
    测试 DataForSEO API 连接和余额
    返回账户余额、限制等信息
    """
    try:
        result = await test_dataforseo_connection(payload.login, payload.password)
        return result
    except Exception as e:
        logger.error(f"DataForSEO 连接测试失败: {e}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }


# 注意：DataForSEO Labs 没有 YouTube 频道搜索功能
# 以下端点已被新的多渠道KOL发现功能替代：
# - /api/dataforseo/keyword-research (关键词研究)
# - /api/dataforseo/find-influencer-websites (Google搜索KOL网站)
# - /api/dataforseo/youtube-video-search (通过视频发现频道)


# ==================== 新增：多渠道KOL发现功能 ====================

class KeywordResearchRequest(BaseModel):
    """关键词研究请求"""
    seed_keyword: str = Field(..., description="种子关键词，如 'tech review'")
    language_code: str = Field("en", description="语言代码")
    location_code: int = Field(2840, description="地区代码，2840=美国, 2156=中国")
    limit: int = Field(100, description="返回数量", ge=1, le=200)


@app.post("/api/dataforseo/keyword-research", tags=["DataForSEO"])
async def keyword_research(payload: KeywordResearchRequest):
    """
    关键词研究 - 找到高价值关键词
    用这些关键词去YouTube API搜索频道
    """
    try:
        config = vikpea_bridge.vikpea_common.load_config()
        login = config.get("DATAFORSEO_LOGIN")
        password = config.get("DATAFORSEO_PASSWORD")

        if not login or not password:
            raise HTTPException(
                status_code=400,
                detail="请先在系统设置中配置 DataForSEO API 凭证"
            )

        client = DataForSEOClient(login, password)
        keywords = await client.keyword_research(
            seed_keyword=payload.seed_keyword,
            language_code=payload.language_code,
            location_code=payload.location_code,
            limit=payload.limit
        )

        return {
            "seed_keyword": payload.seed_keyword,
            "total": len(keywords),
            "keywords": keywords
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"关键词研究失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class InfluencerWebsiteSearchRequest(BaseModel):
    """KOL网站搜索请求"""
    niche: str = Field(..., description="领域/行业，如 'tech blogger', 'gaming youtuber'")
    language_code: str = Field("en", description="语言代码")
    location_code: int = Field(2840, description="地区代码")
    depth: int = Field(20, description="搜索深度", ge=1, le=100)


@app.post("/api/dataforseo/find-influencer-websites", tags=["DataForSEO"])
async def find_influencer_websites(payload: InfluencerWebsiteSearchRequest):
    """
    在Google上搜索博主/KOL的个人网站
    可以找到博主的官网、YouTube频道、社交媒体等
    """
    try:
        config = vikpea_bridge.vikpea_common.load_config()
        login = config.get("DATAFORSEO_LOGIN")
        password = config.get("DATAFORSEO_PASSWORD")

        if not login or not password:
            raise HTTPException(
                status_code=400,
                detail="请先在系统设置中配置 DataForSEO API 凭证"
            )

        client = DataForSEOClient(login, password)
        websites = await client.search_influencer_websites(
            niche=payload.niche,
            language_code=payload.language_code,
            location_code=payload.location_code,
            depth=payload.depth
        )

        return {
            "niche": payload.niche,
            "total": len(websites),
            "websites": websites
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索KOL网站失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class YouTubeVideoSearchRequest(BaseModel):
    """YouTube视频搜索请求"""
    keyword: str = Field(..., description="搜索关键词")
    language_code: str = Field("en", description="语言代码")
    location_code: int = Field(2840, description="地区代码")
    depth: int = Field(20, description="搜索深度", ge=1, le=100)


@app.post("/api/dataforseo/youtube-video-search", tags=["DataForSEO"])
async def youtube_video_search(payload: YouTubeVideoSearchRequest):
    """
    搜索YouTube视频，提取频道ID
    通过视频间接发现频道（一个频道可能有多个热门视频）
    """
    try:
        config = vikpea_bridge.vikpea_common.load_config()
        login = config.get("DATAFORSEO_LOGIN")
        password = config.get("DATAFORSEO_PASSWORD")

        if not login or not password:
            raise HTTPException(
                status_code=400,
                detail="请先在系统设置中配置 DataForSEO API 凭证"
            )

        client = DataForSEOClient(login, password)
        channels = await client.search_youtube_videos(
            keyword=payload.keyword,
            language_code=payload.language_code,
            location_code=payload.location_code,
            depth=payload.depth
        )

        return {
            "keyword": payload.keyword,
            "total": len(channels),
            "channels": channels  # 已去重的频道列表
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube视频搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================== 后台任务 ========================

async def process_keywords_batch(task_id: str, keywords: List[KeywordInput]):
    """后台处理批量关键词分析（对每个关键词查真实的历史复盘数据）"""
    logger.info(f"[后台任务] 处理批量关键词分析: {task_id}")
    try:
        results = []
        for kw in keywords:
            data = vikpea_bridge.lookup_keyword(kw.keyword)
            results.append(KeywordAnalysisResult(
                keyword=kw.keyword,
                source=kw.source,
                total_found=data["total_found"],
                eligible_count=data["eligible_count"],
                email_found_count=data["email_found_count"],
                email_rate=data["email_rate"],
                timestamp=datetime.now(),
                details=data["details"],
            ))
        BATCH_TASKS_STORE[task_id] = {
            "task_id": task_id,
            "status": "completed",
            "results": results,
            "error": None,
        }
    except Exception as e:
        logger.error(f"批量关键词分析失败: {e}")
        BATCH_TASKS_STORE[task_id] = {
            "task_id": task_id,
            "status": "failed",
            "results": [],
            "error": str(e),
        }


# ======================== 启动和关闭事件 ========================

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 VikPea SEO API 启动")
    # TODO: 初始化数据库、缓存等
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 VikPea SEO API 关闭")
    # TODO: 清理资源
    pass


# ======================== 静态文件（可选） ========================

# 如果需要提供前端文件，可以取消注释：
# app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式自动重新加载
        log_level="info",
    )
