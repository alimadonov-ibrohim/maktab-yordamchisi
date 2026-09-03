import { useEffect, useState } from 'react';
import {
  getAdminStats, getSchools, getClasses, getStudents,
  getTeachers, getParents,
} from '../services/admin';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, CartesianGrid, Tooltip, Cell } from 'recharts';
import Skeleton from './ui/Skeleton';
import ErrorState from './ui/ErrorState';
import type { AdminStats } from '../services/admin';

interface DashboardPageProps {
  role: string;
}

export default function DashboardPage({ role }: DashboardPageProps) {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [s] = await Promise.all([
        getAdminStats(),
        getSchools(),
        getClasses(),
        getStudents(),
        getTeachers(),
        getParents(),
      ]);
      setStats(s);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div>
        <h2 className="text-xl font-bold mb-4">📊 Dashboard</h2>
        <Skeleton lines={5} />
      </div>
    );
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  if (!stats) return null;

  const chartData = [
    { name: 'Kelgan', value: stats.today_present, color: '#22c55e' },
    { name: 'Kelmagan', value: stats.today_absent, color: '#ef4444' },
    { name: 'Kechikkan', value: stats.today_late, color: '#f97316' },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-5 animate-fade-up">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">📊 Dashboard</h2>
        <span className="text-xs bg-primary-600/20 text-primary-400 px-3 py-1 rounded-full uppercase">
          {role}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="card flex items-center gap-3">
          <div className="text-3xl">🏫</div>
          <div>
            <p className="text-2xl font-bold">{stats.total_schools}</p>
            <p className="text-sm text-dark-muted">Maktab</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="text-3xl">👨‍🎓</div>
          <div>
            <p className="text-2xl font-bold">{stats.total_students}</p>
            <p className="text-sm text-dark-muted">O'quvchi</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="text-3xl">👨‍🏫</div>
          <div>
            <p className="text-2xl font-bold">{stats.total_teachers}</p>
            <p className="text-sm text-dark-muted">O'qituvchi</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="text-3xl">👨‍👩‍👧</div>
          <div>
            <p className="text-2xl font-bold">{stats.total_parents}</p>
            <p className="text-sm text-dark-muted">Ota-ona</p>
          </div>
        </div>
      </div>

      <div className="card">
        <p className="font-semibold mb-2">Bugungi davomat</p>
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center">
            <p className="text-2xl font-bold text-status-present">🟢 {stats.today_present}</p>
            <p className="text-xs text-dark-muted">Kelgan</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-status-absent">🔴 {stats.today_absent}</p>
            <p className="text-xs text-dark-muted">Kelmagan</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-status-late">🟠 {stats.today_late}</p>
            <p className="text-xs text-dark-muted">Kechikkan</p>
          </div>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="card">
          <p className="font-semibold mb-3">📈 Bugungi davomat grafigi</p>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
              <XAxis dataKey="name" stroke="#888" tick={{ fill: '#888' }} />
              <YAxis allowDecimals={false} stroke="#888" tick={{ fill: '#888' }} />
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
    </div>
  );
}
