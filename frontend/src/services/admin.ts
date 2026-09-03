import { api } from './auth';

export interface AdminStats {
  total_schools: number;
  total_classes: number;
  total_students: number;
  total_teachers: number;
  total_parents: number;
  today_present: number;
  today_absent: number;
  today_late: number;
}

export async function getAdminStats(): Promise<AdminStats> {
  const res = await api.get('/admin/stats');
  return res.data;
}

export async function getSchools() {
  const res = await api.get('/admin/schools');
  return res.data;
}

export async function createSchool(data: any) {
  const res = await api.post('/admin/schools', data);
  return res.data;
}

export async function updateSchool(id: number, data: any) {
  const res = await api.put(`/admin/schools/${id}`, data);
  return res.data;
}

export async function deleteSchool(id: number) {
  const res = await api.delete(`/admin/schools/${id}`);
  return res.data;
}

export async function getClasses(schoolId?: number) {
  const res = await api.get('/admin/classes', { params: schoolId ? { school_id: schoolId } : {} });
  return res.data;
}

export async function createClass(data: any) {
  const res = await api.post('/admin/classes', data);
  return res.data;
}

export async function updateClass(id: number, data: any) {
  const res = await api.put(`/admin/classes/${id}`, data);
  return res.data;
}

export async function deleteClass(id: number) {
  const res = await api.delete(`/admin/classes/${id}`);
  return res.data;
}

export async function getStudents(classId?: number, schoolId?: number) {
  const params: Record<string, number> = {};
  if (classId) params.class_id = classId;
  if (schoolId) params.school_id = schoolId;
  const res = await api.get('/admin/students', { params });
  return res.data;
}

export async function createStudent(data: any) {
  const res = await api.post('/admin/students', data);
  return res.data;
}

export async function updateStudent(id: number, data: any) {
  const res = await api.put(`/admin/students/${id}`, data);
  return res.data;
}

export async function deleteStudent(id: number) {
  const res = await api.delete(`/admin/students/${id}`);
  return res.data;
}

export async function getParents() {
  const res = await api.get('/admin/parents');
  return res.data;
}

export async function createParent(data: any) {
  const res = await api.post('/admin/parents', data);
  return res.data;
}

export async function linkChild(parentId: number, studentId: number) {
  const res = await api.post(`/admin/parents/${parentId}/link-child/${studentId}`);
  return res.data;
}

export async function deleteParent(id: number) {
  const res = await api.delete(`/admin/parents/${id}`);
  return res.data;
}

export async function getTeachers() {
  const res = await api.get('/admin/teachers');
  return res.data;
}

export async function createTeacher(data: any) {
  const res = await api.post('/admin/teachers', data);
  return res.data;
}

export async function updateTeacher(id: number, data: any) {
  const res = await api.put(`/admin/teachers/${id}`, data);
  return res.data;
}

export async function deleteTeacher(id: number) {
  const res = await api.delete(`/admin/teachers/${id}`);
  return res.data;
}

export async function getAttendance(classId?: number, attDate?: string) {
  const params: Record<string, any> = {};
  if (classId) params.class_id = classId;
  if (attDate) params.att_date = attDate;
  const res = await api.get('/admin/attendance', { params });
  return res.data;
}

export async function getAdmins() {
  const res = await api.get('/admin/system/admins');
  return res.data;
}

export async function createAdmin(data: any) {
  const res = await api.post('/admin/system/admins', null, { params: data });
  return res.data;
}

export async function deleteAdmin(id: number) {
  const res = await api.delete(`/admin/system/admins/${id}`);
  return res.data;
}

export async function getAuditLogs(limit = 50) {
  const res = await api.get('/admin/system/audit', { params: { limit } });
  return res.data;
}

export async function getSystemSettings() {
  const res = await api.get('/admin/system/settings');
  return res.data;
}

export async function updateSetting(key: string, value: string) {
  const res = await api.put('/admin/system/settings', null, { params: { key, value } });
  return res.data;
}

export async function getSchoolDays(schoolId?: number) {
  const res = await api.get('/admin/system/school-days', { params: schoolId ? { school_id: schoolId } : {} });
  return res.data;
}

export async function createSchoolDay(data: any) {
  const res = await api.post('/admin/system/school-days', null, { params: data });
  return res.data;
}

export async function deleteSchoolDay(id: number) {
  const res = await api.delete(`/admin/system/school-days/${id}`);
  return res.data;
}

export async function getNotifications() {
  const res = await api.get('/admin/system/notifications');
  return res.data;
}

export async function broadcastNotification(title: string, message: string, role: string) {
  const res = await api.post('/admin/system/notifications/broadcast', null, { params: { title, message, role } });
  return res.data;
}
