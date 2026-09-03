import CrudManager from './CrudManager';
import {
  getSchools, createSchool, updateSchool, deleteSchool,
} from '../../services/admin';

const fields = [
  { key: 'name', label: 'Maktab nomi', required: true },
  { key: 'region', label: 'Viloyat' },
  { key: 'city', label: 'Shahar' },
  { key: 'address', label: 'Manzil' },
  { key: 'phone', label: 'Telefon', type: 'tel' as const },
];

export default function SchoolsPage() {
  return (
    <CrudManager
      title="🏫 Maktablar"
      columns={[
        { key: 'name', label: 'Nomi' },
        { key: 'city', label: 'Shahar' },
        { key: 'region', label: 'Viloyat' },
        { key: 'phone', label: 'Tel' },
      ]}
      fields={fields}
      load={getSchools}
      create={createSchool}
      update={updateSchool}
      remove={deleteSchool}
      searchKeys={['name', 'city', 'region']}
    />
  );
}
