from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, Time
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False, default="parent")
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    parent = relationship("Parent", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    classes = relationship("Class", back_populates="school")


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)

    user = relationship("User", back_populates="parent")
    student_links = relationship(
        "ParentStudent", back_populates="parent"
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)

    user = relationship("User", back_populates="teacher")
    classes = relationship("Class", back_populates="teacher")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    grade = Column(Integer, nullable=True)
    shift = Column(String(20), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    school = relationship("School", back_populates="classes")
    teacher = relationship("Teacher", back_populates="classes")
    students = relationship("Student", back_populates="class_obj")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    class_obj = relationship("Class", back_populates="students")
    school = relationship("School")
    parent_links = relationship(
        "ParentStudent", back_populates="student"
    )
    attendances = relationship(
        "Attendance", back_populates="student", order_by="Attendance.date.desc()"
    )


class ParentStudent(Base):
    __tablename__ = "parent_students"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    parent = relationship("Parent", back_populates="student_links")
    student = relationship("Student", back_populates="parent_links")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="absent")
    arrival_time = Column(Time, nullable=True)
    departure_time = Column(Time, nullable=True)
    late_minutes = Column(Integer, default=0)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    student = relationship("Student", back_populates="attendances")


class SchoolDay(Base):
    __tablename__ = "school_days"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    start_time = Column(Time, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    school = relationship("School")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
