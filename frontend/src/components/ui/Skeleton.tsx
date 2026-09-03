interface SkeletonProps {
  lines?: number;
  className?: string;
}

export default function Skeleton({ lines = 3, className = '' }: SkeletonProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton h-16"></div>
      ))}
    </div>
  );
}
