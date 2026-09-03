interface EmptyStateProps {
  message: string;
}

export default function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3 text-center">
      <div className="text-4xl">📭</div>
      <p className="text-dark-muted">{message}</p>
    </div>
  );
}
