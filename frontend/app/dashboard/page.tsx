/**
 * 仪表板页面 - 应用首页
 */

'use client';

import { useEffect, useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import StatsCard from '../components/StatsCard';
import Link from 'next/link';
import vikpeaAPI, { type StatsResponse, type HealthCheckResponse } from '@/lib/api/vikpea';

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const [statsData, healthData] = await Promise.all([
          vikpeaAPI.getStats(),
          vikpeaAPI.healthCheck(),
        ]);
        
        setStats(statsData);
        setHealth(healthData);
      } catch (err: any) {
        setError(err.message || '无法连接到服务器');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const features = [
    {
      icon: '🎥',
      title: 'YouTube KOL 搜索',
      description: '真实跑 yt-dlp 抓取 YouTube 博主并找邮箱',
      href: '/youtube',
    },
    {
      icon: '🔍',
      title: '关键词分析',
      description: '分析关键词的搜索潜力和邮箱发现率',
      href: '/analyze',
    },
    {
      icon: '✉️',
      title: '邮箱验证',
      description: '验证邮箱地址的有效性和可信度',
      href: '/email',
    },
    {
      icon: '🔎',
      title: 'SEO 机会扫描',
      description: '发现高价值的 SEO 发展机会',
      href: '/seo',
    },
    {
      icon: '📄',
      title: '报告生成',
      description: '生成详细的分析和统计报告',
      href: '/reports',
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-4xl font-bold mb-4">欢迎使用 VikPea</h1>
            <p className="text-xl text-blue-100">
              强大的 SEO 和邮箱开发自动化平台
            </p>
            <p className="text-blue-200 mt-2">
              {health?.status === 'healthy' ? (
                <span>✓ 服务正常运行</span>
              ) : (
                <span>⚠️ 服务连接中...</span>
              )}
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Error Alert */}
          {error && (
            <ErrorAlert
              message={error}
              onDismiss={() => setError(null)}
            />
          )}

          {/* Statistics */}
          {isLoading ? (
            <LoadingSpinner />
          ) : stats ? (
            <>
              <div className="mb-12">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  📊 统计数据
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatsCard
                    label="分析过的关键词"
                    value={stats.total_keywords_analyzed}
                    icon="🔍"
                    color="blue"
                    subtext="累计分析"
                  />
                  <StatsCard
                    label="验证过的邮箱"
                    value={stats.total_emails_validated}
                    icon="✉️"
                    color="green"
                    subtext="累计验证"
                  />
                  <StatsCard
                    label="发现的机会"
                    value={stats.total_opportunities_found}
                    icon="🎯"
                    color="purple"
                    subtext="累计发现"
                  />
                  <StatsCard
                    label="今日活动"
                    value={
                      stats.today_activities.keywords_analyzed +
                      stats.today_activities.emails_validated
                    }
                    icon="📈"
                    color="orange"
                    subtext="今天"
                  />
                </div>
              </div>

              {/* Today Activity */}
              <div className="mb-12 bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">📅 今日活动</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-gray-600 text-sm mb-2">分析关键词</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {stats.today_activities.keywords_analyzed}
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-gray-600 text-sm mb-2">验证邮箱</p>
                    <p className="text-2xl font-bold text-green-600">
                      {stats.today_activities.emails_validated}
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <p className="text-gray-600 text-sm mb-2">发现机会</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {stats.today_activities.opportunities_found}
                    </p>
                  </div>
                </div>
              </div>
            </>
          ) : null}

          {/* Features */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">⚡ 主要功能</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature) => (
                <Link
                  key={feature.href}
                  href={feature.href}
                  className="bg-white rounded-lg shadow hover:shadow-lg p-6 transition-shadow group"
                >
                  <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    {feature.description}
                  </p>
                  <span className="inline-block px-4 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium group-hover:bg-blue-100 transition-colors">
                    开始使用 →
                  </span>
                </Link>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">💡 快速入门</h3>
            <ul className="space-y-3 text-gray-700">
              <li>
                <strong>1. 分析关键词</strong> - 输入关键词，系统自动分析搜索潜力
              </li>
              <li>
                <strong>2. 验证邮箱</strong> - 检查邮箱有效性，清理垃圾邮箱
              </li>
              <li>
                <strong>3. 扫描 SEO 机会</strong> - 发现高价值的邮箱开发目标
              </li>
              <li>
                <strong>4. 生成报告</strong> - 导出详细的分析报告用于决策
              </li>
            </ul>
          </div>
        </div>
      </main>
  );
}
