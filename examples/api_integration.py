"""
API 集成示例和最佳实践

这个文件包含在实际项目中如何集成 VikPea API 的完整示例
"""

# ======================== 示例 1: Python 异步调用 ========================

import asyncio
from api.client import VikPeaAPIClient


async def example_python_async():
    """Python 异步使用示例"""
    
    # 初始化客户端
    async with VikPeaAPIClient("http://localhost:8000") as client:
        
        # 1. 分析关键词
        print("📊 分析关键词...")
        keyword_result = await client.analyze_keyword(
            keyword="python web development",
            source="article",
            limit=50,
            min_score=3.0
        )
        print(f"✅ 找到 {keyword_result['total_found']} 个结果")
        print(f"✅ 邮箱命中率: {keyword_result['email_rate']*100:.1f}%")
        
        # 2. 验证邮箱
        print("\n✉️  验证邮箱...")
        emails = [
            "contact@example.com",
            "info@example.org",
            "hello@example.io"
        ]
        validation_result = await client.validate_emails_batch(emails)
        print(f"✅ 验证完成: {validation_result['processed']} 个邮箱")
        
        # 3. 扫描 SEO 机会
        print("\n🔍 扫描 SEO 机会...")
        opportunities = await client.scan_seo_opportunities(
            keyword="video enhancement",
            min_score=5.0
        )
        print(f"✅ 找到 {len(opportunities)} 个 A 级机会")
        
        # 4. 生成报告
        print("\n📄 生成报告...")
        report_id = await client.generate_report(
            report_type="keyword_review",
            include_stats=True
        )
        print(f"✅ 报告已生成: {report_id}")
        
        # 5. 获取统计数据
        print("\n📈 获取统计数据...")
        stats = await client.get_statistics()
        print(f"✅ 总分析关键词数: {stats['total_keywords_analyzed']}")
        print(f"✅ 总验证邮箱数: {stats['total_emails_validated']}")


# 运行示例
# asyncio.run(example_python_async())


# ======================== 示例 2: Python 同步调用 ========================

from api.client import VikPeaAPIClientSync


def example_python_sync():
    """Python 同步使用示例（更简单）"""
    
    client = VikPeaAPIClientSync("http://localhost:8000")
    
    try:
        # 分析关键词
        result = client.analyze_keyword("digital marketing", source="seo")
        print(f"关键词 '{result['keyword']}' 分析完成")
        print(f"邮箱命中率: {result['email_rate']}")
        
        # 验证邮箱
        email = client.validate_email("contact@example.com")
        print(f"邮箱 {email['email']} 有效性: {email['is_valid']}")
        
        # 扫描 SEO
        opportunities = client.scan_seo_opportunities("marketing")
        print(f"找到 {len(opportunities)} 个机会")
        
    finally:
        client.close()


# 运行示例
# example_python_sync()


# ======================== 示例 3: JavaScript/TypeScript 调用 ========================

# 这些代码应该在前端项目中使用

# api/vikpea.ts
"""
import axios, { AxiosInstance } from 'axios';

interface KeywordAnalysisRequest {
  keyword: string;
  source: 'youtube' | 'article' | 'seo';
  limit?: number;
  min_score?: number;
}

interface KeywordAnalysisResponse {
  keyword: string;
  source: string;
  total_found: number;
  email_found_count: number;
  email_rate: number;
}

class VikPeaAPI {
  private client: AxiosInstance;
  
  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
  
  // 分析关键词
  async analyzeKeyword(data: KeywordAnalysisRequest): Promise<KeywordAnalysisResponse> {
    const response = await this.client.post('/api/analyze/keyword', data);
    return response.data;
  }
  
  // 验证邮箱
  async validateEmail(email: string) {
    const response = await this.client.post('/api/validate/email', {
      email,
      check_blacklist: true,
    });
    return response.data;
  }
  
  // 扫描 SEO 机会
  async scanSEO(keyword: string, minScore: number = 3.0) {
    const response = await this.client.post('/api/seo/scan', {
      keyword,
      source: 'seo',
      limit: 50,
      min_score: minScore,
    });
    return response.data;
  }
  
  // 生成报告
  async generateReport(reportType: string) {
    const response = await this.client.post('/api/report/generate', {
      report_type: reportType,
      include_stats: true,
    });
    return response.data;
  }
  
  // 获取统计
  async getStats() {
    const response = await this.client.get('/api/stats');
    return response.data;
  }
}

export default new VikPeaAPI();
"""


# ======================== 示例 4: React 组件示例 ========================

# components/KeywordAnalyzer.tsx
"""
'use client';

import { useState } from 'react';
import vikpeaAPI from '@/lib/api/vikpea';

export default function KeywordAnalyzer() {
  const [keyword, setKeyword] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleAnalyze = async () => {
    if (!keyword.trim()) {
      setError('请输入关键词');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const data = await vikpeaAPI.analyzeKeyword({
        keyword,
        source: 'article',
        limit: 30,
        min_score: 3.0,
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || '分析失败');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🔍 关键词分析</h1>
      
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="输入关键词..."
          className="flex-1 px-4 py-2 border rounded"
          onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? '分析中...' : '分析'}
        </button>
      </div>
      
      {error && <div className="text-red-500 mb-4">{error}</div>}
      
      {result && (
        <div className="bg-gray-100 p-4 rounded">
          <h2 className="text-lg font-bold mb-2">{result.keyword}</h2>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-600">找到结果:</span>
              <span className="font-bold ml-2">{result.total_found}</span>
            </div>
            <div>
              <span className="text-gray-600">有效结果:</span>
              <span className="font-bold ml-2">{result.eligible_count}</span>
            </div>
            <div>
              <span className="text-gray-600">邮箱找到:</span>
              <span className="font-bold ml-2">{result.email_found_count}</span>
            </div>
            <div>
              <span className="text-gray-600">邮箱命中率:</span>
              <span className="font-bold ml-2">{(result.email_rate * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
"""


