export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: string;
  user_id: number;
}

export interface Child {
  id: number;
  first_name: string;
  last_name: string;
  class_name?: string | null;
  class_id?: number | null;
  school_name?: string | null;
  school_id?: number | null;
  attendance_status?: string | null;
  arrival_time?: string | null;
  late_minutes: number;
}

export interface Student {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  class_id?: number | null;
  school_id: number;
  is_active: boolean;
}

export interface TodayAttendance {
  id?: number;
  status: string;
  date: string;
  arrival_time?: string | null;
  departure_time?: string | null;
  late_minutes: number;
  reason?: string | null;
}

export interface MonthlyDay {
  date: string;
  day_name: string;
  status: string;
  arrival_time?: string | null;
  late_minutes: number;
}

export interface Statistics {
  student_id: number;
  student_name: string;
  class_name?: string | null;
  month: number;
  year: number;
  total_school_days: number;
  present_days: number;
  absent_days: number;
  late_days: number;
  excused_days: number;
  attendance_percentage: number;
  level: string;
}

export interface ClassInfo {
  student_name: string;
  class_name: string;
  grade?: number | null;
  shift?: string | null;
  school_name?: string | null;
  school_region?: string | null;
  school_city?: string | null;
  school_address?: string | null;
  teacher_name?: string | null;
  teacher_phone?: string | null;
}

export interface TeacherClass {
  id: number;
  name: string;
  grade?: number | null;
  shift?: string | null;
  student_count: number;
}

export interface StudentStatus {
  id: number;
  first_name: string;
  last_name: string;
  today_status?: string | null;
  arrival_time?: string | null;
}
