import { useEffect, useState } from 'react';
import { getTeacherClasses, getClassStudents, markAttendance, sendNotification } from '../services/teacher';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import type { TeacherClass, StudentStatus } from '../types';

interface TeacherAppProps {
  role: string;
  onLogout: () => void;
}

const statusConfig: Record<string, { emoji: string; color: string }> = {
  present: { emoji: '🟢', color: 'text-status-present' },
  absent: { emoji: '🔴', color: 'text-status-absent' },
  late: { emoji: '🟠', color: 'text-status-late' },
  excused: { emoji: '🔵', color: 'text-status-excused' },
  no_data: { emoji: '⚪', color: 'text-dark-muted' },
};

export default function TeacherApp({ role, onLogout }: TeacherAppProps) {
  const [classes, setClasses] = useState<TeacherClass[]>([]);
  const [selectedClass, setSelectedClass] = useState<TeacherClass | null>(null);
  const [students, setStudents] = useState<StudentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [section, setSection] = useState('home');
  const [notifTitle, setNotifTitle] = useState('');
  const [notifMsg, setNotifMsg] = useState('');
  const [notifSent, setNotifSent] = useState('');

  const loadClasses = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getTeacherClasses();
      setClasses(data);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClasses();
  }, []);

  const openClass = async (cls: TeacherClass) => {
    setSelectedClass(cls);
    setSection('students');
    setLoading(true);
    setError('');
    try {
      const data = await getClassStudents(cls.id);
      setStudents(data);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  const doMark = async (studentId: number, status: string) => {
    try {
      await markAttendance(studentId, status);
      if (selectedClass) {
        const data = await getClassStudents(selectedClass.id);
        setStudents(data);
      }
    } catch (e) {
      alert('Davomat belgilashda xatolik.');
    }
  };

  const doSendNotification = async () => {
    if (!selectedClass || !notifTitle || !notifMsg) return;
    try {
      await sendNotification(selectedClass.id, notifTitle, notifMsg);
      setNotifSent(`✅ ${selectedClass.name} sinfiga bildirishnoma yuborildi`);
      setNotifTitle('');
      setNotifMsg('');
      setTimeout(() => setNotifSent(''), 4000);
    } catch (e) {
      alert('Xabar yuborishda xatolik.');
    }
  };

  if (error && classes.length === 0) {
    return (
      <div className="min-h-screen bg-dark-bg p-4">
        <ErrorState message={error} onRetry={loadClasses} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-bg p-4 pb-20">
      <div className="max-w-md mx-auto space-y-5 animate-fade-up">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold">
              {role === 'admin' ? '👨‍💼 Admin' : '👨‍🏫 O\'qituvchi'}
            </h1>
            <p className="text-dark-muted text-sm">Maktab Yordamchisi</p>
          </div>
          <button
            onClick={onLogout}
            className="bg-dark-card border border-dark-border rounded-xl px-3 py-2 text-dark-muted active:scale-95 transition-all"
          >
            ⏻
          </button>
        </header>

        {/* Bottom nav */}
        <div className="grid grid-cols-4 gap-2 bg-dark-card border border-dark-border rounded-2xl p-2 fixed bottom-4 left-4 right-4 z-50 max-w-md mx-auto">
          {[
            { key: 'home', label: 'Bosh', icon: '🏠' },
            { key: 'classes', label: 'Sinflar', icon: '📚' },
            { key: 'notif', label: 'Xabar', icon: '📢' },
            { key: 'stats', label: 'Stats', icon: '📊' },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => {
                setSection(t.key);
                if (t.key === 'classes') loadClasses();
              }}
              className={`flex flex-col items-center py-2 rounded-xl text-xs transition-all ${
                section === t.key ? 'bg-primary-600 text-white' : 'text-dark-muted'
              }`}
            >
              <span className="text-lg">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>

        {section === 'home' && (
          <div className="space-y-4 pt-4">
            <div className="card">
              <p className="text-3xl">👋</p>
              <p className="text-lg font-bold mt-2">
                Xush kelibsiz, {role === 'admin' ? 'Admin' : 'O\'qituvchi'}!
              </p>
              <p className="text-dark-muted text-sm mt-1">
                Sizga biriktirilgan <b>{classes.length}</b> ta sinf mavjud.
              </p>
            </div>

            <div>
              <h2 className="text-sm font-semibold text-dark-muted mb-3">SIZNING SINFLARINGIZ</h2>
              {classes.map((c) => (
                <button
                  key={c.id}
                  onClick={() => openClass(c)}
                  className="card w-full mb-2 flex items-center justify-between active:scale-[0.98] transition-all"
                >
                  <div>
                    <p className="font-bold text-lg">{c.name}</p>
                    <p className="text-sm text-dark-muted">{c.student_count} o'quvchi</p>
                  </div>
                  <span className="text-dark-muted">→</span>
                </button>
              ))}
              {classes.length === 0 && (
                <EmptyState message="Sinf biriktirilmagan" />
              )}
            </div>
          </div>
        )}

        {section === 'classes' && (
          <div className="space-y-4 pt-4">
            <h2 className="text-lg font-bold">📚 Sinflar</h2>
            {classes.map((c) => (
              <button
                key={c.id}
                onClick={() => openClass(c)}
                className="card w-full flex items-center justify-between mb-2 active:scale-[0.98] transition-all"
              >
                <div>
                  <p className="font-bold">📚 {c.name}</p>
                  <p className="text-sm text-dark-muted">{c.student_count} o'quvchi</p>
                </div>
                <span className="text-dark-muted">→</span>
              </button>
            ))}
          </div>
        )}

        {section === 'students' && selectedClass && (
          <div className="space-y-4 pt-4">
            <button
              onClick={() => setSection('home')}
              className="text-dark-muted text-sm mb-2"
            >
              ← Orqaga
            </button>
            <h2 className="text-lg font-bold">👨‍🎓 {selectedClass.name}</h2>

            {loading ? (
              <Skeleton lines={5} />
            ) : (
              <div className="space-y-3">
                {students.map((s) => {
                  const config = statusConfig[s.today_status || 'no_data'] || statusConfig.no_data;
                  return (
                    <div key={s.id} className="card space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                          👤
                        </div>
                        <div>
                          <p className="font-semibold">{s.first_name} {s.last_name}</p>
                          <p className={`text-sm ${config.color}`}>
                            {config.emoji} {s.today_status || 'no_data'}
                            {s.arrival_time ? ` • ${s.arrival_time}` : ''}
                          </p>
                        </div>
                      </div>
                      <div className="grid grid-cols-4 gap-1">
                        <button
                          onClick={() => doMark(s.id, 'present')}
                          className="py-2 rounded-lg bg-white/5 text-xs active:scale-95 transition-all"
                        >
                          🟢 Kelgan
                        </button>
                        <button
                          onClick={() => doMark(s.id, 'absent')}
                          className="py-2 rounded-lg bg-white/5 text-xs active:scale-95 transition-all"
                        >
                          🔴 Kelmagan
                        </button>
                        <button
                          onClick={() => doMark(s.id, 'late')}
                          className="py-2 rounded-lg bg-white/5 text-xs active:scale-95 transition-all"
                        >
                          🟠 Kechikkan
                        </button>
                        <button
                          onClick={() => doMark(s.id, 'excused')}
                          className="py-2 rounded-lg bg-white/5 text-xs active:scale-95 transition-all"
                        >
                          🔵 Sababli
                        </button>
                      </div>
                    </div>
                  );
                })}
                {students.length === 0 && <EmptyState message="O'quvchilar topilmadi" />}
              </div>
            )}
          </div>
        )}

        {section === 'notif' && (
          <div className="space-y-4 pt-4">
            <h2 className="text-lg font-bold">📢 Bildirishnoma</h2>
            <div>
              <label className="text-sm text-dark-muted">Sinf</label>
              <select
                className="input mt-1"
                value={selectedClass?.id || ''}
                onChange={(e) => {
                  const cls = classes.find((c) => c.id === Number(e.target.value));
                  if (cls) setSelectedClass(cls);
                }}
              >
                <option value="">Sinf tanlang</option>
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-dark-muted">Sarlavha</label>
              <input
                className="input mt-1"
                value={notifTitle}
                onChange={(e) => setNotifTitle(e.target.value)}
                placeholder="Xabar sarlavhasi"
              />
            </div>
            <div>
              <label className="text-sm text-dark-muted">Xabar matni</label>
              <textarea
                className="input mt-1 min-h-[100px]"
                value={notifMsg}
                onChange={(e) => setNotifMsg(e.target.value)}
                placeholder="Xabar matnini yozing..."
              />
            </div>
            {notifSent && (
              <div className="text-sm text-status-present bg-green-500/10 rounded-xl p-3">
                {notifSent}
              </div>
            )}
            <button
              onClick={doSendNotification}
              disabled={!selectedClass || !notifTitle || !notifMsg}
              className="btn-primary w-full disabled:opacity-50"
            >
              📤 Yuborish
            </button>
          </div>
        )}

        {section === 'stats' && (
          <div className="space-y-4 pt-4">
            <h2 className="text-lg font-bold">📊 Statistika</h2>
            <div className="card">
              <p className="font-semibold">Sinflar:</p>
              <p className="text-3xl font-bold">{classes.length}</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="card text-center">
                <p className="text-3xl">👨‍🎓</p>
                <p className="text-2xl font-bold">
                  {classes.reduce((acc, c) => acc + c.student_count, 0)}
                </p>
                <p className="text-sm text-dark-muted">Jami o'quvchilar</p>
              </div>
              <div className="card text-center">
                <p className="text-3xl">📚</p>
                <p className="text-2xl font-bold">{classes.length}</p>
                <p className="text-sm text-dark-muted">Sinflar soni</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
