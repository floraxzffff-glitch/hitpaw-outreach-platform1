/**
 * 邮箱验证页面
 */

'use client';

import { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import SuccessAlert from '../components/SuccessAlert';
import vikpeaAPI, { type EmailValidationResponse } from '@/lib/api/vikpea';
import { validateEmail, copyToClipboard } from '@/lib/utils/helpers';

export default function EmailPage() {
  const [emailInput, setEmailInput] = useState('');
  const [emails, setEmails] = useState<string[]>([]);
  const [results, setResults] = useState<EmailValidationResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [checkBlacklist, setCheckBlacklist] = useState(true);

  const addEmail = () => {
    const trimmed = emailInput.trim();
    if (!trimmed) {
      setError('请输入邮箱地址');
      return;
    }
    if (!validateEmail(trimmed)) {
      setError('邮箱格式不正确');
      return;
    }
    if (emails.includes(trimmed)) {
      setError('邮箱已存在');
      return;
    }
    if (emails.length >= 100) {
      setError('最多添加 100 个邮箱');
      return;
    }

    setEmails([...emails, trimmed]);
    setEmailInput('');
    setError(null);
  };

  const removeEmail = (email: string) => {
    setEmails(emails.filter((e) => e !== email));
  };

  const handleValidate = async () => {
    if (emails.length === 0) {
      setError('请先添加邮箱');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      const data = await vikpeaAPI.validateEmailsBatch(emails);
      setResults(data.results);
      setSuccess(`验证完成！已处理 ${data.processed} 个邮箱`);

      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || '验证失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      const newEmails = text
        .split(/[\n,;\s]+/)
        .map((e) => e.trim())
        .filter((e) => e && validateEmail(e))
        .filter((e) => !emails.includes(e));
      
      setEmails([...emails, ...newEmails.slice(0, 100 - emails.length)]);
      setSuccess(`已粘贴 ${newEmails.length} 个邮箱`);
      setTimeout(() => setSuccess(null), 3000);
    } catch {
      setError('无法读取剪贴板');
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">✉️ 邮箱验证</h1>
            <p className="text-gray-600">
              批量验证邮箱有效性，检查黑名单状态
            </p>
          </div>

          {/* Error and Success Alerts */}
          <div className="space-y-4 mb-8">
            {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
            {success && (
              <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Input Section */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">添加邮箱</h2>

                <div className="space-y-4">
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                      邮箱地址
                    </label>
                    <input
                      id="email"
                      type="email"
                      value={emailInput}
                      onChange={(e) => setEmailInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addEmail()}
                      placeholder="user@example.com"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                      disabled={isLoading}
                    />
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={addEmail}
                      disabled={isLoading}
                      className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      添加
                    </button>
                    <button
                      onClick={handlePaste}
                      disabled={isLoading}
                      className="flex-1 bg-gray-500 hover:bg-gray-600 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      粘贴
                    </button>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      id="blacklist"
                      type="checkbox"
                      checked={checkBlacklist}
                      onChange={(e) => setCheckBlacklist(e.target.checked)}
                      className="w-4 h-4 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
                      disabled={isLoading}
                    />
                    <label htmlFor="blacklist" className="text-sm text-gray-700">
                      检查黑名单
                    </label>
                  </div>

                  <button
                    onClick={handleValidate}
                    disabled={isLoading || emails.length === 0}
                    className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition-all"
                  >
                    {isLoading ? '验证中...' : `验证 (${emails.length})`}
                  </button>

                  <button
                    onClick={() => setEmails([])}
                    disabled={isLoading || emails.length === 0}
                    className="w-full bg-gray-300 hover:bg-gray-400 disabled:opacity-50 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    清空
                  </button>
                </div>

                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>提示：</strong>支持批量添加，可以粘贴用空格/逗号分隔的邮箱列表
                  </p>
                </div>
              </div>
            </div>

            {/* Email List and Results */}
            <div className="lg:col-span-2 space-y-8">
              {/* Email List */}
              {emails.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">待验证邮箱 ({emails.length})</h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {emails.map((email) => (
                      <div
                        key={email}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                      >
                        <span className="text-sm text-gray-700">{email}</span>
                        <button
                          onClick={() => removeEmail(email)}
                          className="text-red-500 hover:text-red-700 font-bold"
                          disabled={isLoading}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Results */}
              {isLoading && <LoadingSpinner />}

              {results.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">验证结果</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {results.map((result) => (
                      <div
                        key={result.email}
                        className={`p-4 rounded-lg border-l-4 ${
                          result.is_valid
                            ? result.is_blacklisted
                              ? 'bg-yellow-50 border-yellow-400'
                              : 'bg-green-50 border-green-400'
                            : 'bg-red-50 border-red-400'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-mono text-sm font-semibold text-gray-900">
                              {result.email}
                            </p>
                            <div className="mt-2 flex items-center space-x-4 text-xs">
                              <span
                                className={
                                  result.is_valid
                                    ? 'text-green-700 font-semibold'
                                    : 'text-red-700 font-semibold'
                                }
                              >
                                {result.is_valid ? '✓ 有效' : '✗ 无效'}
                              </span>
                              {result.is_blacklisted && (
                                <span className="text-yellow-700 font-semibold">
                                  ⚠️ 在黑名单中
                                </span>
                              )}
                              <span className="text-gray-600">
                                置信度: {(result.confidence_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            {result.reason && (
                              <p className="mt-2 text-xs text-gray-600">{result.reason}</p>
                            )}
                          </div>
                          <button
                            onClick={() => copyToClipboard(result.email)}
                            className="text-blue-500 hover:text-blue-700 font-bold text-lg ml-2"
                            title="复制邮箱"
                          >
                            📋
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Summary */}
                  <div className="mt-6 pt-6 border-t grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-gray-600 text-sm mb-1">有效邮箱</p>
                      <p className="text-2xl font-bold text-green-600">
                        {results.filter((r) => r.is_valid && !r.is_blacklisted).length}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-600 text-sm mb-1">风险邮箱</p>
                      <p className="text-2xl font-bold text-yellow-600">
                        {results.filter((r) => r.is_blacklisted).length}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-600 text-sm mb-1">无效邮箱</p>
                      <p className="text-2xl font-bold text-red-600">
                        {results.filter((r) => !r.is_valid).length}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
  );
}
