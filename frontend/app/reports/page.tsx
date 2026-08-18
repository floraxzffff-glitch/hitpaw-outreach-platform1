/**
 * 报告页面
 */

'use client';

import { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type ReportResponse } from '@/lib/api/vikpea';
import { formatDate } from '@/lib/utils/helpers';

export default function ReportsPage() {
  const [reportType, setReportType] = useState<'keyword_review' | 'seo_analysis' | 'email_validation'>('keyword_review');
  const [reports, setReports] = useState<ReportResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load reports
  useEffect(() => {
    const loadReports = async () => {
      try {
        setIsLoading(true);
        const data = await vikpeaAPI.listReports();
        setReports(data.reports);
      } catch (err: any) {
        setError(err.message || '加载报告失败');
      } finally {
        setIsLoading(false);
      }
    };

    loadReports();
  }, []);

  const handleGenerateReport = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      
      const report = await vikpeaAPI.generateReport(reportType, true);
      setReports([report, ...reports]);
      setSuccess('报告已生成！');
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '生成报告失败');
    } finally {
      setIsGenerating(false);
    }
  };

  const reportTypeLabels = {
    keyword_review: '关键词复盘',
    seo_analysis: 'SEO 分析',
    email_validation: '邮箱验证',
  };

  const reportTypeEmojis = {
    keyword_review: '📊',
    seo_analysis: '🔍',
    email_validation: '✉️',
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📄 生成报告</h1>
            <p className="text-gray-600">
              生成详细的分析报告，帮助您做出更好的决策
            </p>
          </div>

          {/* Error and Success Alerts */}
          <div className="space-y-4 mb-8">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && (
              <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />
            )}
          </div>

          {/* Generate Report Section */}
          <div className="bg-white rounded-lg shadow p-8 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">新建报告</h2>

            <div className="space-y-6">
              <div>
                <label htmlFor="reportType" className="block text-sm font-medium text-gray-700 mb-4">
                  报告类型
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {(Object.entries(reportTypeLabels) as [keyof typeof reportTypeLabels, string][]).map(
                    ([type, label]) => (
                      <label key={type} className="relative flex cursor-pointer">
                        <input
                          type="radio"
                          name="reportType"
                          value={type}
                          checked={reportType === type}
                          onChange={() => setReportType(type)}
                          disabled={isGenerating}
                          className="sr-only"
                        />
                        <div
                          className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                            reportType === type
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 bg-white hover:border-gray-300'
                          }`}
                        >
                          <p className="text-2xl mb-2">{reportTypeEmojis[type]}</p>
                          <p className="font-semibold text-gray-900">{label}</p>
                        </div>
                      </label>
                    )
                  )}
                </div>
              </div>

              <button
                onClick={handleGenerateReport}
                disabled={isGenerating}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isGenerating ? '生成中...' : '生成报告'}
              </button>
            </div>
          </div>

          {/* Reports List */}
          <div className="bg-white rounded-lg shadow p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">最近报告</h2>

            {isLoading ? (
              <LoadingSpinner />
            ) : reports.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-600 text-lg mb-4">还没有生成过报告</p>
                <p className="text-gray-500">点击上面的"生成报告"按钮来创建您的第一个报告</p>
              </div>
            ) : (
              <div className="space-y-4">
                {reports.map((report) => (
                  <div
                    key={report.report_id}
                    className="flex items-start justify-between p-6 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md transition-all"
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-2xl">
                          {reportTypeEmojis[report.report_type as keyof typeof reportTypeEmojis]}
                        </span>
                        <div>
                          <h3 className="text-lg font-bold text-gray-900">
                            {report.title}
                          </h3>
                          <p className="text-sm text-gray-600">
                            ID: {report.report_id}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-gray-500">
                        生成于 {formatDate(report.generated_at)}
                      </p>
                    </div>

                    <div className="ml-4 flex-shrink-0">
                      {report.file_url ? (
                        <a
                          href={report.file_url}
                          download
                          className="inline-block px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium transition-colors"
                        >
                          下载
                        </a>
                      ) : (
                        <div className="inline-block px-4 py-2 bg-gray-100 text-gray-600 rounded-lg font-medium">
                          准备中...
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
  );
}
