import { useState } from 'react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export default function ErrorState({ message = 'Ma\'lumotni yuklashda xatolik yuz berdi.', onRetry }: ErrorStateProps) {
  const [showRetry] = useState(true);
  void showRetry;

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4 text-center">
      <div className="text-5xl">⚠️</div>
      <p className="text-dark-muted max-w-xs">{message}</p>
      <p className="text-sm text-dark-muted">Internet aloqasini tekshirib qayta urinib ko'ring.</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-primary mt-2">
          🔄 Qayta urinish
        </button>
      )}
    </div>
  );
}
