'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Sidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <aside className="w-64 bg-slate-900 text-gray-100 flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-xl font-bold">HitPaw Outreach</h1>
        <p className="text-sm text-gray-400 mt-1">云端外联工作台 V2</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        <Link
          href="/"
          className={`block px-4 py-2.5 rounded-lg transition-colors ${
            isActive('/')
              ? 'bg-blue-500 text-white'
              : 'text-gray-300 hover:bg-slate-800 hover:text-white'
          }`}
        >
          🏠 首页
        </Link>
        <Link
          href="/youtube"
          className={`block px-4 py-2.5 rounded-lg transition-colors ${
            isActive('/youtube')
              ? 'bg-blue-500 text-white'
              : 'text-gray-300 hover:bg-slate-800 hover:text-white'
          }`}
        >
          🎥 YouTube KOL 搜索
        </Link>
        <Link
          href="/youtube-expansion"
          className={`block px-4 py-2.5 rounded-lg transition-colors ${
            isActive('/youtube-expansion')
              ? 'bg-blue-500 text-white'
              : 'text-gray-300 hover:bg-slate-800 hover:text-white'
          }`}
        >
          🎯 YouTube 关键词拓展
        </Link>
        <Link
          href="/settings"
          className={`block px-4 py-2.5 rounded-lg transition-colors ${
            isActive('/settings')
              ? 'bg-blue-500 text-white'
              : 'text-gray-300 hover:bg-slate-800 hover:text-white'
          }`}
        >
          ⚙️ 系统设置
        </Link>
      </nav>
    </aside>
  );
}
