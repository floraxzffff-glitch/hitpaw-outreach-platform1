'use client';

interface SuccessAlertProps {
  message: string;
  onDismiss: () => void;
}

export default function SuccessAlert({ message, onDismiss }: SuccessAlertProps) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start justify-between">
      <div className="flex items-start">
        <span className="text-green-600 text-lg mr-2">✓</span>
        <p className="text-sm text-green-800">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-green-400 hover:text-green-600 ml-4"
      >
        ✕
      </button>
    </div>
  );
}
