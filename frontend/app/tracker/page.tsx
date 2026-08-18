/**
 * 发送追踪页面 —— 已联络记录 + 回复/跟进进度
 */

'use client';

import { useEffect, useState } from 'react';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import LoadingSpinner from '../components/LoadingSpinner';
import vikpeaAPI, { type TrackerUpdateInput } from '@/lib/api/vikpea';

const EMPTY_FORM: TrackerUpdateInput = {
  是否回复: '',
  回复摘要: '',
  当前状态: '',
  ABC分级: '',
  跟进1日期: '',
  跟进1状态: '',
  跟进2日期: '',
  跟进2状态: '',
  最近回复日期: '',
  频道标签: '',
};

export default function TrackerPage() {
  const [rows, setRows] = useState<Record<string, any>[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingRownum, setEditingRownum] = useState<number | null>(null);
  const [form, setForm] = useState<TrackerUpdateInput>(EMPTY_FORM);
  const [isSaving, setIsSaving] = useState(false);

  const load = async () => {
    try {
      setIsLoading(true);
      const data = await vikpeaAPI.getTracker();
      setRows(data.rows);
    } catch (err: any) {
      setError(err.message || '加载追踪记录失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openEdit = (row: Record<string, any>) => {
    setForm({
      是否回复: row['是否回复'] || '',
      回复摘要: row['回复摘要'] || '',
      当前状态: row['当前状态'] || '',
      ABC分级: row['ABC分级'] || '',
      跟进1日期: row['跟进1日期'] || '',
      跟进1状态: row['跟进1状态'] || '',
      跟进2日期: row['跟进2日期'] || '',
      跟进2状态: row['跟进2状态'] || '',
      最近回复日期: row['最近回复日期'] || '',
      频道标签: row['频道标签'] || '',
    });
    setEditingRownum(row['_rownum']);
  };

  const handleSave = async () => {
    if (editingRownum == null) return;
    try {
      setIsSaving(true);
      setError(null);
      const data = await vikpeaAPI.updateTracker(editingRownum, form);
      setRows(data.rows);
      setEditingRownum(null);
      setSuccess('已更新');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  const total = rows.length;
  const replied = rows.filter((r) => ['是', 'Y', 'Yes', 'yes', 'TRUE', 'True'].includes(String(r['是否回复'] || ''))).length;
  const gradeA = rows.filter((r) => String(r['ABC分级'] || '').toUpperCase() === 'A').length;

  return (
    <main className="py-8 md:py-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📈 发送追踪</h1>
          <p className="text-gray-600">
            已联络记录 + 回复/跟进进度，真实读写 VikPea_邮件开发追踪.xlsx
          </p>
        </div>

        <div className="space-y-4 mb-6">
          {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
          {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 mb-1">已联络总数</p>
            <p className="text-2xl font-bold text-gray-900">{total}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 mb-1">已回复</p>
            <p className="text-2xl font-bold text-green-600">{replied}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-5">
            <p className="text-sm text-gray-500 mb-1">A 级</p>
            <p className="text-2xl font-bold text-blue-600">{gradeA}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">联络记录</h2>
            <button onClick={load} className="text-xs text-blue-500 hover:text-blue-700 font-medium">
              ↻ 刷新
            </button>
          </div>

          {isLoading ? (
            <LoadingSpinner />
          ) : rows.length === 0 ? (
            <p className="text-gray-500 text-sm py-8 text-center">
              还没有联络记录，发信之后这里会出现数据
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-gray-500 border-b">
                    <th className="py-2 pr-4">日期</th>
                    <th className="py-2 pr-4">联系人/平台</th>
                    <th className="py-2 pr-4">邮箱</th>
                    <th className="py-2 pr-4">视频链接</th>
                    <th className="py-2 pr-4">是否回复</th>
                    <th className="py-2 pr-4">当前状态</th>
                    <th className="py-2 pr-4">ABC分级</th>
                    <th className="py-2 pr-4">频道标签</th>
                    <th className="py-2 pr-4">回复摘要</th>
                    <th className="py-2 pr-4">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, i) => (
                    <tr key={i} className="border-b border-gray-100 hover:bg-gray-50 align-top">
                      <td className="py-2 pr-4 whitespace-nowrap text-gray-600">{row['日期']}</td>
                      <td className="py-2 pr-4 font-medium text-gray-900">{row['联系人/平台']}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{row['邮箱']}</td>
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
                      <td className="py-2 pr-4">
                        {row['是否回复'] ? (
                          <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                            {row['是否回复']}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-xs">未回复</span>
                        )}
                      </td>
                      <td className="py-2 pr-4 text-gray-600">{row['当前状态']}</td>
                      <td className="py-2 pr-4">{row['ABC分级']}</td>
                      <td className="py-2 pr-4 text-gray-600">{row['频道标签']}</td>
                      <td className="py-2 pr-4 text-gray-600 max-w-xs truncate">{row['回复摘要']}</td>
                      <td className="py-2 pr-4">
                        <button
                          onClick={() => openEdit(row)}
                          className="text-gray-400 hover:text-blue-600"
                          title="更新回复/跟进状态"
                        >
                          ✎ 更新
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {editingRownum != null && (
          <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-bold text-gray-900 mb-4">更新回复/跟进状态</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">是否回复</label>
                  <select
                    value={form.是否回复}
                    onChange={(e) => setForm({ ...form, 是否回复: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">未回复</option>
                    <option value="是">是</option>
                    <option value="否">否</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">回复摘要</label>
                  <textarea
                    value={form.回复摘要}
                    onChange={(e) => setForm({ ...form, 回复摘要: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">当前状态</label>
                    <input
                      type="text"
                      value={form.当前状态}
                      onChange={(e) => setForm({ ...form, 当前状态: e.target.value })}
                      placeholder="沟通中 / 已合作 / 已拒绝..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">ABC 分级</label>
                    <select
                      value={form.ABC分级}
                      onChange={(e) => setForm({ ...form, ABC分级: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">未分级</option>
                      <option value="A">A</option>
                      <option value="B">B</option>
                      <option value="C">C</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">频道标签</label>
                  <input
                    type="text"
                    value={form.频道标签}
                    onChange={(e) => setForm({ ...form, 频道标签: e.target.value })}
                    placeholder="例如：科技、美妆、教育..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">跟进1日期</label>
                    <input
                      type="text"
                      value={form.跟进1日期}
                      onChange={(e) => setForm({ ...form, 跟进1日期: e.target.value })}
                      placeholder="2026-08-20"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">跟进1状态</label>
                    <input
                      type="text"
                      value={form.跟进1状态}
                      onChange={(e) => setForm({ ...form, 跟进1状态: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-5">
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
                >
                  {isSaving ? '保存中...' : '保存'}
                </button>
                <button
                  onClick={() => setEditingRownum(null)}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 rounded-lg transition-colors"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
