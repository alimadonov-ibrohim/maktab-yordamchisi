export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-dark-bg flex flex-col items-center justify-center gap-4">
      <div className="w-16 h-16 rounded-full border-4 border-dark-border border-t-primary-500 animate-spin"></div>
      <p className="text-dark-muted">Yuklanmoqda...</p>
    </div>
  );
}
