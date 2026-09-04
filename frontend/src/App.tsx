import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { authenticateWithTelegram } from './services/auth';
import ParentApp from './pages/ParentApp';
import TeacherApp from './pages/TeacherApp';
import AdminApp from './pages/AdminApp';
import LoadingScreen from './components/ui/LoadingScreen';
import { hasAdminAccess } from './utils/roles';

export default function App() {
  const [authed, setAuthed] = useState<boolean>(() => {
    return !!localStorage.getItem('access_token');
  });
  const [role, setRole] = useState<string | null>(
    () => localStorage.getItem('role')
  );
  const [loading, setLoading] = useState<boolean>(!localStorage.getItem('access_token'));
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const tryAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        setLoading(false);
        return;
      }

      try {
        if (window.Telegram?.WebApp?.initData) {
          const res = await authenticateWithTelegram();
          localStorage.setItem('access_token', res.access_token);
          localStorage.setItem('role', res.role);
          localStorage.setItem('user_id', String(res.user_id));
          setRole(res.role);
          setAuthed(true);
        } else {
          setError('Telegram WebApp dan oching.');
        }
      } catch (e: any) {
        if (e?.response?.status === 404) {
          setError('Hisobingiz topilmadi. Admin bilan bog\'laning.');
        } else {
          setError('Xatolik yuz berdi. Qayta urinib ko\'ring.');
        }
      }
      setLoading(false);
    };

    tryAuth();
  }, []);

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    setAuthed(false);
    setRole(null);
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (!authed) {
    return (
      <div className="min-h-screen bg-dark-bg flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-sm text-center space-y-4">
          <div className="w-20 h-20 rounded-3xl bg-primary-600 flex items-center justify-center text-4xl mx-auto">
            🎓
          </div>
          <h1 className="text-2xl font-bold">Maktab Yordamchisi</h1>
          <p className="text-dark-muted">{error || 'Yuklanmoqda...'}</p>
        </div>
      </div>
    );
  }

  const isAdmin = hasAdminAccess(role || '');

  return (
    <BrowserRouter>
      <Routes>
        {isAdmin ? (
          <Route path="/*" element={<AdminApp role={role || 'parent'} onLogout={logout} />} />
        ) : role === 'teacher' ? (
          <Route path="/*" element={<TeacherApp role="teacher" onLogout={logout} />} />
        ) : (
          <Route path="/*" element={<ParentApp onLogout={logout} />} />
        )}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
