'use client';

import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function Home() {
  const [status, setStatus] = useState<string>('未检查');
  const [result, setResult] = useState<string>('');

  async function checkBackend() {
    setStatus('检查中...');
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setStatus(data.ok ? '后端正常' : '后端异常');
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setStatus('连接失败');
      setResult(String(error));
    }
  }

  async function inspectExcel(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    setResult('正在读取表格...');
    try {
      const response = await fetch(`${API_BASE}/files/inspect-excel`, {
        method: 'POST',
        body: form,
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult(String(error));
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6 text-gray-800">系统检查</h1>

      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">系统检查</h2>
          <div className="flex gap-4 mb-4">
            <button
              onClick={checkBackend}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              检查后端
            </button>
            <label className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 cursor-pointer transition-colors">
              上传 Excel
              <input
                type="file"
                accept=".xlsx,.xlsm"
                onChange={inspectExcel}
                className="hidden"
              />
            </label>
          </div>
          <div className="mb-4">
            <p className="text-sm text-gray-600">
              状态: <span className="font-medium">{status}</span>
            </p>
          </div>
          {result && (
            <div className="bg-gray-50 rounded p-4 max-h-96 overflow-auto">
              <pre className="text-xs">{result}</pre>
            </div>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            📋 快速导航
          </h3>
          <div className="space-y-2 text-sm text-blue-800">
            <p>• YouTube KOL 搜索 - 批量搜索 YouTube 创作者并管理候选名单</p>
            <p>• YouTube 关键词拓展 - 使用 DataForSEO 拓展关键词并搜索视频</p>
            <p>• 系统设置 - 配置 API 密钥、SMTP 邮箱、过滤规则等</p>
          </div>
        </div>
      </div>
    </div>
  );
}
