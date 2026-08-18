'use client'

import { useState } from 'react'

export default function DataForSEOPage() {
  const [activeTab, setActiveTab] = useState<'test' | 'keywords' | 'google' | 'youtube'>('test')

  // 测试连接
  const [testLogin, setTestLogin] = useState('')
  const [testPassword, setTestPassword] = useState('')
  const [testResult, setTestResult] = useState<any>(null)
  const [testLoading, setTestLoading] = useState(false)

  // 关键词研究
  const [seedKeyword, setSeedKeyword] = useState('')
  const [keywordResults, setKeywordResults] = useState<any>(null)
  const [keywordLoading, setKeywordLoading] = useState(false)

  // Google搜索KOL网站
  const [niche, setNiche] = useState('')
  const [googleResults, setGoogleResults] = useState<any>(null)
  const [googleLoading, setGoogleLoading] = useState(false)

  // YouTube视频搜索
  const [youtubeKeyword, setYoutubeKeyword] = useState('')
  const [youtubeResults, setYoutubeResults] = useState<any>(null)
  const [youtubeLoading, setYoutubeLoading] = useState(false)

  const handleTest = async () => {
    if (!testLogin || !testPassword) {
      alert('请输入登录凭证')
      return
    }

    setTestLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/dataforseo/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login: testLogin, password: testPassword })
      })
      const result = await response.json()
      setTestResult(result)
    } catch (error: any) {
      setTestResult({ success: false, message: error.message })
    } finally {
      setTestLoading(false)
    }
  }

  const handleKeywordResearch = async () => {
    if (!seedKeyword) {
      alert('请输入种子关键词')
      return
    }

    setKeywordLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/dataforseo/keyword-research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          seed_keyword: seedKeyword,
          language_code: 'en',
          location_code: 2840,
          limit: 100
        })
      })
      const result = await response.json()
      setKeywordResults(result)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setKeywordLoading(false)
    }
  }

  const handleGoogleSearch = async () => {
    if (!niche) {
      alert('请输入行业/领域')
      return
    }

    setGoogleLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/dataforseo/find-influencer-websites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          niche: niche,
          language_code: 'en',
          location_code: 2840,
          depth: 20
        })
      })
      const result = await response.json()
      setGoogleResults(result)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setGoogleLoading(false)
    }
  }

  const handleYoutubeSearch = async () => {
    if (!youtubeKeyword) {
      alert('请输入搜索关键词')
      return
    }

    setYoutubeLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/dataforseo/youtube-video-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: youtubeKeyword,
          language_code: 'en',
          location_code: 2840,
          depth: 20
        })
      })
      const result = await response.json()
      setYoutubeResults(result)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setYoutubeLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">多渠道KOL发现工具</h1>
      <p className="text-gray-600 mb-6">使用DataForSEO进行关键词研究、Google搜索、YouTube视频搜索</p>

      <div className="mb-6 border-b">
        <nav className="flex space-x-4">
          <button
            className={`px-4 py-2 ${activeTab === 'test' ? 'border-b-2 border-blue-500 font-semibold' : ''}`}
            onClick={() => setActiveTab('test')}
          >
            🔌 连接测试
          </button>
          <button
            className={`px-4 py-2 ${activeTab === 'keywords' ? 'border-b-2 border-blue-500 font-semibold' : ''}`}
            onClick={() => setActiveTab('keywords')}
          >
            🔍 关键词研究
          </button>
          <button
            className={`px-4 py-2 ${activeTab === 'google' ? 'border-b-2 border-blue-500 font-semibold' : ''}`}
            onClick={() => setActiveTab('google')}
          >
            🌐 Google找KOL
          </button>
          <button
            className={`px-4 py-2 ${activeTab === 'youtube' ? 'border-b-2 border-blue-500 font-semibold' : ''}`}
            onClick={() => setActiveTab('youtube')}
          >
            📺 YouTube发现
          </button>
        </nav>
      </div>

      {/* 连接测试 */}
      {activeTab === 'test' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">测试 DataForSEO API 连接</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">登录邮箱</label>
              <input
                type="text"
                className="w-full border rounded px-3 py-2"
                value={testLogin}
                onChange={(e) => setTestLogin(e.target.value)}
                placeholder="your-email@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">密码</label>
              <input
                type="password"
                className="w-full border rounded px-3 py-2"
                value={testPassword}
                onChange={(e) => setTestPassword(e.target.value)}
                placeholder="your-password"
              />
            </div>

            <button
              onClick={handleTest}
              disabled={testLoading}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
            >
              {testLoading ? '测试中...' : '测试连接'}
            </button>
          </div>

          {testResult && (
            <div className={`mt-4 p-4 rounded ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(testResult, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      {/* 关键词研究 */}
      {activeTab === 'keywords' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">关键词研究</h2>
          <p className="text-gray-600 mb-4">输入种子关键词，找到相关的高价值关键词，然后用这些关键词在YouTube API中搜索频道</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">种子关键词</label>
              <input
                type="text"
                className="w-full border rounded px-3 py-2"
                value={seedKeyword}
                onChange={(e) => setSeedKeyword(e.target.value)}
                placeholder="例如: tech review, gaming, cooking"
              />
            </div>

            <button
              onClick={handleKeywordResearch}
              disabled={keywordLoading}
              className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              {keywordLoading ? '搜索中...' : '开始研究'}
            </button>
          </div>

          {keywordResults && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">找到 {keywordResults.total} 个关键词</h3>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border px-4 py-2">关键词</th>
                      <th className="border px-4 py-2">搜索量</th>
                      <th className="border px-4 py-2">竞争度</th>
                      <th className="border px-4 py-2">CPC</th>
                    </tr>
                  </thead>
                  <tbody>
                    {keywordResults.keywords?.map((kw: any, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="border px-4 py-2">{kw.keyword}</td>
                        <td className="border px-4 py-2">{kw.search_volume?.toLocaleString()}</td>
                        <td className="border px-4 py-2">{kw.competition}</td>
                        <td className="border px-4 py-2">${kw.cpc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Google搜索KOL */}
      {activeTab === 'google' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">Google搜索找KOL</h2>
          <p className="text-gray-600 mb-4">在Google上搜索博主/KOL的个人网站、YouTube频道、博客等</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">行业/领域</label>
              <input
                type="text"
                className="w-full border rounded px-3 py-2"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                placeholder="例如: tech blogger, gaming youtuber, food influencer"
              />
            </div>

            <button
              onClick={handleGoogleSearch}
              disabled={googleLoading}
              className="bg-purple-600 text-white px-6 py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
            >
              {googleLoading ? '搜索中...' : '开始搜索'}
            </button>
          </div>

          {googleResults && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">找到 {googleResults.total} 个网站</h3>
              <div className="space-y-3">
                {googleResults.websites?.map((site: any, idx: number) => (
                  <div key={idx} className="border rounded p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-blue-600">
                          <a href={site.url} target="_blank" rel="noopener noreferrer">
                            {site.title}
                          </a>
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">{site.description}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          域名: {site.domain} | 类型: {site.type}
                        </p>
                        {site.youtube_channel_id && (
                          <p className="text-xs text-green-600 mt-1">
                            ✅ YouTube频道ID: {site.youtube_channel_id}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* YouTube视频搜索 */}
      {activeTab === 'youtube' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-2">YouTube视频搜索</h2>
          <p className="text-gray-600 mb-4">搜索YouTube视频，从中提取频道ID（间接发现频道）</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">搜索关键词</label>
              <input
                type="text"
                className="w-full border rounded px-3 py-2"
                value={youtubeKeyword}
                onChange={(e) => setYoutubeKeyword(e.target.value)}
                placeholder="例如: unboxing, tutorial, review"
              />
            </div>

            <button
              onClick={handleYoutubeSearch}
              disabled={youtubeLoading}
              className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700 disabled:bg-gray-400"
            >
              {youtubeLoading ? '搜索中...' : '开始搜索'}
            </button>
          </div>

          {youtubeResults && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">找到 {youtubeResults.total} 个频道（已去重）</h3>
              <div className="space-y-3">
                {youtubeResults.channels?.map((channel: any, idx: number) => (
                  <div key={idx} className="border rounded p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-red-600">
                          <a href={channel.channel_url} target="_blank" rel="noopener noreferrer">
                            {channel.channel_name}
                          </a>
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">频道ID: {channel.channel_id}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          示例视频: {channel.example_video_title} ({channel.example_video_views?.toLocaleString()} 观看)
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
