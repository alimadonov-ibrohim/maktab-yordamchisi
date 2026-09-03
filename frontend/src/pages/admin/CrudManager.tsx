import { useEffect, useState } from 'react';
import Skeleton from '../ui/Skeleton';
import ErrorState from '../ui/ErrorState';
import EmptyState from '../ui/EmptyState';

interface Column {
  key: string;
  label: string;
  render?: (row: any) => React.ReactNode;
}

interface Field {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'select' | 'tel';
  options?: { value: any; label: string }[];
  required?: boolean;
}

interface CrudManagerProps {
  title: string;
  columns: Column[];
  fields: Field[];
  load: () => Promise<any[]>;
  create?: (data: any) => Promise<any>;
  update?: (id: number, data: any) => Promise<any>;
  remove?: (id: number) => Promise<any>;
  searchKeys?: string[];
}

export default function CrudManager({
  title,
  columns,
  fields,
  load,
  create,
  update,
  remove,
  searchKeys = [],
}: CrudManagerProps) {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [form, setForm] = useState<Record<string, any>>({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await load();
      setRows(data);
    } catch (e) {
      setError('Ma\'lumotni yuklashda xatolik yuz berdi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const startCreate = () => {
    setEditing(null);
    const init: Record<string, any> = {};
    fields.forEach((f) => {
      if (f.options && f.options.length) init[f.key] = f.options[0].value;
      else if (f.type === 'number') init[f.key] = '';
      else init[f.key] = '';
    });
    setForm(init);
    setShowForm(true);
  };

  const startEdit = (row: any) => {
    setEditing(row);
    setForm({ ...row });
    setShowForm(true);
  };

  const submit = async () => {
    setSaving(true);
    setMsg('');
    try {
      if (editing && update) {
        await update(editing.id, form);
        setMsg('✅ Yangilandi');
      } else if (create) {
        await create(form);
        setMsg('✅ Qo\'shildi');
      }
      setShowForm(false);
      setTimeout(() => setMsg(''), 3000);
      await loadData();
    } catch (e: any) {
      setMsg('❌ Xatolik: ' + (e?.response?.data?.detail || 'Noma\'lum'));
    } finally {
      setSaving(false);
    }
  };

  const doDelete = async (id: number) => {
    if (!remove) return;
    if (!confirm('Haqiqatan o\'chirasizmi?')) return;
    try {
      await remove(id);
      await loadData();
    } catch (e: any) {
      alert('O\'chirishda xatolik: ' + (e?.response?.data?.detail || ''));
    }
  };

  const filtered = search
    ? rows.filter((r) =>
        searchKeys.some((k) =>
          String(r[k] || '').toLowerCase().includes(search.toLowerCase())
        )
      )
    : rows;

  if (loading) return <div><Skeleton lines={5} /></div>;
  if (error) return <ErrorState message={error} onRetry={loadData} />;

  return (
    <div className="space-y-4 animate-fade-up">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">{title}</h2>
        {create && (
          <button onClick={startCreate} className="btn-primary text-sm py-2 px-3">
            ➕ Qo'shish
          </button>
        )}
      </div>

      {msg && (
        <div className="text-sm bg-white/5 rounded-xl p-3">{msg}</div>
      )}

      {searchKeys.length > 0 && (
        <input
          className="input"
          placeholder="🔍 Qidirish..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      )}

      {showForm && (
        <div className="card border border-primary-600/30 space-y-3">
          <p className="font-semibold">{editing ? '✏️ Tahrirlash' : `➕ ${title} qo'shish`}</p>
          <div className="grid grid-cols-2 gap-2">
            {fields.map((f) => (
              <div key={f.key} className={f.type === 'select' ? 'col-span-2' : ''}>
                <label className="text-xs text-dark-muted block mb-1">{f.label}</label>
                {f.type === 'select' ? (
                  <select
                    className="input"
                    value={form[f.key] ?? ''}
                    onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                  >
                    {(f.options || []).map((o) => (
                      <option key={String(o.value)} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    className="input"
                    type={f.type === 'number' ? 'number' : 'text'}
                    value={form[f.key] ?? ''}
                    required={f.required}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        [f.key]: f.type === 'number' ? Number(e.target.value) : e.target.value,
                      })
                    }
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <button onClick={submit} disabled={saving} className="btn-primary flex-1">
              {saving ? 'Saqlanmoqda...' : '💾 Saqlash'}
            </button>
            <button onClick={() => setShowForm(false)} className="btn-ghost">
              Bekor qilish
            </button>
          </div>
        </div>
      )}

      {filtered.length === 0 ? (
        <EmptyState message="Ma'lumot topilmadi" />
      ) : (
        <div className="space-y-2">
          {filtered.map((row) => (
            <div key={row.id} className="card flex items-center justify-between">
              <div className="flex-1 min-w-0">
                {columns.map((c) => (
                  <div key={c.key} className="text-sm truncate">
                    {c.render ? c.render(row) : (
                      <>
                        <span className="text-dark-muted">{c.label}: </span>
                        <span className="font-medium">{row[c.key]}</span>
                      </>
                    )}
                  </div>
                ))}
              </div>
              <div className="flex gap-1 ml-2">
                {update && (
                  <button
                    onClick={() => startEdit(row)}
                    className="px-2 py-1 rounded-lg bg-white/5 text-sm active:scale-95"
                  >
                    ✏️
                  </button>
                )}
                {remove && (
                  <button
                    onClick={() => doDelete(row.id)}
                    className="px-2 py-1 rounded-lg bg-red-500/10 text-sm active:scale-95"
                  >
                    🗑
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
