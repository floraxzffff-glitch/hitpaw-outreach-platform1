import './globals.css';
import { Sidebar } from './components/Sidebar';

export const metadata = {
  title: 'HitPaw Outreach 工作台',
  description: '云端外联工作台 V2',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="flex min-h-screen bg-gray-50">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
