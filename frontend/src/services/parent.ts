import { api } from './auth';
import type {
  Child,
  TodayAttendance,
  MonthlyDay,
  Statistics,
  ClassInfo,
} from '../types';

export async function getChildren(): Promise<Child[]> {
  const res = await api.get('/parent/children');
  return res.data;
}

export async function getTodayAttendance(studentId: number): Promise<TodayAttendance> {
  const res = await api.get(`/parent/attendance/today/${studentId}`);
  return res.data;
}

export async function getMonthlyAttendance(
  studentId: number,
  month?: number,
  year?: number
): Promise<MonthlyDay[]> {
  const params: Record<string, number> = {};
  if (month) params.month = month;
  if (year) params.year = year;
  const res = await api.get(`/parent/attendance/monthly/${studentId}`, { params });
  return res.data;
}

export async function getStatistics(
  studentId: number,
  month?: number,
  year?: number
): Promise<Statistics> {
  const params: Record<string, number> = {};
  if (month) params.month = month;
  if (year) params.year = year;
  const res = await api.get(`/parent/statistics/${studentId}`, { params });
  return res.data;
}

export async function getClassInfo(studentId: number): Promise<ClassInfo> {
  const res = await api.get(`/parent/class/${studentId}`);
  return res.data;
}
