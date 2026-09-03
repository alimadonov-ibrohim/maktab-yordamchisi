from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


class ContactAuthRequest(BaseModel):
    phone: str = Field(..., min_length=9, max_length=20)
    telegram_id: Optional[int] = None


class TelegramAuthRequest(BaseModel):
    init_data: str


class ParentProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    telegram_id: Optional[int] = None

    class Config:
        from_attributes = True


class ChildResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    class_name: Optional[str] = None
    class_id: Optional[int] = None
    school_name: Optional[str] = None
    school_id: Optional[int] = None
    attendance_status: Optional[str] = None
    arrival_time: Optional[str] = None
    late_minutes: int = 0

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    class_id: Optional[int] = None
    school_id: int
    is_active: bool

    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    date: date
    status: str
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    late_minutes: int = 0
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    student_id: int
    status: str = Field(..., pattern="^(present|absent|late|excused)$")
    reason: Optional[str] = None


class AttendanceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(present|absent|late|excused)$")
    departure_time: Optional[str] = None
    reason: Optional[str] = None


class StatisticsResponse(BaseModel):
    student_id: int
    student_name: str
    class_name: Optional[str] = None
    month: int
    year: int
    total_school_days: int
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    attendance_percentage: float
    level: str


class MonthlyDayStat(BaseModel):
    date: str
    day_name: str
    status: str
    arrival_time: Optional[str] = None
    late_minutes: int = 0


class ClassResponse(BaseModel):
    id: int
    name: str
    school_id: int
    grade: Optional[int] = None
    shift: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


class ClassDetailResponse(BaseModel):
    id: int
    name: str
    grade: Optional[int] = None
    shift: Optional[str] = None
    school_name: Optional[str] = None
    school_region: Optional[str] = None
    school_city: Optional[str] = None
    school_address: Optional[str] = None
    teacher_name: Optional[str] = None
    teacher_phone: Optional[str] = None

    class Config:
        from_attributes = True


class StudentInClass(BaseModel):
    id: int
    first_name: str
    last_name: str
    today_status: Optional[str] = None
    arrival_time: Optional[str] = None

    class Config:
        from_attributes = True


class SchoolCreate(BaseModel):
    name: str
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class SchoolResponse(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class ClassCreate(BaseModel):
    name: str
    school_id: int
    grade: Optional[int] = None
    shift: Optional[str] = None
    teacher_id: Optional[int] = None


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    class_id: Optional[int] = None
    school_id: int


class ParentCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    telegram_id: Optional[int] = None


class ParentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    telegram_id: Optional[int] = None

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    telegram_id: Optional[int] = None


class TeacherResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    telegram_id: Optional[int] = None

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeacherProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    telegram_id: Optional[int] = None
    classes: List[ClassResponse] = []

    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    total_schools: int = 0
    total_classes: int = 0
    total_students: int = 0
    total_teachers: int = 0
    total_parents: int = 0
    today_present: int = 0
    today_absent: int = 0
    today_late: int = 0
