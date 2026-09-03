import { useCallback, useEffect, useMemo, useState } from 'react';
import { getStatistics, getMonthlyAttendance } from '../services/parent';
import { BarChart, Bar, Cell, XAxis, YAxis, ResponsiveContainer, CartesianGrid, Tooltip } from 'recharts';
import Skeleton from './ui/Skeleton';
import ErrorState from './ui/ErrorState';
import EmptyState from './ui/EmptyState';
import type { Child, Statistics, MonthlyDay } from '../types';

interface StatsPageProps {
  child: Child;
}

const monthNames = [
  'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
  'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr',
];

export default function StatsPage({ child }: StatsPageProps) {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [stats, setStats] = useState<Statistics | null>(null);
  const [days, setDays] = useState<MonthlyDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDay, setSelectedDay] = useState<MonthlyDay | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [s, d] = await Promise.all([
        getStatistics(child.id, month, year),
        getMonthlyAttendance(child.id, month, year),
      ]);
      setStats(s);
      setDays(d);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  }, [child.id, month, year]);

  useEffect(() => { load(); }, [load]);

  const prevMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const nextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  const chartData = useMemo(() => {
    return [
      { name: 'Kelgan', value: stats?.present_days || 0, color: '#22c55e' },
      { name: 'Kelmagan', value: stats?.absent_days || 0, color: '#ef4444' },
      { name: 'Kechikkan', value: stats?.late_days || 0, color: '#f97316' },
      { name: 'Sababli', value: stats?.excused_days || 0, color: '#3b82f6' },
    ].filter((d) => d.value > 0);
  }, [stats]);

  if (loading) {
    return (
      <div className="animate-fade-up">
        <Skeleton lines={4} />
      </div>
    );
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  if (!stats) {
    return <EmptyState message="Statistika ma'lumotlari topilmadi." />;
  }

  const levelColor =
    stats.level === 'A\'lo'
      ? 'text-status-present'
      : stats.level === 'Yaxshi'
      ? 'text-status-excused'
      : 'text-status-late';

  return (
    <div className="space-y-5 animate-fade-up">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">📊 Statistika</h2>
      </div>

      <div className="flex items-center justify-between bg-dark-card border border-dark-border rounded-2xl p-2">
        <button onClick={prevMonth} className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center active:scale-95 transition-all">
          ←
        </button>
        <span className="font-semibold">
          {monthNames[month - 1]} {year}
        </span>
        <button onClick={nextMonth} className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center active:scale-95 transition-all">
          →
        </button>
      </div>

      <div className="text-center">
        <p className="text-lg font-bold">
          {child.first_name} {child.last_name}
        </p>
        <p className="text-dark-muted">{child.class_name || ''}</p>
      </div>

      <div className="card text-center space-y-2">
        <p className="text-5xl font-bold text-primary-400">
          {Math.round(stats.attendance_percentage)}%
        </p>
        <p className="font-medium">Davomat</p>
        <p className={`font-medium ${levelColor}`}>{stats.level}</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="card flex items-center gap-3">
          <div className="text-3xl">🔵</div>
          <div>
            <p className="text-sm text-dark-muted">O'quv kunlari</p>
            <p className="text-2xl font-bold">{stats.total_school_days}</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="text-3xl">🟢</div>
          <div>
            <p className="text-sm text-dark-muted">Kelgan</p>
            <p className="text-2xl font-bold">{stats.present_days}</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="text-3xl">🔴</div>
          <div>
            <p className="text-sm text-dark-muted">Kelmagan</p>
            <p className="text-2xl font-bold">{stats.absent_days}</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="text-3xl">🟠</div>
          <div>
            <p className="text-sm text-dark-muted">Kechikkan</p>
            <p className="text-2xl font-bold">{stats.late_days}</p>
          </div>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="card">
          <p className="font-semibold mb-3">📈 Grafik</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
              <XAxis dataKey="name" stroke="#888888" tick={{ fill: '#888888' }} />
              <YAxis allowDecimals={false} stroke="#888888" tick={{ fill: '#888888' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: '12px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {chartData.map((d) => (
                  <Cell key={d.name} fill={d.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {days.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-dark-muted mb-3">KUNLIK TAFSILOT</h3>
          <div className="space-y-2">
            {days.map((d) => {
              const dayNum = new Date(d.date + 'T00:00:00').getDate();
              const emoji = {
                present: '🟢',
                absent: '🔴',
                late: '🟠',
                excused: '🔵',
              }[d.status] || '⚪';
              return (
                <button
                  key={d.date}
                  onClick={() => setSelectedDay(selectedDay?.date === d.date ? null : d)}
                  className="card w-full flex items-center gap-4 active:scale-[0.98] transition-all text-left"
                >
                  <div className="w-10 h-10 rounded-xl bg-white/5 flex flex-col items-center justify-center">
                    <span className="text-sm font-bold">{dayNum}</span>
                    <span className="text-xs text-dark-muted">{d.day_name}</span>
                  </div>
                  <span className="text-xl">{emoji}</span>
                  <span className="font-medium">{d.status}</span>
                  <span className="ml-auto text-sm text-dark-muted">
                    {d.arrival_time || ''}
                  </span>
                </button>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
