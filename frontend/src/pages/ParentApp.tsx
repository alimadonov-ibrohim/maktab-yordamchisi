import { useEffect, useMemo, useState } from 'react';
import BottomNav from '../components/BottomNav';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import HomePage from '../components/HomePage';
import TodayPage from '../components/TodayPage';
import StatsPage from '../components/StatsPage';
import ClassPage from '../components/ClassPage';
import { getChildren } from '../services/parent';
import type { Child } from '../types';

interface ParentAppProps {
  onLogout: () => void;
}

export default function ParentApp({ onLogout }: ParentAppProps) {
  const [tab, setTab] = useState('home');
  const [children, setChildren] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [greeting, setGreeting] = useState('');
  const [parentName, setParentName] = useState('');

  const loadChildren = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getChildren();
      setChildren(data);
      if (data.length > 0) {
        setSelectedChild(data[0]);
      }
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChildren();
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Xayrli tong');
    else if (hour < 18) setGreeting('Xayrli kun');
    else setGreeting('Xayrli kech');

    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (tgUser?.first_name) {
      setParentName(tgUser.first_name);
    } else {
      setParentName('Ota-ona');
    }

    // Polling for realtime updates
    const interval = setInterval(loadChildren, 30000);
    return () => clearInterval(interval);
  }, []);

  const presentCount = useMemo(
    () => children.filter((c) => c.attendance_status === 'present' || c.attendance_status === 'late').length,
    [children]
  );

  if (loading && children.length === 0) {
    return (
      <div className="min-h-screen bg-dark-bg pb-20 p-4">
        <Skeleton lines={4} />
        <BottomNav active={tab} onChange={setTab} />
      </div>
    );
  }

  if (error && children.length === 0) {
    return (
      <div className="min-h-screen bg-dark-bg p-4">
        <ErrorState message={error} onRetry={loadChildren} />
      </div>
    );
  }

  if (children.length === 0) {
    return (
      <div className="min-h-screen bg-dark-bg p-4">
        <EmptyState message="Farzandlaringiz topilmadi. Admin bilan bog'laning." />
      </div>
    );
  }

  const child = selectedChild || children[0];

  return (
    <div className="min-h-screen bg-dark-bg pb-20">
      <div className="max-w-md mx-auto px-4 pt-6">
        {tab === 'home' && (
          <HomePage
            greeting={greeting}
            parentName={parentName}
            totalChildren={children.length}
            presentCount={presentCount}
            child={child}
            children={children}
            onSelectChild={setSelectedChild}
            onLogout={onLogout}
          />
        )}
        {tab === 'today' && (
          <TodayPage child={child} />
        )}
        {tab === 'stats' && (
          <StatsPage child={child} />
        )}
        {tab === 'class' && (
          <ClassPage child={child} />
        )}
      </div>
      <BottomNav active={tab} onChange={setTab} />
    </div>
  );
}
