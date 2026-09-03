import { useEffect, useState } from 'react';
import { getClassInfo } from '../services/parent';
import Skeleton from './ui/Skeleton';
import ErrorState from './ui/ErrorState';
import type { Child, ClassInfo } from '../types';

interface ClassPageProps {
  child: Child;
}

export default function ClassPage({ child }: ClassPageProps) {
  const [info, setInfo] = useState<ClassInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getClassInfo(child.id);
      setInfo(data);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [child.id]);

  if (loading) {
    return (
      <div className="animate-fade-up">
        <h2 className="text-2xl font-bold mb-4">🏫 Sinf</h2>
        <Skeleton lines={4} />
      </div>
    );
  }

  if (error) {
    return <ErrorState message={error} onRetry={load} />;
  }

  if (!info) {
    return null;
  }

  return (
    <div className="space-y-5 animate-fade-up">
      <div>
        <h2 className="text-2xl font-bold">🏫 Sinf</h2>
        <p className="text-lg font-semibold mt-2">{info.student_name}</p>
      </div>

      <section>
        <h3 className="text-sm font-semibold text-dark-muted mb-3">MAKTAB</h3>
        <div className="card space-y-2">
          <p className="text-lg font-bold">{info.school_name || '20-maktab'}</p>
          {info.school_region && (
            <p className="text-sm">
              <span className="text-dark-muted">Viloyat:</span>{' '}
              {info.school_region}
            </p>
          )}
          {info.school_city && (
            <p className="text-sm">
              <span className="text-dark-muted">Shahar:</span>{' '}
              {info.school_city}
            </p>
          )}
          {info.school_address && (
            <p className="text-sm">
              <span className="text-dark-muted">Manzil:</span>{' '}
              {info.school_address}
            </p>
          )}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-dark-muted mb-3">SINF</h3>
        <div className="card flex items-center justify-between">
          <p className="text-2xl font-bold">{info.class_name}</p>
          <span className="text-sm text-dark-muted">{info.shift || ''}</span>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-dark-muted mb-3">SINF RAHBARI</h3>
        <div className="card">
          {info.teacher_name ? (
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-2xl">
                👨‍🏫
              </div>
              <div>
                <p className="font-semibold">{info.teacher_name}</p>
                {info.teacher_phone && (
                  <p className="text-sm text-dark-muted">📞 {info.teacher_phone}</p>
                )}
              </div>
            </div>
          ) : (
            <p className="text-dark-muted">Sinf rahbari biriktirilmagan</p>
          )}
        </div>
      </section>
    </div>
  );
}
