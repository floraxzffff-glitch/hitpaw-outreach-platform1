'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-8 text-center">
      <h2 className="text-lg font-semibold text-gray-900 mb-2">页面出错了</h2>
      <p className="text-sm text-gray-500 mb-6 max-w-md break-words">
        {error.message || '发生未知错误'}
      </p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
      >
        重试
      </button>
    </div>
  );
}
