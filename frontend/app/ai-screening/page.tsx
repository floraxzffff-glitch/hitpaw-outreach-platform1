/**
 * AI KOL 智能筛选页面
 * 功能点描述 → AI生成关键词 → 搜索候选频道 → 门槛过滤 → AI相关性判断 → AI适配度评分
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import LoadingSpinner from '../components/LoadingSpinner';
import vikpeaAPI, {
  type ScreeningKeyword,
  type ScreeningTaskStatus,
  type ScreeningExportResult,
  type ScreeningCandidate,
} from '@/lib/api/vikpea';

type TabKey = 'config' | 'run' | 'results';

const TABS: { key: TabKey; label: string }[] = [
  { key: 'config', label: '⚙️ 功能与关键词' },
  { key: 'run', label: '🚀 运行筛选' },
  { key: 'results', label: '📊 结果' },
];

const STATUS_LABELS: Record<string, string> = {
  idle: '待启动',
  generating_keywords: '生成关键词',
  searching_videos: '搜索视频',
  aggregating_channels: '聚合频道',
  filtering_thresholds: '门槛过滤',
  judging_relevance: 'AI相关性判断',
  fetching_channel_details: '拉取频道详情',
  scoring_fit: 'AI适配度评分',
  completed: '已完成',
  failed: '失败',
};

function toCSV(rows: ScreeningCandidate[]): string {
  const headers = ['频道名', '频道链接', '粉丝数', '近期均播', '命中视频数', '相关性', '适配度评分', '适配度判断', '判断理由', '建议角度'];
  const lines = [headers.join(',')];
  for (const c of rows) {
    const cells = [
      c.channel_name,
      c.channel_url,
      String(c.subscriber_count),
      String(c.recent_avg_views),
      String(c.matched_videos_count),
      c.relevance_verdict,
      String(c.fit_score),
      c.fit_verdict,
      c.fit_reason,
      c.suggested_angle,
    ];
    lines.push(cells.map((v) => `"${String(v ?? '').replace(/"/g, '""')}"`).join(','));
  }
  return lines.join('\n');
}

function downloadCSV(filename: string, rows: ScreeningCandidate[]) {
  const csv = '﻿' + toCSV(rows);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function AIScreeningPage() {
  const [tab, setTab] = useState<TabKey>('config');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 配置
  const [featureDescription, setFeatureDescription] = useState('');
  const [keywordCount, setKeywordCount] = useState(10);
  const [isGenerating, setIsGenerating] = useState(false);
  const [keywords, setKeywords] = useState<ScreeningKeyword[]>([]);
  const [customKeyword, setCustomKeyword] = useState('');

  // 运行参数
  const [maxResultsPerKeyword, setMaxResultsPerKeyword] = useState(50);
  const [minSubscribers, setMinSubscribers] = useState(1000);
  const [maxSubscribers, setMaxSubscribers] = useState(1000000);
  const [minVideoViews, setMinVideoViews] = useState(1000);
  const [minRecentAvgViews, setMinRecentAvgViews] = useState(500);

  // 任务状态
  const [task, setTask] = useState<ScreeningTaskStatus | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  // 结果
  const [exportResult, setExportResult] = useState<ScreeningExportResult | null>(null);
  const [resultView, setResultView] = useState<'recommended' | 'uncertain' | 'not_recommended'>('recommended');
  const [isLoadingResult, setIsLoadingResult] = useState(false);

  useEffect(() => {
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [task?.progress.length]);

  const enabledKeywords = keywords.filter((k) => k.enabled).map((k) => k.keyword);

  const handleGenerateKeywords = async () => {
    if (!featureDescription.trim()) {
      setError('请先填写功能点描述');
      return;
    }
    try {
      setIsGenerating(true);
      setError(null);
      const data = await vikpeaAPI.generateScreeningKeywords(featureDescription, keywordCount);
      setKeywords(data.keywords);
      setSuccess(`已生成 ${data.count} 个关键词`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || 'AI生成关键词失败');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleKeyword = (keyword: string) => {
    setKeywords((prev) =>
      prev.map((k) => (k.keyword === keyword ? { ...k, enabled: !k.enabled } : k))
    );
  };

  const handleRemoveKeyword = (keyword: string) => {
    setKeywords((prev) => prev.filter((k) => k.keyword !== keyword));
  };

  const handleAddCustomKeyword = () => {
    const kw = customKeyword.trim();
    if (!kw) return;
    if (keywords.some((k) => k.keyword === kw)) {
      setError('关键词已存在');
      return;
    }
    setKeywords((prev) => [...prev, { keyword: kw, enabled: true }]);
    setCustomKeyword('');
  };

  const pollTask = (taskId: string) => {
    if (pollTimer.current) clearInterval(pollTimer.current);
    pollTimer.current = setInterval(async () => {
      try {
        const data = await vikpeaAPI.getScreeningStatus(taskId);
        setTask(data);
        if (data.status === 'completed' || data.status === 'failed') {
          if (pollTimer.current) clearInterval(pollTimer.current);
          if (data.status === 'completed') {
            setSuccess('筛选完成！去"结果"标签查看');
            loadExportResult(taskId);
          } else {
            setError(data.error || '筛选任务失败');
          }
        }
      } catch (err: any) {
        if (pollTimer.current) clearInterval(pollTimer.current);
        setError(err.message || '查询筛选进度失败');
      }
    }, 3000);
  };

  const handleStartScreening = async () => {
    if (!featureDescription.trim()) {
      setError('请先填写功能点描述');
      return;
    }
    if (enabledKeywords.length === 0) {
      setError('请至少启用一个关键词');
      return;
    }
    try {
      setIsStarting(true);
      setError(null);
      setSuccess(null);
      setExportResult(null);
      const { task_id } = await vikpeaAPI.startScreeningRun(featureDescription, enabledKeywords, {
        max_results_per_keyword: maxResultsPerKeyword,
        min_subscribers: minSubscribers,
        max_subscribers: maxSubscribers,
        min_video_views: minVideoViews,
        min_recent_avg_views: minRecentAvgViews,
      });
      setTask({
        task_id,
        status: 'idle',
        progress: [],
        candidates: [],
        started_at: new Date().toISOString(),
      });
      setTab('run');
      pollTask(task_id);
    } catch (err: any) {
      setError(err.message || '启动筛选失败');
    } finally {
      setIsStarting(false);
    }
  };

  const loadExportResult = async (taskId: string) => {
    try {
      setIsLoadingResult(true);
      const data = await vikpeaAPI.exportScreeningResult(taskId);
      setExportResult(data);
    } catch (err: any) {
      setError(err.message || '加载结果失败');
    } finally {
      setIsLoadingResult(false);
    }
  };

  const isRunning = task && task.status !== 'completed' && task.status !== 'failed' && task.status !== 'idle';
  const currentResultRows = exportResult
    ? exportResult[resultView]
    : [];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-2 text-gray-800">🤖 AI KOL 智能筛选</h1>
      <p className="text-sm text-gray-500 mb-6">
        描述一个产品功能点，AI 生成差异化关键词，自动搜索、聚合频道、过滤门槛，再用 AI 判断相关性和适配度
      </p>

      {error && (
        <div className="mb-4">
          <ErrorAlert message={error} onDismiss={() => setError(null)} />
        </div>
      )}
      {success && (
        <div className="mb-4">
          <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />
        </div>
      )}

      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.key
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'config' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">功能点描述</h2>
            <textarea
              value={featureDescription}
              onChange={(e) => setFeatureDescription(e.target.value)}
              placeholder="例如：AI 视频画质增强、AI 视频降噪、AI 慢动作补帧..."
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm h-24 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <div className="flex items-center gap-3 mt-3">
              <label className="text-sm text-gray-600">生成数量</label>
              <input
                type="number"
                min={5}
                max={20}
                value={keywordCount}
                onChange={(e) => setKeywordCount(Number(e.target.value))}
                className="w-20 border border-gray-300 rounded px-2 py-1 text-sm"
              />
              <button
                onClick={handleGenerateKeywords}
                disabled={isGenerating}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 transition-colors text-sm"
              >
                {isGenerating ? '生成中...' : '✨ AI 生成关键词'}
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">
              关键词列表 <span className="text-sm text-gray-400">（{enabledKeywords.length} / {keywords.length} 已启用）</span>
            </h2>

            {keywords.length === 0 ? (
              <p className="text-sm text-gray-400">还没有关键词，先生成或手动添加</p>
            ) : (
              <div className="space-y-2 mb-4">
                {keywords.map((k) => (
                  <div
                    key={k.keyword}
                    className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded"
                  >
                    <label className="flex items-center gap-2 text-sm text-gray-700 flex-1">
                      <input
                        type="checkbox"
                        checked={k.enabled}
                        onChange={() => handleToggleKeyword(k.keyword)}
                      />
                      {k.keyword}
                    </label>
                    <button
                      onClick={() => handleRemoveKeyword(k.keyword)}
                      className="text-gray-400 hover:text-red-500 text-sm ml-2"
                    >
                      删除
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                value={customKeyword}
                onChange={(e) => setCustomKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddCustomKeyword()}
                placeholder="手动添加关键词"
                className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <button
                onClick={handleAddCustomKeyword}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors text-sm"
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}

      {tab === 'run' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">筛选参数</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">每个关键词取多少结果</label>
                <input
                  type="number"
                  value={maxResultsPerKeyword}
                  onChange={(e) => setMaxResultsPerKeyword(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">最少粉丝数</label>
                <input
                  type="number"
                  value={minSubscribers}
                  onChange={(e) => setMinSubscribers(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">最多粉丝数</label>
                <input
                  type="number"
                  value={maxSubscribers}
                  onChange={(e) => setMaxSubscribers(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">命中视频最低播放量</label>
                <input
                  type="number"
                  value={minVideoViews}
                  onChange={(e) => setMinVideoViews(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">近期均播门槛</label>
                <input
                  type="number"
                  value={minRecentAvgViews}
                  onChange={(e) => setMinRecentAvgViews(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                />
              </div>
            </div>

            <button
              onClick={handleStartScreening}
              disabled={isStarting || !!isRunning}
              className="mt-6 w-full px-4 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 transition-colors font-medium"
            >
              {isRunning ? '筛选进行中...' : isStarting ? '启动中...' : '🚀 开始筛选'}
            </button>
          </div>

          {task && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">运行进度</h2>
                <span
                  className={`text-sm px-3 py-1 rounded-full ${
                    task.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : task.status === 'failed'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}
                >
                  {STATUS_LABELS[task.status] || task.status}
                </span>
              </div>
              <div className="bg-gray-50 rounded p-4 max-h-80 overflow-auto text-sm space-y-1">
                {task.progress.length === 0 && <p className="text-gray-400">等待任务开始...</p>}
                {task.progress.map((p, idx) => (
                  <div key={idx} className="text-gray-700">
                    <span className="text-gray-400 mr-2">[{STATUS_LABELS[p.status] || p.status}]</span>
                    {p.message}
                    {p.total > 0 && (
                      <span className="text-gray-400 ml-1">
                        ({p.current}/{p.total})
                      </span>
                    )}
                  </div>
                ))}
                <div ref={logEndRef} />
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'results' && (
        <div className="space-y-6">
          {!task && <p className="text-sm text-gray-400">还没有运行过筛选任务</p>}

          {task && task.status !== 'completed' && (
            <p className="text-sm text-gray-400">任务还未完成，先去"运行筛选"看看进度</p>
          )}

          {isLoadingResult && <LoadingSpinner />}

          {exportResult && !isLoadingResult && (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">
                    共 {exportResult.total} 个候选频道
                  </h2>
                  <button
                    onClick={() => downloadCSV(`AI筛选结果_${resultView}.csv`, currentResultRows)}
                    disabled={currentResultRows.length === 0}
                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 transition-colors text-sm"
                  >
                    📥 导出当前分类为 CSV
                  </button>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => setResultView('recommended')}
                    className={`px-4 py-2 rounded text-sm ${
                      resultView === 'recommended' ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    ✅ 推荐 ({exportResult.recommended.length})
                  </button>
                  <button
                    onClick={() => setResultView('uncertain')}
                    className={`px-4 py-2 rounded text-sm ${
                      resultView === 'uncertain' ? 'bg-yellow-500 text-white' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    🤔 待确认 ({exportResult.uncertain.length})
                  </button>
                  <button
                    onClick={() => setResultView('not_recommended')}
                    className={`px-4 py-2 rounded text-sm ${
                      resultView === 'not_recommended' ? 'bg-gray-500 text-white' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    ❌ 不推荐 ({exportResult.not_recommended.length})
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {currentResultRows.length === 0 && (
                  <p className="text-sm text-gray-400">这个分类下没有候选</p>
                )}
                {currentResultRows.map((c) => (
                  <div key={c.channel_id} className="bg-white rounded-lg shadow p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <a
                          href={c.channel_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 font-medium hover:underline"
                        >
                          {c.channel_name}
                        </a>
                        <p className="text-sm text-gray-500 mt-1">
                          粉丝 {c.subscriber_count.toLocaleString()} · 近期均播{' '}
                          {c.recent_avg_views.toLocaleString()} · 命中 {c.matched_videos_count} 个视频
                        </p>
                      </div>
                      <span className="text-sm font-semibold text-gray-700">
                        适配度 {c.fit_score}
                      </span>
                    </div>
                    {c.fit_reason && (
                      <p className="text-sm text-gray-600 mt-2">{c.fit_reason}</p>
                    )}
                    {c.suggested_angle && (
                      <p className="text-sm text-blue-500 mt-1">💡 {c.suggested_angle}</p>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
