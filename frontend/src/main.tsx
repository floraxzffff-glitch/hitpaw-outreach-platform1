import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

type Page = 'home' | 'youtube' | 'youtube-expansion' | 'settings';

function App() {
  const [status, setStatus] = useState<string>("未检查");
  const [result, setResult] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<Page>('home');

  async function checkBackend() {
    setStatus("检查中...");
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setStatus(data.ok ? "后端正常" : "后端异常");
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setStatus("连接失败");
      setResult(String(error));
    }
  }

  async function inspectExcel(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setResult("正在读取表格...");
    try {
      const response = await fetch(`${API_BASE}/files/inspect-excel`, {
        method: "POST",
        body: form,
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult(String(error));
    }
  }

  const renderPage = () => {
    if (currentPage === 'youtube-expansion') {
      return (
        <div className="page-container">
          <h2>🎯 YouTube 关键词拓展+视频搜索</h2>
          <p className="text-gray-600 mb-4">
            使用 YouTube Data API v3 进行视频搜索，可选 DataForSEO 进行关键词拓展
          </p>
          <div className="info-box">
            <h3>功能说明</h3>
            <ul>
              <li>✓ 从种子关键词自动拓展相关关键词</li>
              <li>✓ 使用 YouTube Data API v3 搜索视频</li>
              <li>✓ VPH (观看数/小时数) 筛选</li>
              <li>✓ 频道去重和汇总统计</li>
              <li>✓ 导出 Excel 结果 (双表)</li>
            </ul>
            <p className="mt-4">
              <strong>访问完整功能：</strong><br/>
              请访问 <a href="/app/youtube-expansion/page.tsx" className="text-blue-500">YouTube 关键词拓展页面</a>
            </p>
          </div>
        </div>
      );
    }

    if (currentPage === 'youtube') {
      return (
        <div className="page-container">
          <h2>🎥 YouTube KOL 搜索 (原版)</h2>
          <p className="text-gray-600 mb-4">
            使用 yt-dlp 进行 YouTube 搜索，写入 VikPea 工作表
          </p>
          <div className="info-box">
            <p>
              <strong>访问完整功能：</strong><br/>
              请访问 <a href="/app/youtube/page.tsx" className="text-blue-500">YouTube KOL 搜索页面</a>
            </p>
          </div>
        </div>
      );
    }

    if (currentPage === 'settings') {
      return (
        <div className="page-container">
          <h2>⚙️ 系统设置</h2>
          <p className="text-gray-600 mb-4">配置 API 密钥和搜索参数</p>
          <div className="info-box">
            <p>
              <strong>访问完整功能：</strong><br/>
              请访问 <a href="/app/settings/page.tsx" className="text-blue-500">设置页面</a>
            </p>
          </div>
        </div>
      );
    }

    return (
      <section>
        <div className="toolbar">
          <button onClick={checkBackend}>检查后端</button>
          <label>
            上传 Excel
            <input type="file" accept=".xlsx,.xlsm" onChange={inspectExcel} />
          </label>
        </div>

        <div className="panel">
          <h2>状态</h2>
          <p>{status}</p>
        </div>

        <div className="panel">
          <h2>输出</h2>
          <pre>{result || "先检查后端，或上传一个 Excel 表格。"}</pre>
        </div>
      </section>
    );
  };

  return (
    <main>
      <aside>
        <h1>HitPaw Outreach</h1>
        <p>云端外联工作台 V2</p>
        <nav style={{ marginTop: '2rem' }}>
          <button
            onClick={() => setCurrentPage('home')}
            className={currentPage === 'home' ? 'nav-active' : ''}
            style={{ display: 'block', width: '100%', marginBottom: '0.5rem', padding: '0.5rem', textAlign: 'left' }}
          >
            🏠 首页
          </button>
          <button
            onClick={() => setCurrentPage('youtube')}
            className={currentPage === 'youtube' ? 'nav-active' : ''}
            style={{ display: 'block', width: '100%', marginBottom: '0.5rem', padding: '0.5rem', textAlign: 'left' }}
          >
            🎥 YouTube KOL 搜索
          </button>
          <button
            onClick={() => setCurrentPage('youtube-expansion')}
            className={currentPage === 'youtube-expansion' ? 'nav-active' : ''}
            style={{ display: 'block', width: '100%', marginBottom: '0.5rem', padding: '0.5rem', textAlign: 'left' }}
          >
            🎯 YouTube 关键词拓展
          </button>
          <button
            onClick={() => setCurrentPage('settings')}
            className={currentPage === 'settings' ? 'nav-active' : ''}
            style={{ display: 'block', width: '100%', marginBottom: '0.5rem', padding: '0.5rem', textAlign: 'left' }}
          >
            ⚙️ 设置
          </button>
        </nav>
      </aside>

      {renderPage()}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
