from datetime import date, datetime, time as dtime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models.models import (
    User, Teacher, Student, Class, School,
    Attendance,
)
from app.schemas.schemas import (
    ClassResponse, StudentInClass,
    AttendanceCreate, AttendanceUpdate,
)
from app.api.deps import get_current_user, require_teacher

router = APIRouter(prefix="/teacher", tags=["Teacher"])


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    cls_result = await db.execute(
        select(Class).where(Class.teacher_id == teacher.id)
    )
    classes = cls_result.scalars().all()

    class_list = []
    for cls in classes:
        student_count_result = await db.execute(
            select(Student).where(
                and_(
                    Student.class_id == cls.id,
                    Student.is_active == True,
                )
            )
        )
        student_count = len(student_count_result.scalars().all())
        class_list.append({
            "id": cls.id,
            "name": cls.name,
            "grade": cls.grade,
            "shift": cls.shift,
            "student_count": student_count,
        })

    return {
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "phone": teacher.phone,
        "telegram_id": teacher.telegram_id,
        "classes": class_list,
    }


@router.get("/classes")
async def get_classes(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    cls_result = await db.execute(
        select(Class).where(Class.teacher_id == teacher.id)
    )
    classes = cls_result.scalars().all()

    result_list = []
    for cls in classes:
        student_count_result = await db.execute(
            select(Student).where(
                and_(Student.class_id == cls.id, Student.is_active == True)
            )
        )
        student_count = len(student_count_result.scalars().all())
        result_list.append({
            "id": cls.id,
            "name": cls.name,
            "grade": cls.grade,
            "shift": cls.shift,
            "student_count": student_count,
        })

    return result_list


@router.get("/classes/{class_id}/students")
async def get_class_students(
    class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    teacher_result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = teacher_result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    cls_result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    cls = cls_result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    if current_user.role != "admin" and cls.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403, detail="Not your class"
        )

    students_result = await db.execute(
        select(Student).where(
            and_(Student.class_id == class_id, Student.is_active == True)
        ).order_by(Student.last_name)
    )
    students = students_result.scalars().all()

    today = date.today()
    result_list = []
    for st in students:
        att_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.student_id == st.id,
                    Attendance.date == today,
                )
            )
        )
        att = att_result.scalar_one_or_none()
        result_list.append({
            "id": st.id,
            "first_name": st.first_name,
            "last_name": st.last_name,
            "today_status": att.status if att else "no_data",
            "arrival_time": (
                att.arrival_time.strftime("%H:%M")
                if att and att.arrival_time
                else None
            ),
        })

    return result_list


@router.post("/attendance")
async def create_attendance(
    data: AttendanceCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    teacher_result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = teacher_result.scalar_one_or_none()
    if not teacher and current_user.role != "admin":
        raise HTTPException(status_code=404, detail="Teacher not found")

    student_result = await db.execute(
        select(Student).where(Student.id == data.student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.class_id and current_user.role != "admin":
        cls_result = await db.execute(
            select(Class).where(Class.id == student.class_id)
        )
        cls = cls_result.scalar_one_or_none()
        if cls and cls.teacher_id != teacher.id:
            raise HTTPException(
                status_code=403, detail="Not your class student"
            )

    today = date.today()
    existing_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.student_id == data.student_id,
                Attendance.date == today,
            )
        )
    )
    existing = existing_result.scalar_one_or_none()

    now = datetime.now()
    current_time = now.time()

    from app.config import settings
    start_time_str = settings.DEFAULT_SCHOOL_START_TIME
    h, m = map(int, start_time_str.split(":"))
    start_time = dtime(h, m)

    late_minutes = 0
    if data.status == "present" and current_time > start_time:
        delta_min = (
            current_time.hour * 60 + current_time.minute
        ) - (start_time.hour * 60 + start_time.minute)
        late_minutes = max(0, delta_min)

    if existing:
        existing.status = data.status
        if data.status == "present":
            existing.arrival_time = current_time
            existing.late_minutes = late_minutes
        existing.reason = data.reason
        await db.commit()
        await db.refresh(existing)
        await _notify_parents(db, student.id, data.status, existing, class_name=None)
        return {
            "id": existing.id,
            "status": existing.status,
            "message": "Davomat yangilandi",
        }

    att = Attendance(
        student_id=data.student_id,
        date=today,
        status=data.status,
        arrival_time=current_time if data.status in ("present", "late") else None,
        late_minutes=late_minutes,
        reason=data.reason,
    )
    db.add(att)
    await db.commit()
    await db.refresh(att)
    await _notify_parents(db, student.id, data.status, att, class_name=None)

    return {
        "id": att.id,
        "status": att.status,
        "message": "Davomat belgilandi",
    }


