import { useState } from 'react';
import DashboardPage from './admin/DashboardPage';
import SchoolsPage from './admin/SchoolsPage';
import CrudManager from './admin/CrudManager';
import {
  getClasses, createClass, updateClass, deleteClass,
  getStudents, createStudent, updateStudent, deleteStudent,
  getTeachers, createTeacher, updateTeacher, deleteTeacher,
  getParents, createParent, deleteParent,
} from '../services/admin';

interface AdminAppProps {
  role: string;
  onLogout: () => void;
}

export default function AdminApp({ role, onLogout }: AdminAppProps) {
  const [section, setSection] = useState('dashboard');

  const navItems = [
    { key: 'dashboard', label: 'Bosh', icon: '📊' },
    { key: 'schools', label: 'Maktab', icon: '🏫' },
    { key: 'classes', label: 'Sinflar', icon: '📚' },
    { key: 'students', label: "O'quvchi", icon: '👨‍🎓' },
    { key: 'more', label: 'Boshqa', icon: '☰' },
  ];

  const classFields = [
    { key: 'name', label: 'Sinf nomi', required: true },
    { key: 'school_id', label: 'Maktab ID', type: 'number' as const },
    { key: 'grade', label: 'Sinf (sinf raqami)', type: 'number' as const },
    { key: 'shift', label: 'Smena', type: 'number' as const },
    { key: 'teacher_id', label: "O'qituvchi ID", type: 'number' as const },
  ];

  const studentFields = [
    { key: 'first_name', label: 'Ism', required: true },
    { key: 'last_name', label: 'Familiya', required: true },
    { key: 'class_id', label: 'Sinf ID', type: 'number' as const },
    { key: 'school_id', label: 'Maktab ID', type: 'number' as const },
  ];

  const teacherFields = [
    { key: 'first_name', label: 'Ism', required: true },
    { key: 'last_name', label: 'Familiya', required: true },
    { key: 'phone', label: 'Telefon', type: 'tel' as const },
    { key: 'telegram_id', label: 'Telegram ID', type: 'number' as const },
  ];

  const parentFields = [
    { key: 'first_name', label: 'Ism', required: true },
    { key: 'last_name', label: 'Familiya', required: true },
    { key: 'phone', label: 'Telefon', type: 'tel' as const },
    { key: 'telegram_id', label: 'Telegram ID', type: 'number' as const },
  ];

  const renderSection = () => {
    switch (section) {
      case 'dashboard':
        return <DashboardPage role={role} />;
      case 'schools':
        return <SchoolsPage />;
      case 'classes':
        return (
          <CrudManager
            title="📚 Sinflar"
            columns={[
              { key: 'name', label: 'Nomi' },
              { key: 'school_name', label: 'Maktab' },
              { key: 'grade', label: 'Sinf' },
              { key: 'student_count', label: "O'quvchilar" },
            ]}
            fields={classFields}
            load={getClasses}
            create={createClass}
            update={updateClass}
            remove={deleteClass}
            searchKeys={['name', 'school_name']}
          />
        );
      case 'students':
        return (
          <CrudManager
            title="👨‍🎓 O'quvchilar"
            columns={[
              { key: 'first_name', label: 'Ism' },
              { key: 'last_name', label: 'Familiya' },
              { key: 'class_name', label: 'Sinf' },
            ]}
            fields={studentFields}
            load={getStudents}
            create={createStudent}
            update={updateStudent}
            remove={deleteStudent}
            searchKeys={['first_name', 'last_name', 'class_name']}
          />
        );
      case 'teachers':
        return (
          <CrudManager
            title="👨‍🏫 O'qituvchilar"
            columns={[
              { key: 'first_name', label: 'Ism' },
              { key: 'last_name', label: 'Familiya' },
              { key: 'phone', label: 'Tel' },
            ]}
            fields={teacherFields}
            load={getTeachers}
            create={createTeacher}
            update={updateTeacher}
            remove={deleteTeacher}
            searchKeys={['first_name', 'last_name', 'phone']}
          />
        );
      case 'parents':
        return (
          <CrudManager
            title="👨‍👩‍👧 Ota-onalar"
            columns={[
              { key: 'first_name', label: 'Ism' },
              { key: 'last_name', label: 'Familiya' },
              { key: 'phone', label: 'Tel' },
            ]}
            fields={parentFields}
            load={getParents}
            create={createParent}
            remove={deleteParent}
            searchKeys={['first_name', 'last_name', 'phone']}
          />
        );
      case 'more':
        return (
          <div className="space-y-2 pt-4">
            <button
              onClick={() => setSection('teachers')}
              className="card w-full flex items-center justify-between active:scale-[0.98] transition-all"
            >
              <span className="font-semibold">👨‍🏫 O'qituvchilar</span>
              <span className="text-dark-muted">→</span>
            </button>
            <button
              onClick={() => setSection('parents')}
              className="card w-full flex items-center justify-between active:scale-[0.98] transition-all"
            >
              <span className="font-semibold">👨‍👩‍👧 Ota-onalar</span>
              <span className="text-dark-muted">→</span>
            </button>
          </div>
        );
      default:
        return <DashboardPage role={role} />;
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg p-4 pb-20">
      <div className="max-w-md mx-auto space-y-5 animate-fade-up">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold">👨‍💼 Admin</h1>
            <p className="text-dark-muted text-sm">Maktab Yordamchisi</p>
          </div>
          <button
            onClick={onLogout}
            className="bg-dark-card border border-dark-border rounded-xl px-3 py-2 text-dark-muted active:scale-95 transition-all"
          >
            ⏻
          </button>
        </header>

        {renderSection()}

        <div className="grid grid-cols-5 gap-2 bg-dark-card border border-dark-border rounded-2xl p-2 fixed bottom-4 left-4 right-4 z-50 max-w-md mx-auto">
          {navItems.map((t) => (
            <button
              key={t.key}
              onClick={() => setSection(t.key)}
              className={`flex flex-col items-center py-2 rounded-xl text-xs transition-all ${
                section === t.key ? 'bg-primary-600 text-white' : 'text-dark-muted'
              }`}
            >
              <span className="text-lg">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
