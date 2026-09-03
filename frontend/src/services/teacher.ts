import { api } from './auth';
import type { TeacherClass, StudentStatus } from '../types';

export async function getTeacherClasses(): Promise<TeacherClass[]> {
  const res = await api.get('/teacher/classes');
  return res.data;
}

export async function getClassStudents(classId: number): Promise<StudentStatus[]> {
  const res = await api.get(`/teacher/classes/${classId}/students`);
  return res.data;
}

export async function markAttendance(studentId: number, status: string, reason?: string) {
  const res = await api.post('/teacher/attendance', {
    student_id: studentId,
    status,
    reason,
  });
  return res.data;
}

export async function sendNotification(classId: number, title: string, message: string) {
  const res = await api.post('/teacher/notification', null, {
    params: { class_id: classId, title, message },
  });
  return res.data;
}
