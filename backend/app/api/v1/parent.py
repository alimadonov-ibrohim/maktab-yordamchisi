from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models.models import (
    User, Parent, Student, Class, School,
    Attendance, ParentStudent, Teacher,
)
from app.schemas.schemas import (
    ParentProfile, ChildResponse, ClassDetailResponse,
    StudentInClass, AttendanceResponse,
)
from app.api.deps import get_current_user, require_parent

router = APIRouter(prefix="/parent", tags=["Parent"])


@router.get("/profile", response_model=ParentProfile)
async def get_profile(
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    return parent


@router.get("/children")
async def get_children(
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    ps_result = await db.execute(
        select(ParentStudent.student_id).where(
            ParentStudent.parent_id == parent.id
        )
    )
    student_ids = [row[0] for row in ps_result.all()]

    if not student_ids:
        return []

    today = date.today()
    children = []
    for sid in student_ids:
        student_result = await db.execute(
            select(Student).where(Student.id == sid)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            continue

        class_name = None
        school_name = None
        if student.class_id:
            cls_result = await db.execute(
                select(Class).where(Class.id == student.class_id)
            )
            cls = cls_result.scalar_one_or_none()
            if cls:
                class_name = cls.name
                sch_result = await db.execute(
                    select(School).where(School.id == cls.school_id)
                )
                sch = sch_result.scalar_one_or_none()
                if sch:
                    school_name = sch.name
        else:
            sch_result = await db.execute(
                select(School).where(School.id == student.school_id)
            )
            sch = sch_result.scalar_one_or_none()
            if sch:
                school_name = sch.name

        att_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.student_id == sid,
                    Attendance.date == today,
                )
            )
        )
        att = att_result.scalar_one_or_none()
        status_val = att.status if att else "no_data"
        arrival = (
            att.arrival_time.strftime("%H:%M") if att and att.arrival_time
            else None
        )

        children.append({
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "class_name": class_name,
            "class_id": student.class_id,
            "school_name": school_name,
            "school_id": student.school_id,
            "attendance_status": status_val,
            "arrival_time": arrival,
            "late_minutes": att.late_minutes if att else 0,
        })

    return children


@router.get("/children/{student_id}")
async def get_child_detail(
    student_id: int,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    ps_result = await db.execute(
        select(ParentStudent).where(
            and_(
                ParentStudent.parent_id == parent.id,
                ParentStudent.student_id == student_id,
            )
        )
    )
    ps = ps_result.scalar_one_or_none()
    if not ps:
        raise HTTPException(
            status_code=403, detail="Not your child"
        )

    student_result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "class_id": student.class_id,
        "school_id": student.school_id,
    }


@router.get("/attendance/today/{student_id}")
async def get_today_attendance(
    student_id: int,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    parent_result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    ps_result = await db.execute(
        select(ParentStudent).where(
            and_(
                ParentStudent.parent_id == parent.id,
                ParentStudent.student_id == student_id,
            )
        )
    )
    if not ps_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not your child")

    today = date.today()
    att_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.student_id == student_id,
                Attendance.date == today,
            )
        )
    )
    att = att_result.scalar_one_or_none()
    if not att:
        return {
            "status": "no_data",
            "date": today.isoformat(),
            "message": "Davomat belgilanmagan",
        }

    return {
        "id": att.id,
        "status": att.status,
        "date": att.date.isoformat(),
        "arrival_time": (
            att.arrival_time.strftime("%H:%M") if att.arrival_time else None
        ),
        "departure_time": (
            att.departure_time.strftime("%H:%M")
            if att.departure_time
            else None
        ),
        "late_minutes": att.late_minutes,
        "reason": att.reason,
    }


