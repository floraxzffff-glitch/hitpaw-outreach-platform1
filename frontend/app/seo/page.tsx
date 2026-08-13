/**
 * SEO 扫描页面
 */

'use client';

import { useState } from 'react';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type SEOOpportunityResponse } from '@/lib/api/vikpea';
import { formatDate, getLevelBadge, getLevelColor, truncateText } from '@/lib/utils/helpers';

export default function SEOPage() {
  const [keyword, setKeyword] = useState('');
  const [minScore, setMinScore] = useState(3.0);
  
  const [opportunities, setOpportunities] = useState<SEOOpportunityResponse[]>([]);
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
      
      const data = await vikpeaAPI.scanSEO(keyword, 'seo', minScore);
      setOpportunities(data);
      setSuccess(`找到 ${data.length} 个 SEO 机会`);
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '扫描失败');
    } finally {
      setIsLoading(false);
    }
  };

  const opportunityStats = {
    total: opportunities.length,
    levelA: opportunities.filter((o) => o.level === 'A').length,
    levelB: opportunities.filter((o) => o.level === 'B').length,
    levelC: opportunities.filter((o) => o.level === 'C').length,
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">🔎 SEO 机会扫描</h1>
            <p className="text-gray-600">
              扫描关键词相关的高价值 SEO 机会和潜在合作目标
            </p>
          </div>

          {/* Error and Success Alerts */}
          <div className="space-y-4 mb-8">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && (
              <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />
            )}
          </div>

          {/* Form */}
          <div className="bg-white rounded-lg shadow p-8 mb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">
                    关键词 *
                  </label>
                  <input
                    id="keyword"
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="例如：video enhancement software"
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
                className="w-full bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold py-3 px-4 rounded-lg hover:from-purple-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? '扫描中...' : '开始扫描'}
              </button>
            </form>
          </div>

          {/* Loading */}
          {isLoading && <LoadingSpinner />}

          {/* Statistics */}
          {!isLoading && opportunities.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <p className="text-gray-600 text-sm mb-2">总计</p>
                <p className="text-3xl font-bold text-blue-600">{opportunityStats.total}</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <p className="text-gray-600 text-sm mb-2">A 级（优先）</p>
                <p className="text-3xl font-bold text-green-600">{opportunityStats.levelA}</p>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <p className="text-gray-600 text-sm mb-2">B 级（可行）</p>
                <p className="text-3xl font-bold text-blue-600">{opportunityStats.levelB}</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <p className="text-gray-600 text-sm mb-2">C 级（参考）</p>
                <p className="text-3xl font-bold text-yellow-600">{opportunityStats.levelC}</p>
              </div>
            </div>
          )}

          {/* Results */}
          {!isLoading && opportunities.length > 0 && (
            <div className="space-y-4">
              {opportunities.map((opportunity, index) => (
                <div key={index} className="bg-white rounded-lg shadow hover:shadow-lg p-6 transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getLevelColor(opportunity.level)}`}>
                          {getLevelBadge(opportunity.level)}
                        </span>
                        <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded">
                          评分: {opportunity.relevance_score.toFixed(1)}/10
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">
                        {opportunity.title}
                      </h3>
                      <a
                        href={opportunity.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:text-blue-700 text-sm font-medium break-all"
                      >
                        {truncateText(opportunity.url, 70)}
                      </a>
                    </div>
                    <div className="ml-4 flex-shrink-0 text-3xl">
                      🎯
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div>
                      <p className="text-gray-600 mb-1">
                        <strong>类型:</strong> {opportunity.opportunity_type}
                      </p>
                      <p className="text-gray-700 bg-gray-50 p-3 rounded">
                        <strong>建议:</strong> {opportunity.action}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t flex items-center justify-between text-xs text-gray-500">
                    <span>发现于 {formatDate(opportunity.timestamp)}</span>
                    <a
                      href={opportunity.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:text-blue-700 font-medium"
                    >
                      访问网站 →
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && opportunities.length === 0 && keyword && (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-600 text-lg">
                还没有扫描结果，请点击"开始扫描"按钮进行扫描
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
