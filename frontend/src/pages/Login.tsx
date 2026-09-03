import { useState } from 'react';
import { authenticateWithContact } from '../services/auth';

interface LoginProps {
  onSuccess: () => void;
  error?: string;
}

export default function Login({ onSuccess, error }: LoginProps) {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(error || null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError(null);

    try {
      const tgId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id;
      const res = await authenticateWithContact(phone, tgId);
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('role', res.role);
      localStorage.setItem('user_id', String(res.user_id));
      onSuccess();
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setLoginError('❌ Telefon raqamingiz tizimda topilmadi. Maktab administratoriga murojaat qiling.');
      } else {
        setLoginError('Ma\'lumotni yuklashda xatolik yuz berdi.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-2">
          <div className="w-20 h-20 rounded-3xl bg-primary-600 flex items-center justify-center text-4xl mx-auto">
            🎓
          </div>
          <h1 className="text-2xl font-bold">Maktab Yordamchisi</h1>
          <p className="text-dark-muted">Telefon raqamingiz bilan kiring</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 animate-fade-up">
          <div>
            <label className="block text-sm text-dark-muted mb-2">Telefon raqam</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+998901234567"
              className="input"
              required
            />
          </div>

          {loginError && (
            <div className="text-sm text-status-absent bg-red-500/10 rounded-xl p-3">
              {loginError}
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Tekshirilmoqda...' : '🔐 Kirish'}
          </button>
        </form>

        <p className="text-xs text-dark-muted text-center">
          Raqamingiz tizimda ro'yxatdan o'tgan bo'lishi kerak.
        </p>
      </div>
    </div>
  );
}
