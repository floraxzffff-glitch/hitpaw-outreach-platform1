'use client';

interface ErrorAlertProps {
  message: string;
  onDismiss: () => void;
}

export default function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start justify-between">
      <div className="flex items-start">
        <span className="text-red-600 text-lg mr-2">⚠️</span>
        <p className="text-sm text-red-800">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-red-400 hover:text-red-600 ml-4"
      >
        ✕
      </button>
    </div>
  );
}
