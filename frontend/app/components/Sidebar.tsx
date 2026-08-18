/**
 * 侧边导航栏 —— 全局唯一，分组展示所有功能
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

type NavItem = { label: string; href: string; icon: string };
type NavGroup = { title: string; items: NavItem[] };

const NAV_GROUPS: NavGroup[] = [
  {
    title: '概览',
    items: [{ label: '仪表板', href: '/dashboard', icon: '📊' }],
  },
  {
    title: 'KOL 开发',
    items: [
      { label: 'YouTube 搜索', href: '/youtube', icon: '🎥' },
      { label: 'DataForSEO 深度分析', href: '/dataforseo', icon: '🔬' },
      { label: '邮件模板', href: '/templates', icon: '📧' },
      { label: '发送开发信', href: '/send', icon: '📮' },
      { label: '发送追踪', href: '/tracker', icon: '📈' },
    ],
  },
  {
    title: '关键词与内容',
    items: [
      { label: '关键词分析', href: '/analyze', icon: '🔍' },
      { label: 'SEO 扫描', href: '/seo', icon: '🔎' },
      { label: '邮箱验证', href: '/email', icon: '✉️' },
      { label: '报告', href: '/reports', icon: '📄' },
    ],
  },
  {
    title: '系统',
    items: [{ label: '系统设置', href: '/settings', icon: '⚙️' }],
  },
];

function NavLink({ item, active, onClick }: { item: NavItem; active: boolean; onClick?: () => void }) {
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        active
          ? 'bg-indigo-50 text-indigo-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      <span className="text-base leading-none">{item.icon}</span>
      <span className="truncate">{item.label}</span>
    </Link>
  );
}

function SidebarContent({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return (
    <div className="flex flex-col h-full">
      <Link href="/dashboard" className="flex items-center gap-2 px-4 h-16 shrink-0 border-b border-gray-200">
        <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-lg flex items-center justify-center text-white font-bold text-sm">
          V
        </div>
        <span className="text-base font-bold text-gray-900">VikPea</span>
      </Link>
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {NAV_GROUPS.map((group) => (
          <div key={group.title}>
            <p className="px-3 mb-1.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              {group.title}
            </p>
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.href}
                  item={item}
                  active={pathname === item.href}
                  onClick={onNavigate}
                />
              ))}
            </div>
          </div>
        ))}
      </nav>
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* 桌面端：固定侧边栏 */}
      <aside className="hidden md:flex md:w-60 md:shrink-0 md:flex-col md:fixed md:inset-y-0 md:left-0 bg-white border-r border-gray-200 z-30">
        <SidebarContent pathname={pathname} />
      </aside>

      {/* 移动端：顶栏 + 抽屉 */}
      <div className="md:hidden sticky top-0 z-40 flex items-center justify-between h-14 px-4 bg-white border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-lg flex items-center justify-center text-white font-bold text-xs">
            V
          </div>
          <span className="text-sm font-bold text-gray-900">VikPea</span>
        </Link>
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-md text-gray-600 hover:bg-gray-100"
          aria-label="打开菜单"
        >
          <svg className="h-5 w-5" stroke="currentColor" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/30" onClick={() => setMobileOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-64 bg-white shadow-xl">
            <SidebarContent pathname={pathname} onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}
    </>
  );
}
