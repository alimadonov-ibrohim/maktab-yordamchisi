import { useEffect, useState } from 'react';
import { getTodayAttendance } from '../services/parent';
import Skeleton from './ui/Skeleton';
import ErrorState from './ui/ErrorState';
import type { Child, TodayAttendance } from '../types';

interface TodayPageProps {
  child: Child;
}

const statusDisplay: Record<string, { emoji: string; color: string; label: string; desc: string }> = {
  present: {
    emoji: '🟢',
    color: 'text-status-present',
    label: 'Maktabga keldi',
    desc: 'Sinfda',
  },
  absent: {
    emoji: '🔴',
    color: 'text-status-absent',
    label: 'Kelmagan',
    desc: 'Bugungi darsda qatnashmadi',
  },
  late: {
    emoji: '🟠',
    color: 'text-status-late',
    label: 'Kechikkan',
    desc: 'Kechikib keldi',
  },
  excused: {
    emoji: '🔵',
    color: 'text-status-excused',
    label: 'Sababli',
    desc: 'Sababli sababli',
  },
  no_data: {
    emoji: '⚪',
    color: 'text-dark-muted',
    label: 'Davomat belgilanmagan',
    desc: '',
  },
};

export default function TodayPage({ child }: TodayPageProps) {
  const [today, setToday] = useState<TodayAttendance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getTodayAttendance(child.id);
      setToday(data);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [child.id]);

  if (loading) {
    return (
      <div className="animate-fade-up">
        <h2 className="text-2xl font-bold mb-4">📅 Bugun</h2>
        <Skeleton lines={3} />
      </div>
    );
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  const config = statusDisplay[today?.status || 'no_data'] || statusDisplay.no_data;
  const todayDate = today?.date || new Date().toISOString().slice(0, 10);
  const formatted = new Date(todayDate + 'T00:00:00').toLocaleDateString('uz-UZ', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="space-y-5 animate-fade-up">
      <div>
        <h2 className="text-2xl font-bold">📅 Bugun</h2>
        <p className="text-dark-muted text-sm capitalize">{formatted}</p>
      </div>

      <section>
        <h3 className="text-sm font-semibold text-dark-muted mb-3">FARZAND</h3>
        <div className="card space-y-1">
          <p className="text-lg font-bold">
            {child.first_name} {child.last_name}
          </p>
          <p className="text-sm text-dark-muted">
            {child.class_name || 'Sinf noma\'lum'}
          </p>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-dark-muted mb-3">
          BUGUNGI DARS YOKI DAVOMAT
        </h3>
        <div className="card">
          <div className={`flex items-center gap-3 ${config.color}`}>
            <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center text-3xl">
              {config.emoji}
            </div>
            <div>
              <p className="font-semibold text-lg">{config.label}</p>
              {today?.arrival_time && (
                <p className="text-sm text-dark-muted">
                  ⏰ {today.arrival_time}
                </p>
              )}
            </div>
          </div>

          {today?.status === 'late' && today.late_minutes > 0 && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <p className="text-sm text-status-late">
                🟠 {today.arrival_time} da keldi
              </p>
              <p className="text-sm text-dark-muted">
                {today.late_minutes} daqiqa kechikdi
              </p>
            </div>
          )}

          {today?.status === 'present' && today.departure_time && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <p className="text-sm text-dark-muted">
                🔵 Maktabdan chiqdi: {today.departure_time}
              </p>
            </div>
          )}

          {today?.status === 'excused' && today.reason && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <p className="text-sm text-dark-muted">
                📝 Sabab: {today.reason}
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
