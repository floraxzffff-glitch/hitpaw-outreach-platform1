/**
 * 系统设置：SMTP / IMAP / 搜索引擎 API / 发信节奏
 */

'use client';

import { useEffect, useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type SystemSettings } from '@/lib/api/vikpea';

function SecretField({
  label,
  hint,
  isSet,
  value,
  onChange,
}: {
  label: string;
  hint?: string;
  isSet: boolean;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-700 mb-1">
        {label} {isSet && <span className="text-green-600">✓ 已设置</span>}
      </label>
      <input
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={isSet ? '已设置，留空则不修改' : '还没设置'}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
      />
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  );
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [draft, setDraft] = useState<Record<string, any>>({});
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [filterConfig, setFilterConfig] = useState<any>(null);
  const [isUploadingFilter, setIsUploadingFilter] = useState(false);
  const [contactThreshold, setContactThreshold] = useState<number>(90);
  const [isUpdatingThreshold, setIsUpdatingThreshold] = useState(false);
  const [contactedHistoryRecords, setContactedHistoryRecords] = useState<Record<string, any>[]>([]);
  const [isLoadingContactedHistory, setIsLoadingContactedHistory] = useState(false);
  const [showContactedHistoryList, setShowContactedHistoryList] = useState(false);
  const [newContactRecord, setNewContactRecord] = useState({ 频道名: '', 邮箱: '', 联络日期: '', 备注: '' });
  const [isAddingContactRecord, setIsAddingContactRecord] = useState(false);

  const load = async () => {
    try {
      setIsLoading(true);
      const data = await vikpeaAPI.getSystemSettings();
      setSettings(data);
      setDraft(data);

      // 加载过滤配置
      const filterData = await vikpeaAPI.getFilterConfig();
      setFilterConfig(filterData);

      // 加载联络历史时间阈值
      const thresholdResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/filter-config/contact-threshold`
      );
      if (thresholdResponse.ok) {
        const thresholdData = await thresholdResponse.json();
        setContactThreshold(thresholdData.followup1_after_days);
      }
    } catch (err: any) {
      setError(err.message || '加载设置失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError(null);
      const updates: Record<string, any> = {
        SMTP_SERVER: draft.SMTP_SERVER,
        SMTP_PORT: Number(draft.SMTP_PORT),
        SMTP_TIMEOUT: Number(draft.SMTP_TIMEOUT),
        SMTP_ALLOW_INSECURE_SSL: Boolean(draft.SMTP_ALLOW_INSECURE_SSL),
        FROM_EMAIL: draft.FROM_EMAIL,
        IMAP_SERVER: draft.IMAP_SERVER,
        IMAP_PORT: Number(draft.IMAP_PORT),
        DAILY_SEND_LIMIT: Number(draft.DAILY_SEND_LIMIT),
        FOLLOWUP_DAILY_LIMIT: Number(draft.FOLLOWUP_DAILY_LIMIT),
        FOLLOWUP1_AFTER_DAYS: Number(draft.FOLLOWUP1_AFTER_DAYS),
        FOLLOWUP2_AFTER_DAYS: Number(draft.FOLLOWUP2_AFTER_DAYS),
        DELAY_SEC: Number(draft.DELAY_SEC),
        SERP_PROVIDER: draft.SERP_PROVIDER,
        DATAFORSEO_LOGIN: draft.DATAFORSEO_LOGIN,
        ANTHROPIC_API_BASE: draft.ANTHROPIC_API_BASE,
        ANTHROPIC_TAG_MODEL: draft.ANTHROPIC_TAG_MODEL,
        ...secrets, // 只有真的填了新值的密钥字段才会在这里出现
      };
      const data = await vikpeaAPI.updateSystemSettings(updates);
      setSettings(data);
      setDraft(data);
      setSecrets({});
      setSuccess('已保存！这只是存配置，不会触发任何真实发信或调用外部 API。');
      setTimeout(() => setSuccess(null), 4000);
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFilterUpload = async (configType: string, file: File) => {
    try {
      setIsUploadingFilter(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/upload/filter-config?config_type=${configType}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('上传失败');
      }

      // 重新加载过滤配置
      const filterData = await vikpeaAPI.getFilterConfig();
      setFilterConfig(filterData);

      setSuccess('过滤配置已上传！');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '上传过滤配置失败');
    } finally {
      setIsUploadingFilter(false);
    }
  };

  const handleThresholdUpdate = async () => {
    try {
      setIsUpdatingThreshold(true);
      setError(null);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/filter-config/contact-threshold`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ threshold_days: contactThreshold }),
        }
      );

      if (!response.ok) {
        throw new Error('更新失败');
      }

      const result = await response.json();
      setSuccess(result.message);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '更新联络历史阈值失败');
    } finally {
      setIsUpdatingThreshold(false);
    }
  };

  const loadContactedHistory = async () => {
    try {
      setIsLoadingContactedHistory(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/contacted-history`
      );
      if (response.ok) {
        const data = await response.json();
        setContactedHistoryRecords(data.records || []);
      }
    } catch (err: any) {
      console.error('加载已联络历史失败:', err);
    } finally {
      setIsLoadingContactedHistory(false);
    }
  };

  const handleAddContactRecord = async () => {
    try {
      setIsAddingContactRecord(true);
      setError(null);

      if (!newContactRecord.频道名 || !newContactRecord.邮箱 || !newContactRecord.联络日期) {
        setError('频道名、邮箱和联络日期不能为空');
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/contacted-history`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            频道名: newContactRecord.频道名,
            email: newContactRecord.邮箱,
            联络日期: newContactRecord.联络日期,
            备注: newContactRecord.备注,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('添加失败');
      }

      setSuccess('已添加联络历史记录');
      setTimeout(() => setSuccess(null), 3000);
      setNewContactRecord({ 频道名: '', 邮箱: '', 联络日期: '', 备注: '' });
      await loadContactedHistory();
      await load();
    } catch (err: any) {
      setError(err.message || '添加联络历史记录失败');
    } finally {
      setIsAddingContactRecord(false);
    }
  };

  const handleDeleteContactRecord = async (rowIndex: number) => {
    if (!confirm('确定要删除这条联络历史记录吗？')) return;

    try {
      setError(null);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ''}/api/contacted-history`,
        {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ row_index: rowIndex }),
        }
      );

      if (!response.ok) {
        throw new Error('删除失败');
      }

      setSuccess('已删除联络历史记录');
      setTimeout(() => setSuccess(null), 3000);
      await loadContactedHistory();
      await load();
    } catch (err: any) {
      setError(err.message || '删除联络历史记录失败');
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">⚙️ 系统设置</h1>
            <p className="text-gray-600">
              真实读写 VikPea_配置.xlsx。密钥类字段（密码、API Key）只会显示"是否已设置"，
              绝不会把明文传回浏览器；只有你填了新值才会覆盖。这里只是存配置，不会触发任何真实发信。
            </p>
          </div>

          <div className="space-y-4 mb-8">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
          </div>

          {isLoading || !settings ? (
            <LoadingSpinner />
          ) : (
            <div className="space-y-6">
              {/* SMTP */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">📤 发信服务器 (SMTP)</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">SMTP 地址</label>
                    <input
                      type="text"
                      value={draft.SMTP_SERVER || ''}
                      onChange={(e) => setDraft({ ...draft, SMTP_SERVER: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">端口</label>
                    <input
                      type="number"
                      value={draft.SMTP_PORT ?? ''}
                      onChange={(e) => setDraft({ ...draft, SMTP_PORT: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">发信邮箱</label>
                    <input
                      type="text"
                      value={draft.FROM_EMAIL || ''}
                      onChange={(e) => setDraft({ ...draft, FROM_EMAIL: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <SecretField
                    label="邮箱授权码"
                    isSet={settings.PASSWORD_SET}
                    value={secrets.PASSWORD || ''}
                    onChange={(v) => setSecrets({ ...secrets, PASSWORD: v })}
                  />
                </div>
              </div>

              {/* IMAP */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">📥 收信服务器 (IMAP)</h2>
                <p className="text-xs text-gray-400 mb-4">读取回复用的，跟发信共用同一个授权码</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">IMAP 地址</label>
                    <input
                      type="text"
                      value={draft.IMAP_SERVER || ''}
                      onChange={(e) => setDraft({ ...draft, IMAP_SERVER: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">端口</label>
                    <input
                      type="number"
                      value={draft.IMAP_PORT ?? ''}
                      onChange={(e) => setDraft({ ...draft, IMAP_PORT: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* 发信节奏 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">⏱️ 发信节奏限制</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">每日发信上限</label>
                    <input
                      type="number"
                      value={draft.DAILY_SEND_LIMIT ?? ''}
                      onChange={(e) => setDraft({ ...draft, DAILY_SEND_LIMIT: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">每日跟进上限</label>
                    <input
                      type="number"
                      value={draft.FOLLOWUP_DAILY_LIMIT ?? ''}
                      onChange={(e) => setDraft({ ...draft, FOLLOWUP_DAILY_LIMIT: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      第一次跟进（发信后几天）
                    </label>
                    <input
                      type="number"
                      value={draft.FOLLOWUP1_AFTER_DAYS ?? ''}
                      onChange={(e) => setDraft({ ...draft, FOLLOWUP1_AFTER_DAYS: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      第二次跟进（发信后几天）
                    </label>
                    <input
                      type="number"
                      value={draft.FOLLOWUP2_AFTER_DAYS ?? ''}
                      onChange={(e) => setDraft({ ...draft, FOLLOWUP2_AFTER_DAYS: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      每封间隔秒数
                    </label>
                    <input
                      type="number"
                      value={draft.DELAY_SEC ?? ''}
                      onChange={(e) => setDraft({ ...draft, DELAY_SEC: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* 搜索引擎 / YouTube API */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-1">🔑 搜索引擎 / YouTube API</h2>
                <p className="text-xs text-gray-400 mb-4">
                  都是可选的：不填就走免费的裸抓取（yt-dlp / 直接爬搜索结果页），填了会更稳定、更不容易被限流
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      搜索引擎供应商 (SERP_PROVIDER)
                    </label>
                    <input
                      type="text"
                      value={draft.SERP_PROVIDER || ''}
                      onChange={(e) => setDraft({ ...draft, SERP_PROVIDER: e.target.value })}
                      placeholder="serper / serpapi / dataforseo，留空=不用"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <SecretField
                    label="Serper API Key"
                    isSet={settings.SERPER_API_KEY_SET}
                    value={secrets.SERPER_API_KEY || ''}
                    onChange={(v) => setSecrets({ ...secrets, SERPER_API_KEY: v })}
                  />
                  <SecretField
                    label="SerpApi Key"
                    isSet={settings.SERPAPI_KEY_SET}
                    value={secrets.SERPAPI_KEY || ''}
                    onChange={(v) => setSecrets({ ...secrets, SERPAPI_KEY: v })}
                  />
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      DataForSEO 登录名
                    </label>
                    <input
                      type="text"
                      value={draft.DATAFORSEO_LOGIN || ''}
                      onChange={(e) => setDraft({ ...draft, DATAFORSEO_LOGIN: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <SecretField
                    label="DataForSEO 密码"
                    isSet={settings.DATAFORSEO_PASSWORD_SET}
                    value={secrets.DATAFORSEO_PASSWORD || ''}
                    onChange={(v) => setSecrets({ ...secrets, DATAFORSEO_PASSWORD: v })}
                  />
                  <SecretField
                    label="YouTube Data API Key"
                    isSet={settings.YOUTUBE_API_KEY_SET}
                    value={secrets.YOUTUBE_API_KEY || ''}
                    onChange={(v) => setSecrets({ ...secrets, YOUTUBE_API_KEY: v })}
                    hint="填了之后 YouTube 搜索会优先走官方 API，播放量/发布时间更准更稳"
                  />
                </div>
              </div>

              {/* AI API 配置 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-1">🤖 AI API 配置 (Claude)</h2>
                <p className="text-xs text-gray-400 mb-4">
                  用于频道深度分析和标签生成。使用 VectorEngine 统一代理，只需配置一个 API Key
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <SecretField
                    label="API Key"
                    isSet={settings.ANTHROPIC_API_KEY_SET}
                    value={secrets.ANTHROPIC_API_KEY || ''}
                    onChange={(v) => setSecrets({ ...secrets, ANTHROPIC_API_KEY: v })}
                    hint="VectorEngine 统一 API Key（支持 Claude 和 DeepSeek 模型）"
                  />
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">API Base URL</label>
                    <input
                      type="text"
                      value={draft.ANTHROPIC_API_BASE || ''}
                      onChange={(e) => setDraft({ ...draft, ANTHROPIC_API_BASE: e.target.value })}
                      placeholder="https://api.vectorengine.ai/v1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">AI 模型</label>
                    <input
                      type="text"
                      value={draft.ANTHROPIC_TAG_MODEL || ''}
                      onChange={(e) => setDraft({ ...draft, ANTHROPIC_TAG_MODEL: e.target.value })}
                      placeholder="claude-3-5-sonnet-20241022"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-400 mt-1">推荐：claude-3-5-sonnet-20241022（性能最佳）</p>
                  </div>
                </div>
              </div>

              {/* 过滤配置管理 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-1">🚫 KOL过滤配置</h2>
                <p className="text-xs text-gray-400 mb-4">
                  上传Excel配置文件来管理负关键词、竞品站点、邮箱黑名单等过滤规则
                </p>

                {filterConfig && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">当前配置统计</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                      <div>
                        <span className="text-gray-500">负关键词：</span>
                        <span className="font-semibold text-gray-900">{filterConfig.negative_keywords_count}个</span>
                      </div>
                      <div>
                        <span className="text-gray-500">竞品站点：</span>
                        <span className="font-semibold text-gray-900">{filterConfig.competitor_sites_count}个</span>
                      </div>
                      <div>
                        <span className="text-gray-500">竞品邮箱：</span>
                        <span className="font-semibold text-gray-900">{filterConfig.competitor_email_suffixes_count}个</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Affiliate黑名单：</span>
                        <span className="font-semibold text-gray-900">{filterConfig.affiliate_blacklist_count}个</span>
                      </div>
                      <div>
                        <span className="text-gray-500">长期合作名单：</span>
                        <span className="font-semibold text-gray-900">{filterConfig.longterm_partners_count}个</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {/* 视频负关键词 */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">📹 视频负关键词</h3>
                    <p className="text-xs text-gray-500 mb-3">
                      检查视频标题和简介中的品牌词（如hitpaw、tenorshare），根据合作时间决定是否排除
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFilterUpload('negative_keywords', file);
                      }}
                      disabled={isUploadingFilter}
                      className="text-xs"
                    />
                  </div>

                  {/* 竞品站点黑名单 */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">🌐 竞品站点黑名单</h3>
                    <p className="text-xs text-gray-500 mb-3">
                      排除推广过竞品站点的KOL
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFilterUpload('competitor_sites', file);
                      }}
                      disabled={isUploadingFilter}
                      className="text-xs"
                    />
                  </div>

                  {/* 竞品邮箱后缀 */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">✉️ 竞品邮箱后缀</h3>
                    <p className="text-xs text-gray-500 mb-3">
                      排除特定邮箱后缀（如竞品公司邮箱）
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFilterUpload('competitor_emails', file);
                      }}
                      disabled={isUploadingFilter}
                      className="text-xs"
                    />
                  </div>

                  {/* Affiliate黑名单 */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">🚫 Affiliate黑名单</h3>
                    <p className="text-xs text-gray-500 mb-3">
                      排除已知的Affiliate用户
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFilterUpload('affiliate_blacklist', file);
                      }}
                      disabled={isUploadingFilter}
                      className="text-xs"
                    />
                  </div>

                  {/* 长期合作名单 */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">🤝 长期合作名单</h3>
                    <p className="text-xs text-gray-500 mb-3">
                      排除已建立长期合作关系的KOL
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFilterUpload('longterm_partners', file);
                      }}
                      disabled={isUploadingFilter}
                      className="text-xs"
                    />
                  </div>

                  {/* 已联络历史名单 */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">📋 已联络历史名单</h3>
                    <p className="text-xs text-gray-500 mb-3">
                      上传团队已联络过的KOL名单，自动去重并标注联络时间
                    </p>
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFilterUpload('contacted_history', file);
                      }}
                      disabled={isUploadingFilter}
                      className="text-xs"
                    />
                    <p className="text-xs text-gray-400 mt-2">
                      Excel格式：频道名 | 邮箱 | 联络日期 | 备注
                    </p>

                    {/* 联络历史时间阈值配置 */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <label className="block text-xs font-medium text-gray-700 mb-2">
                        联络历史时间阈值（天）
                      </label>
                      <p className="text-xs text-gray-500 mb-3">
                        小于阈值 = 直接排除 | 大于阈值 = 不排除但标注"XX天前已联络"
                      </p>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          min="1"
                          value={contactThreshold}
                          onChange={(e) => setContactThreshold(Number(e.target.value))}
                          className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="text-xs text-gray-600">天</span>
                        <button
                          onClick={handleThresholdUpdate}
                          disabled={isUpdatingThreshold}
                          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition"
                        >
                          {isUpdatingThreshold ? '更新中...' : '更新阈值'}
                        </button>
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        当前阈值：{contactThreshold}天（小于{contactThreshold}天的直接排除，大于{contactThreshold}天的标注提醒）
                      </p>
                    </div>

                    {/* 查看和管理联络历史记录 */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <button
                        onClick={() => {
                          setShowContactedHistoryList(!showContactedHistoryList);
                          if (!showContactedHistoryList) {
                            loadContactedHistory();
                          }
                        }}
                        className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {showContactedHistoryList ? '隐藏' : '查看'} 已联络历史记录 ({filterConfig?.contacted_history_count || 0}条)
                      </button>

                      {showContactedHistoryList && (
                        <div className="mt-3 space-y-3">
                          {/* 添加新记录表单 */}
                          <div className="border border-blue-200 rounded-lg p-3 bg-blue-50">
                            <h4 className="text-xs font-semibold text-gray-800 mb-2">添加新记录</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              <input
                                type="text"
                                placeholder="频道名"
                                value={newContactRecord.频道名}
                                onChange={(e) => setNewContactRecord({ ...newContactRecord, 频道名: e.target.value })}
                                className="px-2 py-1 border border-gray-300 rounded text-xs outline-none focus:ring-1 focus:ring-blue-500"
                              />
                              <input
                                type="email"
                                placeholder="邮箱"
                                value={newContactRecord.邮箱}
                                onChange={(e) => setNewContactRecord({ ...newContactRecord, 邮箱: e.target.value })}
                                className="px-2 py-1 border border-gray-300 rounded text-xs outline-none focus:ring-1 focus:ring-blue-500"
                              />
                              <input
                                type="date"
                                value={newContactRecord.联络日期}
                                onChange={(e) => setNewContactRecord({ ...newContactRecord, 联络日期: e.target.value })}
                                className="px-2 py-1 border border-gray-300 rounded text-xs outline-none focus:ring-1 focus:ring-blue-500"
                              />
                              <input
                                type="text"
                                placeholder="备注（可选）"
                                value={newContactRecord.备注}
                                onChange={(e) => setNewContactRecord({ ...newContactRecord, 备注: e.target.value })}
                                className="px-2 py-1 border border-gray-300 rounded text-xs outline-none focus:ring-1 focus:ring-blue-500"
                              />
                            </div>
                            <button
                              onClick={handleAddContactRecord}
                              disabled={isAddingContactRecord}
                              className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-medium rounded transition"
                            >
                              {isAddingContactRecord ? '添加中...' : '添加记录'}
                            </button>
                          </div>

                          {/* 记录列表 */}
                          {isLoadingContactedHistory ? (
                            <p className="text-xs text-gray-500">加载中...</p>
                          ) : contactedHistoryRecords.length === 0 ? (
                            <p className="text-xs text-gray-500">暂无联络历史记录</p>
                          ) : (
                            <div className="border border-gray-200 rounded-lg overflow-hidden">
                              <div className="max-h-64 overflow-y-auto">
                                <table className="w-full text-xs">
                                  <thead className="bg-gray-100 sticky top-0">
                                    <tr>
                                      <th className="px-2 py-1 text-left text-gray-700 font-semibold">频道名</th>
                                      <th className="px-2 py-1 text-left text-gray-700 font-semibold">邮箱</th>
                                      <th className="px-2 py-1 text-left text-gray-700 font-semibold">联络日期</th>
                                      <th className="px-2 py-1 text-left text-gray-700 font-semibold">备注</th>
                                      <th className="px-2 py-1 text-center text-gray-700 font-semibold">操作</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-gray-200">
                                    {contactedHistoryRecords.map((record, idx) => (
                                      <tr key={idx} className="hover:bg-gray-50">
                                        <td className="px-2 py-1">{record.频道名}</td>
                                        <td className="px-2 py-1">{record.邮箱}</td>
                                        <td className="px-2 py-1">{record.联络日期}</td>
                                        <td className="px-2 py-1 text-gray-600">{record.备注}</td>
                                        <td className="px-2 py-1 text-center">
                                          <button
                                            onClick={() => handleDeleteContactRecord(record._row_index)}
                                            className="text-red-600 hover:text-red-800 font-medium"
                                          >
                                            删除
                                          </button>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={handleSave}
                disabled={isSaving}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition-all"
              >
                {isSaving ? '保存中...' : '保存设置'}
              </button>
            </div>
          )}
        </div>
      </main>
  );
}
