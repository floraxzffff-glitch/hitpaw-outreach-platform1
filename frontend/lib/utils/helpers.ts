/**
 * 工具函数库
 */

/**
 * 格式化日期
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * 格式化百分比
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return (value * 100).toFixed(decimals) + '%';
}

/**
 * 获取等级颜色
 */
export function getLevelColor(level: 'A' | 'B' | 'C' | string): string {
  switch (level) {
    case 'A':
      return 'bg-green-100 text-green-800 border-green-300';
    case 'B':
      return 'bg-blue-100 text-blue-800 border-blue-300';
    case 'C':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300';
  }
}

/**
 * 获取等级徽章标签
 */
export function getLevelBadge(level: 'A' | 'B' | 'C' | string): string {
  switch (level) {
    case 'A':
      return '⭐ 优先';
    case 'B':
      return '✓ 可行';
    case 'C':
      return '○ 参考';
    default:
      return level;
  }
}

/**
 * 验证邮箱格式
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证 URL
 */
export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number = 50): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * 复制到剪贴板
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

/**
 * 下载文件
 */
export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * 获取源类型标签
 */
export function getSourceLabel(source: string): string {
  const labels: Record<string, string> = {
    youtube: '🎥 YouTube',
    article: '📝 文章',
    seo: '🔍 SEO',
  };
  return labels[source] || source;
}

/**
 * 格式化大数字
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('en-US');
}

/**
 * 延迟函数（用于 demo）
 */
export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 生成随机颜色
 */
export function getRandomColor(): string {
  const colors = [
    'bg-red-100 text-red-800',
    'bg-blue-100 text-blue-800',
    'bg-green-100 text-green-800',
    'bg-yellow-100 text-yellow-800',
    'bg-purple-100 text-purple-800',
    'bg-pink-100 text-pink-800',
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}
