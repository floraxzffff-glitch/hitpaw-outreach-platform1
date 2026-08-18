/**
 * YouTube KOL 搜索页面
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, {
  type YoutubeKeyword,
  type YoutubeSearchJob,
  type YoutubeSearchSettings,
} from '@/lib/api/vikpea';

const SETTINGS_FIELDS: { key: keyof YoutubeSearchSettings; label: string; hint: string }[] = [
  { key: 'YOUTUBE_SUB_MIN', label: '最少粉丝数', hint: '低于这个数的频道不要' },
  { key: 'YOUTUBE_SUB_MAX', label: '最多粉丝数', hint: '高于这个数的频道不要（太大的号不好谈）' },
  { key: 'YOUTUBE_RESULTS_PER_KEYWORD', label: '每个关键词取多少结果', hint: '越大越慢，候选越多' },
  { key: 'YOUTUBE_MIN_VIDEO_VIEWS', label: '单条视频最低播放量', hint: '常规视频门槛' },
  { key: 'YOUTUBE_MIN_SHORTS_VIEWS', label: 'Shorts 最低播放量', hint: '短视频门槛' },
  { key: 'YOUTUBE_MIN_RECENT_AVG_VIEWS', label: '近期均播门槛', hint: '配合下面"近期视频数"一起看' },
  { key: 'YOUTUBE_RECENT_VIDEO_COUNT', label: '近期视频数', hint: '算均播时看最近几条' },
  { key: 'YOUTUBE_ACTIVE_WITHIN_DAYS', label: '活跃天数', hint: '最近多少天内发过视频才算活跃' },
  { key: 'YOUTUBE_MARKET_SCORE_MIN', label: '市场信号最低分', hint: '越高越严格' },
];

type TabKey = 'keywords' | 'settings' | 'candidates';

const TABS: { key: TabKey; label: string }[] = [
  { key: 'keywords', label: '🔑 关键词' },
  { key: 'settings', label: '⚙️ 筛选参数' },
  { key: 'candidates', label: '📋 候选库' },
];

export default function YoutubePage() {
  const [tab, setTab] = useState<TabKey>('keywords');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 关键词
  const [keywords, setKeywords] = useState<YoutubeKeyword[]>([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [isLoadingKeywords, setIsLoadingKeywords] = useState(true);
  const [showBulkAdd, setShowBulkAdd] = useState(false);
  const [bulkText, setBulkText] = useState('');

  // 筛选参数
  const [settings, setSettings] = useState<YoutubeSearchSettings | null>(null);
  const [settingsDraft, setSettingsDraft] = useState<Record<string, string>>({});
  const [isSavingSettings, setIsSavingSettings] = useState(false);

  // 候选库
  const [confirmed, setConfirmed] = useState<Record<string, any>[]>([]);
  const [pending, setPending] = useState<Record<string, any>[]>([]);
  const [noEmail, setNoEmail] = useState<Record<string, any>[]>([]);
  const [isLoadingCandidates, setIsLoadingCandidates] = useState(true);
  const [candidateView, setCandidateView] = useState<'confirmed' | 'pending' | 'no_email'>('confirmed');
  const [selectedForSend, setSelectedForSend] = useState<Set<number>>(new Set());
  const emptyCandidateForm = { 频道名: '', 邮箱: '', 主页链接: '', 视频链接: '', 备注: '', 类型: 'YouTube', 来源关键词: '', 频道标签: '' };
  const [candidateForm, setCandidateForm] = useState(emptyCandidateForm);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingRownum, setEditingRownum] = useState<number | null>(null);
  const [isSavingCandidate, setIsSavingCandidate] = useState(false);

  // 运行任务
  const [job, setJob] = useState<YoutubeSearchJob | null>(null);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  const loadKeywords = async () => {
    try {
      setIsLoadingKeywords(true);
      const data = await vikpeaAPI.listYoutubeKeywords();
      setKeywords(data.keywords);
    } catch (err: any) {
      setError(err.message || '加载关键词失败');
    } finally {
      setIsLoadingKeywords(false);
    }
  };

  const loadSettings = async () => {
    try {
      const data = await vikpeaAPI.getYoutubeSettings();
      setSettings(data);
      const draft: Record<string, string> = {};
      SETTINGS_FIELDS.forEach((f) => {
        draft[f.key] = String(data[f.key]);
      });
      setSettingsDraft(draft);
    } catch (err: any) {
      setError(err.message || '加载搜索参数失败');
    }
  };

  const loadCandidates = async () => {
    try {
      setIsLoadingCandidates(true);
      const data = await vikpeaAPI.getKolCandidates();
      setConfirmed(data.confirmed);
      setPending(data.pending);
      setNoEmail(data.no_email || []);
      // 默认全选可发信候选
      const allConfirmedIndices = new Set(data.confirmed.map((_: any, idx: number) => idx));
      setSelectedForSend(allConfirmedIndices);
    } catch (err: any) {
      setError(err.message || '加载候选库失败');
    } finally {
      setIsLoadingCandidates(false);
    }
  };

  const openAddForm = () => {
    setCandidateForm(emptyCandidateForm);
    setEditingRownum(null);
    setShowAddForm(true);
  };

  const openEditForm = (row: Record<string, any>) => {
    setCandidateForm({
      频道名: row['频道名'] || '',
      邮箱: row['邮箱'] || '',
      主页链接: row['主页链接'] || '',
      视频链接: row['视频链接'] || '',
      备注: row['备注'] || '',
      类型: row['类型'] || 'YouTube',
      来源关键词: row['来源关键词'] || '',
      频道标签: row['频道标签'] || '',
    });
    setEditingRownum(row['_rownum']);
    setShowAddForm(true);
  };

  const handleSaveCandidate = async () => {
    if (!candidateForm.频道名.trim() || !candidateForm.邮箱.trim()) {
      setError('频道名和邮箱必填');
      return;
    }
    try {
      setIsSavingCandidate(true);
      setError(null);
      const data = editingRownum
        ? await vikpeaAPI.updateConfirmedCandidate(editingRownum, candidateForm)
        : await vikpeaAPI.addConfirmedCandidate(candidateForm);
      setConfirmed(data.candidates);
      setShowAddForm(false);
      setCandidateForm(emptyCandidateForm);
      setEditingRownum(null);
      setSuccess(editingRownum ? '已更新' : '已添加');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setIsSavingCandidate(false);
    }
  };

  const handleDeleteCandidate = async (rownum: number, name: string) => {
    const ok = window.confirm(`删除「${name}」？`);
    if (!ok) return;
    try {
      setError(null);
      const data = await vikpeaAPI.deleteConfirmedCandidate(rownum);
      setConfirmed(data.candidates);
    } catch (err: any) {
      setError(err.message || '删除失败');
    }
  };

  const resumeIfRunning = async () => {
    try {
      const { jobs } = await vikpeaAPI.listYoutubeSearchJobs();
      const active = jobs.find((j) => j.status === 'running' || j.status === 'stopping');
      if (active) {
        setJob(active);
        pollJob(active.job_id);
      }
    } catch {
      // 找不到就算了，不影响页面其他部分
    }
  };

  useEffect(() => {
    loadKeywords();
    loadSettings();
    loadCandidates();
    resumeIfRunning();
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [job?.log.length]);

  const handleSaveSettings = async () => {
    try {
      setIsSavingSettings(true);
      setError(null);
      const updates: Record<string, number> = {};
      SETTINGS_FIELDS.forEach((f) => {
        const n = parseInt(settingsDraft[f.key], 10);
        if (!Number.isNaN(n)) updates[f.key] = n;
      });
      const data = await vikpeaAPI.updateYoutubeSettings(updates);
      setSettings(data);
      setSuccess('搜索参数已保存（真实写入 VikPea_配置.xlsx，桌面版也会用新参数）');
      setTimeout(() => setSuccess(null), 4000);
    } catch (err: any) {
      setError(err.message || '保存参数失败');
    } finally {
      setIsSavingSettings(false);
    }
  };

  const handleToggle = async (keyword: string, enabled: boolean) => {
    try {
      setError(null);
      const data = await vikpeaAPI.toggleYoutubeKeyword(keyword, enabled);
      setKeywords(data.keywords);
    } catch (err: any) {
      setError(err.message || '更新关键词失败');
    }
  };

  const handleDeleteKeyword = async (keyword: string) => {
    const ok = window.confirm(`删除关键词「${keyword}」？`);
    if (!ok) return;
    try {
      setError(null);
      const data = await vikpeaAPI.deleteYoutubeKeyword(keyword);
      setKeywords(data.keywords);
    } catch (err: any) {
      setError(err.message || '删除关键词失败');
    }
  };

  const handleAddKeyword = async () => {
    const trimmed = newKeyword.trim();
    if (!trimmed) {
      setError('请输入关键词');
      return;
    }
    try {
      setError(null);
      const data = await vikpeaAPI.toggleYoutubeKeyword(trimmed, true);
      setKeywords(data.keywords);
      setNewKeyword('');
      setSuccess(`已添加并启用「${trimmed}」`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '添加关键词失败');
    }
  };

  const addKeywordsBatch = async (items: string[]) => {
    const cleaned = items.map((s) => s.trim()).filter(Boolean);
    if (cleaned.length === 0) return;
    try {
      setError(null);
      const data = await vikpeaAPI.addYoutubeKeywordsBatch(cleaned);
      setKeywords(data.keywords);
      setNewKeyword('');
      setSuccess(`已添加 ${data.added} 个新关键词${data.updated ? `，更新 ${data.updated} 个已有的` : ''}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '批量添加失败');
    }
  };

  const bulkLines = bulkText.split('\n').map((s) => s.trim()).filter(Boolean);

  const handleBulkAdd = async () => {
    if (bulkLines.length === 0) {
      setError('文本框里一行都没有');
      return;
    }
    await addKeywordsBatch(bulkLines);
    setBulkText('');
    setShowBulkAdd(false);
  };

  const handleKeywordPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const text = e.clipboardData.getData('text');
    // Excel 整列/多行复制过来是换行或制表符分隔的；这种情况直接拆成多个关键词，
    // 不能按普通粘贴处理（普通输入框会把换行吞掉，导致所有词粘成一长串）。
    if (/[\n\r\t]/.test(text)) {
      e.preventDefault();
      const items = text.split(/[\n\r\t]+/);
      addKeywordsBatch(items);
    }
  };

  const pollJob = (jobId: string) => {
    if (pollTimer.current) clearInterval(pollTimer.current);
    pollTimer.current = setInterval(async () => {
      try {
        const data = await vikpeaAPI.getYoutubeSearchJob(jobId);
        setJob(data);
        if (data.status !== 'running' && data.status !== 'stopping') {
          if (pollTimer.current) clearInterval(pollTimer.current);
          if (data.status === 'completed') {
            setSuccess('搜索任务已完成！结果已经在候选库里了');
          } else if (data.status === 'stopped') {
            setSuccess('已停止');
          } else {
            setError(data.error || '任务失败');
          }
          loadKeywords();
          loadCandidates();
        }
      } catch (err: any) {
        if (pollTimer.current) clearInterval(pollTimer.current);
        setError(err.message || '查询任务状态失败');
      }
    }, 2000);
  };

  const handleStart = async () => {
    try {
      setError(null);
      setSuccess(null);
      const { job_id } = await vikpeaAPI.startYoutubeSearch();
      setJob({
        job_id,
        resource: 'youtube_search',
        label: '',
        status: 'running',
        log: [],
        started_at: new Date().toISOString(),
      });
      pollJob(job_id);
    } catch (err: any) {
      setError(err.message || '启动搜索失败');
    }
  };

  const handleStop = async () => {
    if (!job) return;
    const ok = window.confirm('确认要停止当前搜索吗？已经跑完的部分不会丢，但不会继续往下搜了。');
    if (!ok) return;
    try {
      await vikpeaAPI.stopYoutubeSearchJob(job.job_id);
      setJob({ ...job, status: 'stopping' });
    } catch (err: any) {
      setError(err.message || '停止失败');
    }
  };

  const enabledCount = keywords.filter((k) => k.enabled).length;
  const isRunning = job?.status === 'running' || job?.status === 'stopping';
  const candidateRows = candidateView === 'confirmed' ? confirmed : candidateView === 'pending' ? pending : noEmail;

  return (
    <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">🎥 YouTube KOL 搜索</h1>
            <p className="text-gray-600">
              跑的是真实的 VikPea_YouTube批量搜索.py —— 会用 yt-dlp 真实抓取 YouTube、真实写入
              VikPea_发信名单.xlsx / VikPea_待确认邮箱.xlsx，跟桌面工作台点第 2 项是同一件事。
            </p>
          </div>

          <div className="space-y-4 mb-6">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
          </div>

          {/* 常驻：开始搜索 + 状态 */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <h2 className="text-lg font-bold text-gray-900">开始搜索</h2>
                <p className="text-sm text-gray-500">已启用 {enabledCount} 个关键词</p>
              </div>
              <div className="flex gap-2">
                {isRunning && job?.stoppable !== false && (
                  <button
                    onClick={handleStop}
                    disabled={job?.status === 'stopping'}
                    className="bg-gray-700 hover:bg-gray-800 disabled:opacity-50 text-white font-semibold py-2.5 px-5 rounded-lg transition-all whitespace-nowrap"
                  >
                    {job?.status === 'stopping' ? '停止中...' : '⏹ 停止'}
                  </button>
                )}
                <button
                  onClick={handleStart}
                  disabled={isRunning || enabledCount === 0}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-6 rounded-lg transition-all whitespace-nowrap"
                >
                  {isRunning ? '搜索进行中...' : '🚀 开始真实搜索'}
                </button>
              </div>
            </div>
            {job && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">运行日志</span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      job.status === 'running'
                        ? 'bg-blue-100 text-blue-700'
                        : job.status === 'stopping'
                        ? 'bg-yellow-100 text-yellow-700'
                        : job.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : job.status === 'stopped'
                        ? 'bg-gray-200 text-gray-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {job.status === 'running'
                      ? '进行中'
                      : job.status === 'stopping'
                      ? '停止中'
                      : job.status === 'completed'
                      ? '已完成'
                      : job.status === 'stopped'
                      ? '已停止'
                      : '失败'}
                  </span>
                </div>
                <div className="bg-gray-900 text-gray-100 font-mono text-xs rounded-lg p-4 max-h-64 overflow-y-auto">
                  {job.log.length === 0 ? (
                    <p className="text-gray-500">等待脚本输出...</p>
                  ) : (
                    job.log.map((line, i) => <div key={i}>{line}</div>)
                  )}
                  <div ref={logEndRef} />
                </div>
              </div>
            )}
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

          {/* 关键词管理 */}
          {tab === 'keywords' && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-lg font-bold text-gray-900">关键词</h2>
                <button
                  onClick={() => setShowBulkAdd(!showBulkAdd)}
                  className="text-xs text-blue-500 hover:text-blue-700 font-medium"
                >
                  {showBulkAdd ? '切换回单个添加' : '📋 批量粘贴（一行一个）'}
                </button>
              </div>
              <p className="text-xs text-gray-500 mb-4">来自 VikPea_搜索关键词.xlsx</p>

              {showBulkAdd ? (
                <div className="mb-4">
                  <textarea
                    value={bulkText}
                    onChange={(e) => setBulkText(e.target.value)}
                    placeholder={'一行一个关键词，比如从 Excel 一列复制过来直接粘贴：\nvideo upscaler mac\nhitpaw coupon code\nvideo quality enhancer'}
                    rows={6}
                    disabled={isRunning}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                  <div className="flex items-center justify-between mt-2">
                    <p className="text-xs text-gray-500">
                      识别到 {bulkLines.length} 行{bulkLines.length > 0 && `：${bulkLines.slice(0, 3).join(' / ')}${bulkLines.length > 3 ? ' ...' : ''}`}
                    </p>
                    <button
                      onClick={handleBulkAdd}
                      disabled={isRunning || bulkLines.length === 0}
                      className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors"
                    >
                      批量添加 {bulkLines.length > 0 && `(${bulkLines.length})`}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddKeyword()}
                    onPaste={handleKeywordPaste}
                    placeholder="新关键词，回车或点添加"
                    disabled={isRunning}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                  <button
                    onClick={handleAddKeyword}
                    disabled={isRunning}
                    className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-semibold rounded-lg transition-colors"
                  >
                    添加并启用
                  </button>
                </div>
              )}

              {isLoadingKeywords ? (
                <p className="text-gray-500 text-sm">加载中...</p>
              ) : keywords.length === 0 ? (
                <p className="text-gray-500 text-sm">还没有关键词，先在上面加一个</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {keywords.map((kw) => (
                    <div
                      key={kw.keyword}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="min-w-0 flex-1 mr-3">
                        <p className="text-sm font-medium text-gray-900 break-words">{kw.keyword}</p>
                        {kw.note && <p className="text-xs text-gray-500">{kw.note}</p>}
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <label className="inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={kw.enabled}
                            disabled={isRunning}
                            onChange={(e) => handleToggle(kw.keyword, e.target.checked)}
                            className="w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <span className="ml-2 text-xs text-gray-600">
                            {kw.enabled ? '启用中' : '已停用'}
                          </span>
                        </label>
                        <button
                          onClick={() => handleDeleteKeyword(kw.keyword)}
                          disabled={isRunning}
                          className="text-gray-400 hover:text-red-500 disabled:opacity-50 text-sm font-bold"
                          title="删除"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 筛选参数 */}
          {tab === 'settings' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-1">筛选参数</h2>
              <p className="text-xs text-gray-500 mb-4">
                真实读写 VikPea_配置.xlsx，跟桌面工作台是同一份配置——改这里桌面版也会跟着变。
              </p>
              {!settings ? (
                <p className="text-gray-500 text-sm">加载中...</p>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {SETTINGS_FIELDS.map((f) => (
                      <div key={f.key}>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          {f.label}
                        </label>
                        <input
                          type="number"
                          value={settingsDraft[f.key] ?? ''}
                          onChange={(e) =>
                            setSettingsDraft({ ...settingsDraft, [f.key]: e.target.value })
                          }
                          disabled={isRunning}
                          className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                        <p className="text-xs text-gray-400 mt-1">{f.hint}</p>
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={handleSaveSettings}
                    disabled={isSavingSettings || isRunning}
                    className="mt-4 px-4 py-2 bg-gray-800 hover:bg-gray-900 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors"
                  >
                    {isSavingSettings ? '保存中...' : '保存参数'}
                  </button>
                </>
              )}
            </div>
          )}

          {/* 候选库 */}
          {tab === 'candidates' && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-lg font-bold text-gray-900">候选库</h2>
                <div className="flex items-center gap-3">
                  {candidateView === 'confirmed' && (
                    <button
                      onClick={showAddForm ? () => setShowAddForm(false) : openAddForm}
                      className="text-xs text-blue-500 hover:text-blue-700 font-medium"
                    >
                      {showAddForm ? '取消' : '+ 手动添加'}
                    </button>
                  )}
                  <button
                    onClick={loadCandidates}
                    className="text-xs text-blue-500 hover:text-blue-700 font-medium"
                  >
                    ↻ 刷新
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mb-4">
                搜索/深度找邮箱产出的真实结果，来自 VikPea_发信名单.xlsx 和 VikPea_待确认邮箱.xlsx
              </p>

              {showAddForm && candidateView === 'confirmed' && (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-sm font-semibold text-gray-900 mb-3">
                    {editingRownum ? '编辑候选人' : '手动添加候选人'}
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input
                      type="text"
                      placeholder="频道名 *"
                      value={candidateForm.频道名}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 频道名: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="邮箱 *"
                      value={candidateForm.邮箱}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 邮箱: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="主页链接"
                      value={candidateForm.主页链接}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 主页链接: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="视频链接"
                      value={candidateForm.视频链接}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 视频链接: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="来源关键词（选填）"
                      value={candidateForm.来源关键词}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 来源关键词: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="频道标签（选填）"
                      value={candidateForm.频道标签}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 频道标签: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="备注（选填）"
                      value={candidateForm.备注}
                      onChange={(e) => setCandidateForm({ ...candidateForm, 备注: e.target.value })}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    onClick={handleSaveCandidate}
                    disabled={isSavingCandidate}
                    className="mt-3 px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors"
                  >
                    {isSavingCandidate ? '保存中...' : editingRownum ? '保存修改' : '添加'}
                  </button>
                </div>
              )}

              <div className="flex gap-2 mb-4 items-center">
                <button
                  onClick={() => setCandidateView('confirmed')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                    candidateView === 'confirmed'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  ✅ 可直接发信 ({confirmed.length})
                </button>
                <button
                  onClick={() => setCandidateView('pending')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                    candidateView === 'pending'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  🟡 待人工确认 ({pending.length})
                </button>
                <button
                  onClick={() => setCandidateView('no_email')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                    candidateView === 'no_email'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  📭 无邮箱候选 ({noEmail.length})
                </button>

                {candidateView === 'confirmed' && confirmed.length > 0 && (
                  <div className="ml-auto flex gap-2">
                    <button
                      onClick={() => setSelectedForSend(new Set(confirmed.map((_, idx) => idx)))}
                      className="px-3 py-1 rounded text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
                    >
                      全选
                    </button>
                    <button
                      onClick={() => setSelectedForSend(new Set())}
                      className="px-3 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                    >
                      取消全选
                    </button>
                    <span className="px-3 py-1 text-xs text-gray-600 bg-gray-50 rounded">
                      已选 {selectedForSend.size} 个
                    </span>
                  </div>
                )}
              </div>

              {isLoadingCandidates ? (
                <p className="text-gray-500 text-sm">加载中...</p>
              ) : candidateRows.length === 0 ? (
                <p className="text-gray-500 text-sm py-8 text-center">
                  还没有数据，跑一次搜索之后这里会出现结果
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-gray-500 border-b">
                        {candidateView === 'confirmed' && <th className="py-2 pr-4">本次发送</th>}
                        <th className="py-2 pr-4">频道名</th>
                        <th className="py-2 pr-4">邮箱</th>
                        {candidateView === 'pending' && <th className="py-2 pr-4">置信度</th>}
                        <th className="py-2 pr-4">频道标签</th>
                        <th className="py-2 pr-4">垂直度</th>
                        <th className="py-2 pr-4">推过竞品</th>
                        <th className="py-2 pr-4">合作方式</th>
                        <th className="py-2 pr-4">来源关键词</th>
                        <th className="py-2 pr-4">主页链接</th>
                        <th className="py-2 pr-4">视频链接</th>
                        {candidateView === 'confirmed' && <th className="py-2 pr-4">操作</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {candidateRows.map((row, i) => (
                        <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                          {candidateView === 'confirmed' && (
                            <td className="py-2 pr-4">
                              <input
                                type="checkbox"
                                checked={selectedForSend.has(i)}
                                onChange={(e) => {
                                  const newSet = new Set(selectedForSend);
                                  if (e.target.checked) {
                                    newSet.add(i);
                                  } else {
                                    newSet.delete(i);
                                  }
                                  setSelectedForSend(newSet);
                                }}
                                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                              />
                            </td>
                          )}
                          <td className="py-2 pr-4 font-medium text-gray-900">{row['频道名']}</td>
                          <td className="py-2 pr-4 font-mono text-xs">
                            {row['邮箱'] || row['候选邮箱']}
                          </td>
                          {candidateView === 'pending' && (
                            <td className="py-2 pr-4">{row['置信度']}</td>
                          )}
                          <td className="py-2 pr-4 text-gray-600">{row['频道标签']}</td>
                          <td className="py-2 pr-4">
                            {row['垂直度'] && (
                              <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${
                                Number(row['垂直度']) >= 8
                                  ? 'bg-green-100 text-green-700'
                                  : Number(row['垂直度']) >= 5
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-gray-100 text-gray-600'
                              }`}>
                                {row['垂直度']}/10
                              </span>
                            )}
                          </td>
                          <td className="py-2 pr-4">
                            {row['推过竞品'] && (
                              <span className={`text-xs ${
                                row['推过竞品'].startsWith('是')
                                  ? 'text-orange-600 font-semibold'
                                  : 'text-gray-500'
                              }`}>
                                {row['推过竞品']}
                              </span>
                            )}
                          </td>
                          <td className="py-2 pr-4">
                            {row['合作方式'] && (
                              <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                row['合作方式'] === 'Dedicated'
                                  ? 'bg-purple-100 text-purple-700'
                                  : 'bg-blue-100 text-blue-700'
                              }`}>
                                {row['合作方式']}
                              </span>
                            )}
                          </td>
                          <td className="py-2 pr-4 text-gray-600">{row['来源关键词']}</td>
                          <td className="py-2 pr-4">
                            {row['主页链接'] && (
                              <a
                                href={row['主页链接']}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:text-blue-700"
                              >
                                打开 →
                              </a>
                            )}
                          </td>
                          <td className="py-2 pr-4">
                            {row['视频链接'] && (
                              <a
                                href={row['视频链接']}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:text-blue-700"
                              >
                                打开 →
                              </a>
                            )}
                          </td>
                          {candidateView === 'confirmed' && (
                            <td className="py-2 pr-4 whitespace-nowrap">
                              <button
                                onClick={() => openEditForm(row)}
                                className="text-gray-400 hover:text-blue-600 mr-2"
                                title="编辑"
                              >
                                ✎
                              </button>
                              <button
                                onClick={() => handleDeleteCandidate(row['_rownum'], row['频道名'])}
                                className="text-gray-400 hover:text-red-500"
                                title="删除"
                              >
                                ✕
                              </button>
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
  );
}
