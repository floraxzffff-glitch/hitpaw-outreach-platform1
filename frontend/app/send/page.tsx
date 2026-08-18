/**
 * 发送开发信页面 —— 高风险功能，两段式：先预览，明确勾选确认后才真发
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type SendPreview, type SendJob } from '@/lib/api/vikpea';

export default function SendPage() {
  const [preview, setPreview] = useState<SendPreview | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [personalize, setPersonalize] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [job, setJob] = useState<SendJob | null>(null);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [job?.log.length]);

  const isSending = job?.status === 'running';

  const handlePreview = async () => {
    try {
      setIsPreviewing(true);
      setError(null);
      setSuccess(null);
      setJob(null);
      const data = await vikpeaAPI.previewSend(personalize);
      setPreview(data);
      if (data.message) {
        setSuccess(data.message);
      } else {
        setSelected(new Set(data.targets.map((t) => t.rownum)));
      }
    } catch (err: any) {
      setError(err.message || '预览失败');
    } finally {
      setIsPreviewing(false);
    }
  };

  const toggleRow = (rownum: number) => {
    const next = new Set(selected);
    if (next.has(rownum)) next.delete(rownum);
    else next.add(rownum);
    setSelected(next);
  };

  const pollJob = (jobId: string) => {
    if (pollTimer.current) clearInterval(pollTimer.current);
    pollTimer.current = setInterval(async () => {
      try {
        const data = await vikpeaAPI.getSendJob(jobId);
        setJob(data);
        if (data.status !== 'running') {
          if (pollTimer.current) clearInterval(pollTimer.current);
          if (data.status === 'completed') {
            setSuccess('发送任务已完成，看下面日志确认成功/失败数量');
          } else {
            setError(data.error || '发送任务失败');
          }
          setPreview(null);
        }
      } catch (err: any) {
        if (pollTimer.current) clearInterval(pollTimer.current);
        setError(err.message || '查询发送状态失败');
      }
    }, 2000);
  };

  const handleConfirmSend = () => {
    if (!preview?.preview_id || selected.size === 0) return;
    const ok = window.confirm(
      `确认要真实发送 ${selected.size} 封邮件吗？这个操作不可撤销，收件人会真的收到邮件。`
    );
    if (!ok) return;

    (async () => {
      try {
        setError(null);
        const { job_id } = await vikpeaAPI.confirmSend(preview.preview_id!, Array.from(selected));
        setJob({
          job_id,
          resource: 'email_send',
          label: '',
          status: 'running',
          log: [],
          started_at: new Date().toISOString(),
        });
        pollJob(job_id);
      } catch (err: any) {
        setError(err.message || '发送失败');
      }
    })();
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📮 发送开发信</h1>
            <p className="text-gray-600">
              跑的是真实的 VikPea_读表发信.py 逻辑（安全拦截、去重、主题生成都是同一套代码）。
            </p>
            <div className="mt-3 bg-red-50 border border-red-200 text-red-800 text-sm rounded-lg px-4 py-3">
              ⚠️ 这个功能会真实发送邮件给真实收件人，不可撤销。流程是：先「预览」（不发送）→ 勾选要发的人
              → 点「确认发送」并二次确认，才会真正建立 SMTP 连接发信。
            </div>
          </div>

          <div className="space-y-4 mb-6">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
          </div>

          {/* 预览触发 */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <label className="inline-flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={personalize}
                  disabled={isSending}
                  onChange={(e) => setPersonalize(e.target.checked)}
                  className="w-4 h-4 text-blue-500 rounded"
                />
                抓最近视频标题定制开头（更慢，但更个性化）
              </label>
              <button
                onClick={handlePreview}
                disabled={isPreviewing || isSending}
                className="bg-gray-800 hover:bg-gray-900 disabled:opacity-50 text-white font-semibold py-2.5 px-6 rounded-lg transition-all"
              >
                {isPreviewing ? '预览中...' : '👀 预览（不会发送）'}
              </button>
            </div>
          </div>

          {/* 预览结果 */}
          {preview && preview.targets.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900">
                  可发送 {preview.targets.length} 封（已选 {selected.size}）
                </h2>
                <button
                  onClick={handleConfirmSend}
                  disabled={selected.size === 0 || isSending}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 disabled:opacity-50 text-white font-semibold py-2.5 px-6 rounded-lg transition-all"
                >
                  🚀 确认发送 {selected.size} 封
                </button>
              </div>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {preview.targets.map((t) => (
                  <label
                    key={t.rownum}
                    className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
                  >
                    <input
                      type="checkbox"
                      checked={selected.has(t.rownum)}
                      onChange={() => toggleRow(t.rownum)}
                      className="mt-1 w-4 h-4 text-blue-500 rounded"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {t.name} <span className="text-gray-400 font-normal">→</span>{' '}
                        <span className="font-mono text-xs">{t.email}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">主题：{t.subject}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* 被拦截的 */}
          {preview && preview.blocked.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-bold text-gray-900 mb-1">
                🛑 已拦截，不会发送 ({preview.blocked.length})
              </h2>
              <p className="text-xs text-gray-500 mb-4">黑名单/格式异常/已经发过——安全逻辑自动挡下来的</p>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {preview.blocked.map((t, i) => (
                  <div key={i} className="p-3 bg-red-50 rounded-lg text-sm">
                    <span className="font-medium text-gray-900">{t.name}</span>{' '}
                    <span className="font-mono text-xs text-gray-600">{t.email}</span>{' '}
                    <span className="text-red-700 text-xs">— {t.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {preview && preview.targets.length === 0 && preview.blocked.length === 0 && !preview.message && (
            <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
              发信名单是空的，先去候选库确认几个邮箱再来发信
            </div>
          )}

          {/* 发送日志 */}
          {job && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900">发送日志</h2>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    job.status === 'running'
                      ? 'bg-blue-100 text-blue-700'
                      : job.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {job.status === 'running' ? '发送中' : job.status === 'completed' ? '已完成' : '失败'}
                </span>
              </div>
              <div className="bg-gray-900 text-gray-100 font-mono text-xs rounded-lg p-4 max-h-96 overflow-y-auto">
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
      </main>
  );
}