async def _notify_parents(db, student_id: int, status: str, att, class_name=None):
    from app.models.models import ParentStudent, Parent, Class
    from app.services.notifications import notifier

    if not notifier._bot:
        return

    st_result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = st_result.scalar_one_or_none()
    if not student:
        return

    if not class_name and student.class_id:
        cls_result = await db.execute(
            select(Class).where(Class.id == student.class_id)
        )
        cls = cls_result.scalar_one_or_none()
        class_name = cls.name if cls else ""

    student_name = f"{student.first_name} {student.last_name}"
    class_label = f"{class_name} sinf" if class_name else ""

    ps_result = await db.execute(
        select(ParentStudent).where(ParentStudent.student_id == student_id)
    )
    for ps in ps_result.scalars().all():
        parent_result = await db.execute(
            select(Parent).where(Parent.id == ps.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent or not parent.telegram_id:
            continue

        time_str = (
            att.arrival_time.strftime("%H:%M")
            if att and att.arrival_time
            else None
        )
        try:
            if status == "present":
                await notifier.notify_present(
                    parent.telegram_id, student_name, class_label, time_str or "--:--"
                )
            elif status == "absent":
                await notifier.notify_absent(parent.telegram_id, student_name, class_label)
            elif status == "late":
                await notifier.notify_late(
                    parent.telegram_id,
                    student_name,
                    class_label,
                    time_str or "--:--",
                    late_minutes=att.late_minutes if att else 0,
                )
        except Exception:
            pass


@router.put("/attendance/{attendance_id}")
async def update_attendance(
    attendance_id: int,
    data: AttendanceUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    att_result = await db.execute(
        select(Attendance).where(Attendance.id == attendance_id)
    )
    att = att_result.scalar_one_or_none()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance not found")

    if data.status is not None:
        att.status = data.status
    if data.departure_time is not None:
        parts = data.departure_time.split(":")
        att.departure_time = dtime(int(parts[0]), int(parts[1]))
    if data.reason is not None:
        att.reason = data.reason

    await db.commit()
    await db.refresh(att)

    return {
        "id": att.id,
        "status": att.status,
        "message": "Davomat yangilandi",
    }


@router.get("/attendance/{class_id}")
async def get_class_attendance(
    class_id: int,
    att_date: str = None,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    if att_date:
        try:
            att_date_obj = date.fromisoformat(att_date)
        except ValueError:
            att_date_obj = today
    else:
        att_date_obj = today

    students_result = await db.execute(
        select(Student).where(
            and_(Student.class_id == class_id, Student.is_active == True)
        )
    )
    students = students_result.scalars().all()

    result_list = []
    for st in students:
        att_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.student_id == st.id,
                    Attendance.date == att_date_obj,
                )
            )
        )
        att = att_result.scalar_one_or_none()
        result_list.append({
            "student_id": st.id,
            "first_name": st.first_name,
            "last_name": st.last_name,
            "status": att.status if att else "no_data",
            "arrival_time": (
                att.arrival_time.strftime("%H:%M")
                if att and att.arrival_time
                else None
            ),
            "late_minutes": att.late_minutes if att else 0,
        })

    return result_list


@router.post("/notification")
async def send_notification(
    class_id: int,
    title: str,
    message: str,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    from app.models.models import ParentStudent, Parent, Notification

    teacher_result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = teacher_result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    cls_result = await db.execute(
        select(Class).where(Class.id == class_id)
    )
    cls = cls_result.scalar_one_or_none()
    if not cls or cls.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Not your class")

    students_result = await db.execute(
        select(Student).where(
            and_(Student.class_id == class_id, Student.is_active == True)
        )
    )
    students = students_result.scalars().all()

    sent_count = 0
    for st in students:
        ps_result = await db.execute(
            select(ParentStudent).where(
                ParentStudent.student_id == st.id
            )
        )
        ps_list = ps_result.scalars().all()
        for ps in ps_list:
            parent_result = await db.execute(
                select(Parent).where(Parent.id == ps.parent_id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent and parent.user_id:
                notif = Notification(
                    user_id=parent.user_id,
                    title=title,
                    message=message,
                    notification_type="teacher_message",
                )
                db.add(notif)
                sent_count += 1

    await db.commit()

    return {"message": f"{sent_count} ta xabar yuborildi"}
