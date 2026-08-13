/**
 * 通用加载指示器
 */

export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-8 space-y-3">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 border-r-blue-500 animate-spin"></div>
      </div>
      <p className="text-gray-600 font-medium">正在处理中...</p>
    </div>
  );
}
