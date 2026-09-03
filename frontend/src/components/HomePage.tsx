import { useEffect, useState } from 'react';
import { getTodayAttendance } from '../services/parent';
import type { Child, TodayAttendance } from '../types';

interface HomePageProps {
  greeting: string;
  parentName: string;
  totalChildren: number;
  presentCount: number;
  child: Child;
  children: Child[];
  onSelectChild: (c: Child) => void;
  onLogout: () => void;
}

const statusConfig: Record<string, { emoji: string; color: string; label: string }> = {
  present: { emoji: '🟢', color: 'text-status-present', label: 'Maktabda' },
  absent: { emoji: '🔴', color: 'text-status-absent', label: 'Maktabga kelmagan' },
  late: { emoji: '🟠', color: 'text-status-late', label: 'Kechikkan' },
  excused: { emoji: '🔵', color: 'text-status-excused', label: 'Sababli' },
  no_data: { emoji: '⚪', color: 'text-dark-muted', label: 'Davomat belgilanmagan' },
};

export default function HomePage({
  greeting,
  parentName,
  totalChildren,
  presentCount,
  child,
  children,
  onSelectChild,
  onLogout,
}: HomePageProps) {
  const [today, setToday] = useState<TodayAttendance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setLoading(true);
      try {
        const data = await getTodayAttendance(child.id);
        if (mounted) setToday(data);
      } catch (e) {
        // ignore
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [child.id]);

  const config = statusConfig[child.attendance_status || 'no_data'] || statusConfig.no_data;

  return (
    <div className="space-y-5 animate-fade-up">
      <header className="flex justify-between items-start">
        <div>
          <p className="text-lg font-semibold">{greeting},</p>
          <p className="text-xl font-bold">{parentName}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onLogout}
            className="bg-dark-card border border-dark-border rounded-xl px-3 py-2 text-sm text-dark-muted active:scale-95 transition-all"
          >
            ⏻
          </button>
        </div>
      </header>

      <div className="card bg-primary-600/10 border-primary-600/20">
        <p className="text-sm text-dark-muted">
          {presentCount} / {totalChildren}{' '}
          {totalChildren === 1 ? 'farzand' : 'farzand'} hozir maktabda
        </p>
      </div>

      {totalChildren > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {children.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelectChild(c)}
              className={`px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-all ${
                c.id === child.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-card border border-dark-border text-dark-muted'
              }`}
            >
              {c.first_name}
            </button>
          ))}
        </div>
      )}

      <section>
        <h2 className="text-sm font-semibold text-dark-muted mb-3">BUGUNGI HOLAT</h2>
        <div className="card space-y-4">
          <div>
            <p className="text-lg font-bold">{child.first_name}</p>
            <p className="text-dark-muted">{child.last_name}</p>
          </div>
          <p className="text-sm text-dark-muted">
            {child.class_name || 'Sinf noma\'lum'} • {child.school_name || ''}
          </p>
          <div className="flex items-center justify-between">
            <div className={`flex items-center gap-2 font-medium ${config.color}`}>
              <span className="text-xl">{config.emoji}</span>
              <span>{config.label}</span>
            </div>
            <div className="flex items-center gap-1">
              {loading ? (
                <span className="text-sm text-dark-muted">...</span>
              ) : (
                <>
                  <span className="text-sm text-dark-muted">⏰</span>
                  <span className="text-sm font-medium">
                    {today?.status === 'present' || today?.status === 'late'
                      ? today.arrival_time || '--:--'
                      : '--:--'}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
