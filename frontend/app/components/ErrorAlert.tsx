/**
 * 错误提示组件
 */

interface ErrorAlertProps {
  message: string;
  onDismiss?: () => void;
}

export default function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
      <div className="text-2xl">❌</div>
      <div className="flex-1">
        <h3 className="font-semibold text-red-800 mb-1">出错了</h3>
        <p className="text-red-700 text-sm">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-500 hover:text-red-700 font-bold text-lg"
        >
          ✕
        </button>
      )}
    </div>
  );
}
