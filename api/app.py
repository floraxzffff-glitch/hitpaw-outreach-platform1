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


# ======================== 错误处理 ========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }


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
