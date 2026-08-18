/**
 * 邮件模板 / 产品信息设置页面
 */

'use client';

import { useEffect, useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type EmailTemplateSettings } from '@/lib/api/vikpea';

const PLACEHOLDER_HINT =
  '可用占位符：{opening} 开场白（脚本自动生成） / {from_name} 你的署名 / {product_name} 产品名 / {product_team} 团队名 / {product_url} 产品链接';

export default function TemplatesPage() {
  const [draft, setDraft] = useState<EmailTemplateSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = async () => {
    try {
      setIsLoading(true);
      const data = await vikpeaAPI.getEmailTemplates();
      setDraft(data);
    } catch (err: any) {
      setError(err.message || '加载模板失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const update = (key: keyof EmailTemplateSettings, value: string) => {
    if (!draft) return;
    setDraft({ ...draft, [key]: value });
  };

  const handleSave = async () => {
    if (!draft) return;
    try {
      setIsSaving(true);
      setError(null);
      const data = await vikpeaAPI.updateEmailTemplates(draft);
      setDraft(data);
      setSuccess('已保存！VikPea_读表发信.py 发信时会用这套内容，桌面版和网页版共用。');
      setTimeout(() => setSuccess(null), 4000);
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📧 邮件模板</h1>
            <p className="text-gray-600">
              真实读写 VikPea_配置.xlsx —— 只管"写什么内容"，不涉及 SMTP 密码或真实发送
              （发信是单独的高风险功能，还没接进网页）。
            </p>
          </div>

          <div className="space-y-4 mb-8">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
          </div>

          {isLoading || !draft ? (
            <LoadingSpinner />
          ) : (
            <div className="space-y-6">
              {/* 产品信息 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">产品信息</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">产品名</label>
                    <input
                      type="text"
                      value={draft.PRODUCT_NAME}
                      onChange={(e) => update('PRODUCT_NAME', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">团队名</label>
                    <input
                      type="text"
                      value={draft.PRODUCT_TEAM}
                      onChange={(e) => update('PRODUCT_TEAM', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">产品链接</label>
                    <input
                      type="text"
                      value={draft.PRODUCT_URL}
                      onChange={(e) => update('PRODUCT_URL', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">你的署名</label>
                    <input
                      type="text"
                      value={draft.FROM_NAME}
                      onChange={(e) => update('FROM_NAME', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    />
                  </div>
                </div>
              </div>

              {/* YouTube 模板 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-1">🎥 YouTube 开发信</h2>
                <p className="text-xs text-gray-400 mb-4">{PLACEHOLDER_HINT}</p>
                <label className="block text-xs font-medium text-gray-700 mb-1">邮件主题</label>
                <input
                  type="text"
                  value={draft.OUTREACH_SUBJECT_YOUTUBE}
                  onChange={(e) => update('OUTREACH_SUBJECT_YOUTUBE', e.target.value)}
                  className="w-full px-3 py-2 mb-4 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
                <label className="block text-xs font-medium text-gray-700 mb-1">正文</label>
                <textarea
                  value={draft.OUTREACH_TEMPLATE_YOUTUBE}
                  onChange={(e) => update('OUTREACH_TEMPLATE_YOUTUBE', e.target.value)}
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
              </div>

              {/* 文章模板 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-1">📝 文章站点开发信</h2>
                <p className="text-xs text-gray-400 mb-4">{PLACEHOLDER_HINT}</p>
                <label className="block text-xs font-medium text-gray-700 mb-1">邮件主题</label>
                <input
                  type="text"
                  value={draft.OUTREACH_SUBJECT_ARTICLE}
                  onChange={(e) => update('OUTREACH_SUBJECT_ARTICLE', e.target.value)}
                  className="w-full px-3 py-2 mb-4 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
                <label className="block text-xs font-medium text-gray-700 mb-1">正文</label>
                <textarea
                  value={draft.OUTREACH_TEMPLATE_ARTICLE}
                  onChange={(e) => update('OUTREACH_TEMPLATE_ARTICLE', e.target.value)}
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                />
              </div>

              <button
                onClick={handleSave}
                disabled={isSaving}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition-all"
              >
                {isSaving ? '保存中...' : '保存模板'}
              </button>
            </div>
          )}
        </div>
      </main>
  );
}