# ======================== 示例 5: 批量处理 ========================

async def example_batch_processing():
    """批量处理多个关键词"""
    
    keywords = [
        {"keyword": "python web development", "source": "article"},
        {"keyword": "machine learning", "source": "youtube"},
        {"keyword": "cloud computing", "source": "seo"},
    ]
    
    async with VikPeaAPIClient("http://localhost:8000") as client:
        # 提交批处理任务
        task_id = await client.analyze_keywords_batch(keywords)
        print(f"批处理任务已提交: {task_id}")
        
        # 轮询检查结果
        import time
        max_retries = 30
        retries = 0
        
        while retries < max_retries:
            result = await client.get_batch_result(task_id)
            
            if result['status'] == 'completed':
                print(f"✅ 批处理完成")
                print(f"结果: {result['results']}")
                break
            elif result['status'] == 'failed':
                print(f"❌ 批处理失败: {result.get('error')}")
                break
            else:
                print(f"⏳ 处理中...")
                await asyncio.sleep(2)
                retries += 1


# asyncio.run(example_batch_processing())


# ======================== 示例 6: 错误处理 ========================

async def example_error_handling():
    """完整的错误处理示例"""
    
    async with VikPeaAPIClient("http://localhost:8000") as client:
        try:
            # 尝试分析空关键词（会导致错误）
            result = await client.analyze_keyword("")
        except Exception as e:
            print(f"❌ 错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            
            # 可以根据错误类型采取不同的处理方法
            if "422" in str(e):
                print("验证错误 - 请检查输入参数")
            elif "500" in str(e):
                print("服务器错误 - 请稍后重试")
            elif "timeout" in str(e):
                print("连接超时 - 请检查网络连接")


# asyncio.run(example_error_handling())


# ======================== 示例 7: 集成到 Django 项目 ========================

# Django views.py
"""
from django.shortcuts import render
from django.http import JsonResponse
from api.client import VikPeaAPIClientSync
import asyncio

def analyze_keyword_view(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        
        try:
            client = VikPeaAPIClientSync(
                base_url=os.getenv('VIKPEA_API_URL', 'http://localhost:8000')
            )
            result = client.analyze_keyword(keyword, source='article')
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            client.close()
    
    return render(request, 'analyze.html')
"""


# ======================== 示例 8: 集成到 Flask 项目 ========================

# Flask app.py
"""
from flask import Flask, request, jsonify
from api.client import VikPeaAPIClientSync
import os

app = Flask(__name__)
VIKPEA_API_URL = os.getenv('VIKPEA_API_URL', 'http://localhost:8000')

@app.route('/api/analyze', methods=['POST'])
def analyze_keyword():
    data = request.get_json()
    keyword = data.get('keyword')
    
    if not keyword:
        return jsonify({'error': '缺少关键词'}), 400
    
    try:
        client = VikPeaAPIClientSync(VIKPEA_API_URL)
        result = client.analyze_keyword(keyword)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        client.close()

if __name__ == '__main__':
    app.run(debug=True)
"""


# ======================== 示例 9: 数据库集成 ========================

async def example_database_integration():
    """将 API 结果保存到数据库"""
    
    async with VikPeaAPIClient("http://localhost:8000") as client:
        keyword = "python tutorial"
        
        # 调用 API
        result = await client.analyze_keyword(keyword)
        
        # 假设有 SQLAlchemy 数据库
        # from models import Keyword, session
        
        # db_keyword = Keyword(
        #     keyword=result['keyword'],
        #     source=result['source'],
        #     total_found=result['total_found'],
        #     email_found_count=result['email_found_count'],
        #     email_rate=result['email_rate'],
        # )
        # session.add(db_keyword)
        # session.commit()
        
        print(f"✅ 关键词 '{keyword}' 已保存到数据库")


# asyncio.run(example_database_integration())


# ======================== 示例 10: 监控和日志 ========================

import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_calls.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def example_with_logging():
    """带有详细日志的 API 调用"""
    
    logger.info("开始关键词分析")
    start_time = datetime.now()
    
    try:
        async with VikPeaAPIClient("http://localhost:8000") as client:
            result = await client.analyze_keyword("python web")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"关键词分析完成 - 耗时 {elapsed}s")
            logger.info(f"结果: 找到 {result['total_found']} 个结果")
            
            return result
    except Exception as e:
        logger.error(f"关键词分析失败: {e}", exc_info=True)
        raise


# asyncio.run(example_with_logging())


# ======================== 使用说明 ========================

"""
快速开始:

1. 同步方式 (最简单):
   from api.client import VikPeaAPIClientSync
   client = VikPeaAPIClientSync()
   result = client.analyze_keyword("python")

2. 异步方式 (推荐生产):
   from api.client import VikPeaAPIClient
   async with VikPeaAPIClient() as client:
       result = await client.analyze_keyword("python")

3. 前端使用:
   // JavaScript/TypeScript
   const response = await fetch('http://localhost:8000/api/analyze/keyword', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ keyword: 'python', source: 'article' })
   })
   const data = await response.json()

4. 错误处理:
   try {
     result = await client.analyze_keyword("...")
   } except HTTPException as e:
     print(f"API 错误: {e.detail}")
   except TimeoutError:
     print("请求超时，请重试")

5. 批处理:
   task_id = await client.analyze_keywords_batch([...])
   # 稍后检查结果
   result = await client.get_batch_result(task_id)

6. 查看完整 API 文档:
   http://localhost:8000/api/docs
"""
