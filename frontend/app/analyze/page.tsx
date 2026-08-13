/**
 * 关键词分析页面
 */

'use client';

import { useState } from 'react';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type KeywordAnalysisResponse } from '@/lib/api/vikpea';
import { formatDate, formatPercentage } from '@/lib/utils/helpers';

export default function AnalyzePage() {
  const [keyword, setKeyword] = useState('');
  const [source, setSource] = useState<'article' | 'youtube' | 'seo'>('article');
  const [limit, setLimit] = useState(30);
  const [minScore, setMinScore] = useState(3.0);
  
  const [result, setResult] = useState<KeywordAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!keyword.trim()) {
      setError('请输入关键词');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);
      
      const data = await vikpeaAPI.analyzeKeyword(keyword, source, limit, minScore);
      setResult(data);
      setSuccess('分析完成！');
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '分析失败');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">🔍 关键词分析</h1>
            <p className="text-gray-600">
              输入关键词，系统自动分析搜索潜力、邮箱发现率等数据
            </p>
          </div>

          {/* Error and Success Alerts */}
          <div className="space-y-4 mb-8">
            {error && (
              <ErrorAlert
                message={error}
                onDismiss={() => setError(null)}
              />
            )}
            {success && (
              <SuccessAlert
                message={success}
                onDismiss={() => setSuccess(null)}
              />
            )}
          </div>

          {/* Form */}
          <div className="bg-white rounded-lg shadow p-8 mb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">
                  关键词 *
                </label>
                <input
                  id="keyword"
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="例如：python web development"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  disabled={isLoading}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label htmlFor="source" className="block text-sm font-medium text-gray-700 mb-2">
                    搜索源
                  </label>
                  <select
                    id="source"
                    value={source}
                    onChange={(e) => setSource(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    disabled={isLoading}
                  >
                    <option value="article">📝 文章</option>
                    <option value="youtube">🎥 YouTube</option>
                    <option value="seo">🔍 SEO</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                    结果数量
                  </label>
                  <input
                    id="limit"
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(Math.min(100, Math.max(1, parseInt(e.target.value))))}
                    min="1"
                    max="100"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label htmlFor="minScore" className="block text-sm font-medium text-gray-700 mb-2">
                    最低评分
                  </label>
                  <input
                    id="minScore"
                    type="number"
                    value={minScore}
                    onChange={(e) => setMinScore(Math.min(10, Math.max(0, parseFloat(e.target.value))))}
                    min="0"
                    max="10"
                    step="0.1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? '分析中...' : '开始分析'}
              </button>
            </form>
          </div>

          {/* Results */}
          {isLoading && <LoadingSpinner />}

          {result && (
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                分析结果：{result.keyword}
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Card 1: Total Found */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <p className="text-gray-600 text-sm mb-2">找到结果</p>
                  <p className="text-3xl font-bold text-blue-600">{result.total_found}</p>
                  <p className="text-xs text-gray-500 mt-2">个网站/页面</p>
                </div>

                {/* Card 2: Eligible Count */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <p className="text-gray-600 text-sm mb-2">有效结果</p>
                  <p className="text-3xl font-bold text-green-600">{result.eligible_count}</p>
                  <p className="text-xs text-gray-500 mt-2">符合条件</p>
                </div>

                {/* Card 3: Email Found */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <p className="text-gray-600 text-sm mb-2">找到邮箱</p>
                  <p className="text-3xl font-bold text-purple-600">{result.email_found_count}</p>
                  <p className="text-xs text-gray-500 mt-2">个邮箱</p>
                </div>

                {/* Card 4: Email Rate */}
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                  <p className="text-gray-600 text-sm mb-2">邮箱命中率</p>
                  <p className="text-3xl font-bold text-orange-600">
                    {formatPercentage(result.email_rate)}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">百分比</p>
                </div>
              </div>

              {/* Details */}
              {result.details && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 详细信息</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(result.details).map(([key, value]) => (
                      <div key={key} className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-xs text-gray-600 capitalize mb-1">{key}</p>
                        <p className="text-sm font-semibold text-gray-900">{String(value)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Timestamp */}
              <div className="mt-6 pt-6 border-t text-xs text-gray-500">
                分析时间：{formatDate(result.timestamp)}
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
