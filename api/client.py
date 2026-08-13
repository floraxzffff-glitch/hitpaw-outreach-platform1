"""
API 客户端库 - Python/JavaScript 共用
便于前后端调用
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import httpx
import asyncio
from datetime import datetime


class ReportType(str, Enum):
    """报告类型枚举"""
    KEYWORD_REVIEW = "keyword_review"
    SEO_ANALYSIS = "seo_analysis"
    EMAIL_VALIDATION = "email_validation"


class SourceType(str, Enum):
    """搜索源类型"""
    YOUTUBE = "youtube"
    ARTICLE = "article"
    SEO = "seo"


class VikPeaAPIClient:
    """
    VikPea API 客户端
    
    使用示例：
        client = VikPeaAPIClient(base_url="http://localhost:8000")
        
        # 分析关键词
        result = await client.analyze_keyword("python tutorial", source="youtube")
        print(result)
        
        # 验证邮箱
        validation = await client.validate_email("user@example.com")
        print(validation)
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            base_url: API 服务器地址
            api_key: API 密钥（可选）
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._build_headers(),
            timeout=30.0,
        )
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    # ======================== 关键词分析 ========================
    
    async def analyze_keyword(
        self,
        keyword: str,
        source: str = "article",
        limit: int = 30,
        min_score: float = 3.0,
    ) -> Dict[str, Any]:
        """
        分析单个关键词
        
        Args:
            keyword: 搜索关键词
            source: 搜索源 (youtube, article, seo)
            limit: 结果数量限制
            min_score: 最低评分阈值
        
        Returns:
            关键词分析结果
        """
        payload = {
            "keyword": keyword,
            "source": source,
            "limit": limit,
            "min_score": min_score,
        }
        response = await self.client.post("/api/analyze/keyword", json=payload)
        return response.json()
    
    async def analyze_keywords_batch(self, keywords: List[Dict[str, Any]]) -> str:
        """
        批量分析关键词（返回任务 ID）
        
        Args:
            keywords: 关键词列表 [{"keyword": "...", "source": "..."}, ...]
        
        Returns:
            任务 ID
        """
        response = await self.client.post("/api/analyze/batch", json=keywords)
        result = response.json()
        return result.get("task_id")
    
    async def get_batch_result(self, task_id: str) -> Dict[str, Any]:
        """获取批量分析结果"""
        response = await self.client.get(f"/api/analyze/batch/{task_id}")
        return response.json()
    
    # ======================== 邮箱验证 ========================
    
    async def validate_email(
        self,
        email: str,
        check_blacklist: bool = True,
    ) -> Dict[str, Any]:
        """
        验证单个邮箱
        
        Args:
            email: 邮箱地址
            check_blacklist: 是否检查黑名单
        
        Returns:
            验证结果
        """
        payload = {
            "email": email,
            "check_blacklist": check_blacklist,
        }
        response = await self.client.post("/api/validate/email", json=payload)
        return response.json()
    
    async def validate_emails_batch(self, emails: List[str]) -> Dict[str, Any]:
        """
        批量验证邮箱
        
        Args:
            emails: 邮箱列表
        
        Returns:
            验证结果列表
        """
        response = await self.client.post("/api/validate/batch", json=emails)
        return response.json()
    
    # ======================== SEO 扫描 ========================
    
    async def scan_seo_opportunities(
        self,
        keyword: str,
        source: str = "seo",
        min_score: float = 3.0,
    ) -> List[Dict[str, Any]]:
        """
        扫描 SEO 机会
        
        Args:
            keyword: 搜索关键词
            source: 搜索源
            min_score: 最低评分
        
        Returns:
            SEO 机会列表
        """
        payload = {
            "keyword": keyword,
            "source": source,
            "limit": 50,
            "min_score": min_score,
        }
        response = await self.client.post("/api/seo/scan", json=payload)
        return response.json()
    
    # ======================== 报告生成 ========================
    
    async def generate_report(
        self,
        report_type: str,
        date_range: Optional[tuple] = None,
        include_stats: bool = True,
    ) -> str:
        """
        生成报告（返回报告 ID）
        
        Args:
            report_type: 报告类型
            date_range: 日期范围
            include_stats: 是否包含统计数据
        
        Returns:
            报告 ID
        """
        payload = {
            "report_type": report_type,
            "date_range": date_range,
            "include_stats": include_stats,
        }
        response = await self.client.post("/api/report/generate", json=payload)
        result = response.json()
        return result.get("report_id")
    
    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """获取已生成的报告"""
        response = await self.client.get(f"/api/report/{report_id}")
        return response.json()
    
    async def list_reports(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """列出所有报告"""
        response = await self.client.get("/api/reports", params={"skip": skip, "limit": limit})
        return response.json()
    
    # ======================== 统计数据 ========================
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        response = await self.client.get("/api/stats")
        return response.json()
    
    # ======================== 配置管理 ========================
    
    async def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        response = await self.client.get("/api/config")
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = await self.client.get("/health")
        return response.json()
    
    # ======================== 生命周期 ========================
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


# 同步客户端包装（用于非异步环境）
class VikPeaAPIClientSync:
    """同步版本的 VikPea API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self._client = VikPeaAPIClient(base_url, api_key)
    
    def _run_async(self, coro):
        """在事件循环中运行异步函数"""
        return asyncio.run(coro)
    
    def analyze_keyword(self, keyword: str, source: str = "article", **kwargs) -> Dict[str, Any]:
        """分析关键词（同步）"""
        return self._run_async(self._client.analyze_keyword(keyword, source, **kwargs))
    
    def validate_email(self, email: str, **kwargs) -> Dict[str, Any]:
        """验证邮箱（同步）"""
        return self._run_async(self._client.validate_email(email, **kwargs))
    
    def scan_seo_opportunities(self, keyword: str, **kwargs) -> List[Dict[str, Any]]:
        """扫描 SEO 机会（同步）"""
        return self._run_async(self._client.scan_seo_opportunities(keyword, **kwargs))
    
    def generate_report(self, report_type: str, **kwargs) -> str:
        """生成报告（同步）"""
        return self._run_async(self._client.generate_report(report_type, **kwargs))
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据（同步）"""
        return self._run_async(self._client.get_statistics())
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查（同步）"""
        return self._run_async(self._client.health_check())
    
    def close(self):
        """关闭客户端"""
        self._run_async(self._client.close())


# 使用示例代码
if __name__ == "__main__":
    
    # 异步使用示例
    async def async_example():
        async with VikPeaAPIClient("http://localhost:8000") as client:
            # 分析关键词
            result = await client.analyze_keyword("python web development")
            print("关键词分析结果:", result)
            
            # 验证邮箱
            validation = await client.validate_email("test@example.com")
            print("邮箱验证结果:", validation)
            
            # 扫描 SEO 机会
            opportunities = await client.scan_seo_opportunities("python tutorial")
            print(f"找到 {len(opportunities)} 个 SEO 机会")
            
            # 生成报告
            report_id = await client.generate_report("keyword_review")
            print(f"报告 ID: {report_id}")
    
    # 同步使用示例
    def sync_example():
        client = VikPeaAPIClientSync("http://localhost:8000")
        try:
            result = client.analyze_keyword("digital marketing")
            print("同步分析结果:", result)
        finally:
            client.close()
    
    # 运行示例（取消注释要执行的例子）
    # asyncio.run(async_example())
    # sync_example()
