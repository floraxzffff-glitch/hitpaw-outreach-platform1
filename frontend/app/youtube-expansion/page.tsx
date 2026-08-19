/**
 * YouTube 关键词拓展+搜索页面
 * 使用 YouTube Data API v3 + DataForSEO 进行关键词拓展和视频搜索
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';

type TabKey = 'config' | 'run' | 'results';

const TABS: { key: TabKey; label: string }[] = [
  { key: 'config', label: '⚙️ 配置' },
  { key: 'run', label: '🚀 运行' },
  { key: 'results', label: '📊 结果' },
];

export default function YoutubeExpansionPage() {
  const [tab, setTab] = useState<TabKey>('config');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 配置
  const [seedKeywords, setSeedKeywords] = useState<string>('');
  const [vphThreshold, setVphThreshold] = useState<number>(20);
  const [maxKeywords, setMaxKeywords] = useState<number>(50);
  const [outputFile, setOutputFile] = useState<string>('results.xlsx');
  const [depth, setDepth] = useState<number>(1);
  const [skipExpansion, setSkipExpansion] = useState<boolean>(false);

  // 运行状态
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [log, setLog] = useState<string[]>([]);
  const [progress, setProgress] = useState<string>('');
  const logEndRef = useRef<HTMLDivElement>(null);

  // 结果
  const [resultFile, setResultFile] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log.length]);

  const handleStart = async () => {
    const seeds = seedKeywords.split('\n').map(s => s.trim()).filter(Boolean);
    if (seeds.length === 0) {
      setError('请至少输入一个种子关键词');
      return;
    }

    try {
      setError(null);
      setSuccess(null);
      setIsRunning(true);
      setLog([]);
      setProgress('正在启动...');

      // 构建命令参数
      const args = [
        ...seeds.flatMap(s => ['--seed', s]),
        '--vph-threshold', String(vphThreshold),
        '--max-keywords', String(maxKeywords),
        '--output', outputFile,
        '--depth', String(depth),
      ];

      if (skipExpansion) {
        args.push('--skip-expansion');
      }

      setLog([
        `🚀 启动 YouTube 关键词拓展+搜索工具`,
        `📝 种子关键词: ${seeds.join(', ')}`,
        `📊 VPH阈值: ${vphThreshold}`,
        `🔢 最大关键词数: ${maxKeywords}`,
        `📁 输出文件: ${outputFile}`,
        skipExpansion ? '⚠️  跳过关键词拓展' : `🌐 拓展深度: ${depth}`,
        '',
        '正在调用后端API...',
      ]);

      // 调用后端API启动任务
      const API_BASE = window.location.origin;
      const response = await fetch(`${API_BASE}/api/youtube/expansion/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          seed_keywords: seeds,
          vph_threshold: vphThreshold,
          max_keywords: maxKeywords,
          depth: depth,
          skip_expansion: skipExpansion,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '启动失败');
      }

      const { job_id } = await response.json();
      setLog(prev => [...prev, `✓ 任务已启动 (ID: ${job_id})`, '', '等待执行结果...']);

      // 轮询任务状态
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`${API_BASE}/api/youtube/search/jobs/${job_id}`);
          if (!statusResponse.ok) return;

          const jobData = await statusResponse.json();

          // 更新日志
          if (jobData.log && jobData.log.length > 0) {
            setLog(jobData.log);
          }

          // 检查任务状态
          if (jobData.status === 'completed') {
            clearInterval(pollInterval);
            setLog(prev => [...prev, '', '✅ 工具运行完成']);
            setSuccess(`搜索完成！结果已保存`);
            setResultFile(outputFile);
            setIsRunning(false);
            setTab('results');
          } else if (jobData.status === 'failed') {
            clearInterval(pollInterval);
            setError(jobData.error || '任务失败');
            setIsRunning(false);
          }
        } catch (err) {
          console.error('轮询任务状态失败:', err);
        }
      }, 2000);

      // 5分钟后自动停止轮询
      setTimeout(() => clearInterval(pollInterval), 300000);

    } catch (err: any) {
      setError(err.message || '运行失败');
      setIsRunning(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎯 YouTube 关键词拓展+视频搜索
          </h1>
          <p className="text-gray-600">
            使用 YouTube Data API v3 进行视频搜索，可选 DataForSEO 进行关键词拓展
          </p>
        </div>

        <div className="space-y-4 mb-6">
          {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
          {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 border-b border-gray-200">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors ${
                tab === t.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* 配置 */}
        {tab === 'config' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">运行配置</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  种子关键词 *
                </label>
                <textarea
                  value={seedKeywords}
                  onChange={(e) => setSeedKeywords(e.target.value)}
                  placeholder={'一行一个，例如：\nAI video enhancer\nvideo upscaler\n4k upscaling'}
                  rows={6}
                  disabled={isRunning}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
                <p className="text-xs text-gray-500 mt-1">
                  每个种子词会拓展出更多相关关键词，然后搜索所有关键词
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    VPH 阈值
                  </label>
                  <input
                    type="number"
                    value={vphThreshold}
                    onChange={(e) => setVphThreshold(Number(e.target.value))}
                    disabled={isRunning}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    VPH = 观看数/发布小时数，用于过滤低质量视频
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    最大关键词数
                  </label>
                  <input
                    type="number"
                    value={maxKeywords}
                    onChange={(e) => setMaxKeywords(Number(e.target.value))}
                    disabled={isRunning}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    拓展后最多搜索多少个关键词
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    输出文件名
                  </label>
                  <input
                    type="text"
                    value={outputFile}
                    onChange={(e) => setOutputFile(e.target.value)}
                    disabled={isRunning}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    DataForSEO 拓展深度
                  </label>
                  <select
                    value={depth}
                    onChange={(e) => setDepth(Number(e.target.value))}
                    disabled={isRunning || skipExpansion}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  >
                    <option value={1}>1 (推荐)</option>
                    <option value={2}>2</option>
                    <option value={3}>3 (最深)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="skip-expansion"
                  checked={skipExpansion}
                  onChange={(e) => setSkipExpansion(e.target.checked)}
                  disabled={isRunning}
                  className="w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="skip-expansion" className="ml-2 text-sm text-gray-700">
                  跳过关键词拓展，只搜索种子词
                </label>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 使用提示</h3>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• YouTube API 配额：10,000 units/天，约可搜索 90-100 个关键词</li>
                <li>• DataForSEO 可选，不配置也能用 YouTube 自动补全拓展</li>
                <li>• 配额用完会自动保存进度，第二天可以用 --resume 继续</li>
                <li>• 结果包含两个表：按视频维度 + 按频道汇总</li>
              </ul>
            </div>
          </div>
        )}

        {/* 运行 */}
        {tab === 'run' && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">运行状态</h2>
              <button
                onClick={handleStart}
                disabled={isRunning}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-6 rounded-lg transition-all"
              >
                {isRunning ? '运行中...' : '🚀 开始运行'}
              </button>
            </div>

            {progress && (
              <div className="mb-4">
                <p className="text-sm text-gray-700">{progress}</p>
              </div>
            )}

            <div className="bg-gray-900 text-gray-100 font-mono text-xs rounded-lg p-4 max-h-96 overflow-y-auto">
              {log.length === 0 ? (
                <p className="text-gray-500">点击"开始运行"启动工具...</p>
              ) : (
                log.map((line, i) => <div key={i}>{line}</div>)
              )}
              <div ref={logEndRef} />
            </div>
          </div>
        )}

        {/* 结果 */}
        {tab === 'results' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">搜索结果</h2>

            {!resultFile ? (
              <p className="text-gray-500 text-sm py-8 text-center">
                还没有结果，先在"运行"标签页启动搜索
              </p>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm font-semibold text-green-900 mb-2">
                    ✅ 搜索完成
                  </p>
                  <p className="text-sm text-green-800">
                    结果已保存到: <span className="font-mono">{resultFile}</span>
                  </p>
                </div>

                {stats && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">视频数</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.total_videos}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">频道数</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.total_channels}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">VPH 范围</p>
                      <p className="text-lg font-bold text-gray-900">{stats.vph_range}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">平均 VPH</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.avg_vph}</p>
                    </div>
                  </div>
                )}

                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-sm font-semibold text-blue-900 mb-2">📁 文件说明</h3>
                  <p className="text-xs text-blue-800">
                    Excel 文件包含两个工作表：
                  </p>
                  <ul className="text-xs text-blue-800 mt-2 space-y-1 ml-4">
                    <li>• Sheet 1: 按视频维度 - 所有符合条件的视频详情</li>
                    <li>• Sheet 2: 按频道汇总 - 每个频道的统计信息</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
