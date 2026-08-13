/**
 * 成功提示组件
 */

interface SuccessAlertProps {
  message: string;
  onDismiss?: () => void;
}

export default function SuccessAlert({ message, onDismiss }: SuccessAlertProps) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start space-x-3">
      <div className="text-2xl">✓</div>
      <div className="flex-1">
        <p className="text-green-700 font-medium">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-green-500 hover:text-green-700 font-bold text-lg"
        >
          ✕
        </button>
      )}
    </div>
  );
}
