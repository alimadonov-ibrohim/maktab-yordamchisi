import { useState } from 'react';

interface BottomNavProps {
  active: string;
  onChange: (tab: string) => void;
}

const tabs = [
  { key: 'home', label: 'Asosiy', icon: '🏠' },
  { key: 'today', label: 'Bugun', icon: '📅' },
  { key: 'stats', label: 'Statistika', icon: '📊' },
  { key: 'class', label: 'Sinf', icon: '🏫' },
];

export default function BottomNav({ active, onChange }: BottomNavProps) {
  const [current, setCurrent] = useState(active);

  const handleChange = (key: string) => {
    setCurrent(key);
    onChange(key);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-dark-card border-t border-dark-border z-50">
      <div className="body">
        {/* padding for safe area handled by container below */}
      </div>
      <div className="flex justify-around items-center h-16 max-w-md mx-auto">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => handleChange(t.key)}
            className={`nav-item ${current === t.key ? 'active' : 'text-dark-muted'}`}
          >
            <span className="text-xl">{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
