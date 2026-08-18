/**
 * 页面布局组件
 */

import type { ReactNode } from 'react';
import Sidebar from './components/Sidebar';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="zh">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="VikPea - 外联工作台，自动化关键词分析和邮箱验证" />
        <meta name="keywords" content="SEO, 关键词分析, 邮箱验证, 自动化" />
        <meta property="og:title" content="VikPea 外联工作台" />
        <meta property="og:description" content="强大的 SEO 和邮箱开发工具" />
        <title>VikPea 外联工作台 | SEO 和邮箱开发平台</title>
      </head>
      <body className="bg-gray-50 text-gray-900">
        <Sidebar />
        <div className="md:pl-60">{children}</div>
      </body>
    </html>
  );
}