@router.get("/attendance/monthly/{student_id}")
async def get_monthly_attendance(
    student_id: int,
    month: int = None,
    year: int = None,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    parent_result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    ps_result = await db.execute(
        select(ParentStudent).where(
            and_(
                ParentStudent.parent_id == parent.id,
                ParentStudent.student_id == student_id,
            )
        )
    )
    if not ps_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not your child")

    today = date.today()
    if month is None:
        month = today.month
    if year is None:
        year = today.year

    att_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.student_id == student_id,
            )
        ).order_by(Attendance.date.desc())
    )
    all_att = att_result.scalars().all()

    monthly = [
        a for a in all_att
        if a.date.month == month and a.date.year == year
    ]

    days = []
    for att in monthly:
        days.append({
            "date": att.date.isoformat(),
            "day_name": att.date.strftime("%a"),
            "status": att.status,
            "arrival_time": (
                att.arrival_time.strftime("%H:%M")
                if att.arrival_time
                else None
            ),
            "late_minutes": att.late_minutes,
        })

    return days


@router.get("/statistics/{student_id}")
async def get_statistics(
    student_id: int,
    month: int = None,
    year: int = None,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    parent_result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    ps_result = await db.execute(
        select(ParentStudent).where(
            and_(
                ParentStudent.parent_id == parent.id,
                ParentStudent.student_id == student_id,
            )
        )
    )
    if not ps_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not your child")

    student_result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    today = date.today()
    if month is None:
        month = today.month
    if year is None:
        year = today.year

    class_name = None
    if student.class_id:
        cls_result = await db.execute(
            select(Class).where(Class.id == student.class_id)
        )
        cls = cls_result.scalar_one_or_none()
        if cls:
            class_name = cls.name

    att_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.student_id == student_id,
            )
        )
    )
    all_att = att_result.scalars().all()

    monthly = [
        a for a in all_att
        if a.date.month == month and a.date.year == year
    ]

    import calendar
    school_days = calendar.monthrange(year, month)[1]
    if month == today.month and year == today.year:
        school_days = today.day

    present = sum(1 for a in monthly if a.status == "present")
    absent = sum(1 for a in monthly if a.status == "absent")
    late = sum(1 for a in monthly if a.status == "late")
    excused = sum(1 for a in monthly if a.status == "excused")

    pct = (present / school_days * 100) if school_days > 0 else 0

    if pct < 70:
        level = "Past davomat"
    elif pct < 90:
        level = "Yaxshi"
    else:
        level = "A'lo"

    return {
        "student_id": student.id,
        "student_name": f"{student.first_name} {student.last_name}",
        "class_name": class_name,
        "month": month,
        "year": year,
        "total_school_days": school_days,
        "present_days": present,
        "absent_days": absent,
        "late_days": late,
        "excused_days": excused,
        "attendance_percentage": round(pct, 1),
        "level": level,
    }


@router.get("/class/{student_id}")
async def get_class_info(
    student_id: int,
    current_user: User = Depends(require_parent),
    db: AsyncSession = Depends(get_db),
):
    parent_result = await db.execute(
        select(Parent).where(Parent.user_id == current_user.id)
    )
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    ps_result = await db.execute(
        select(ParentStudent).where(
            and_(
                ParentStudent.parent_id == parent.id,
                ParentStudent.student_id == student_id,
            )
        )
    )
    if not ps_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not your child")

    student_result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not student.class_id:
        raise HTTPException(status_code=404, detail="Class not assigned")

    cls_result = await db.execute(
        select(Class).where(Class.id == student.class_id)
    )
    cls = cls_result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    sch_result = await db.execute(
        select(School).where(School.id == cls.school_id)
    )
    school = sch_result.scalar_one_or_none()

    teacher_name = None
    teacher_phone = None
    if cls.teacher_id:
        t_result = await db.execute(
            select(Teacher).where(Teacher.id == cls.teacher_id)
        )
        teacher = t_result.scalar_one_or_none()
        if teacher:
            teacher_name = f"{teacher.first_name} {teacher.last_name}"
            teacher_phone = teacher.phone

    return {
        "student_name": f"{student.first_name} {student.last_name}",
        "class_name": cls.name,
        "grade": cls.grade,
        "shift": cls.shift,
        "school_name": school.name if school else None,
        "school_region": school.region if school else None,
        "school_city": school.city if school else None,
        "school_address": school.address if school else None,
        "teacher_name": teacher_name,
        "teacher_phone": teacher_phone,
    }
