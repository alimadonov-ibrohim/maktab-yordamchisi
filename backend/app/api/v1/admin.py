from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.database import get_db
from app.models.models import (
    User, School, Class, Student, Parent, Teacher,
    Attendance, ParentStudent, Notification, AuditLog,
)
from app.schemas.schemas import (
    SchoolCreate, SchoolResponse, ClassCreate, ClassResponse,
    StudentCreate, StudentResponse, ParentCreate, ParentResponse,
    TeacherCreate, TeacherResponse, AdminStats,
)
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


async def _audit(db, user, action, entity_type, entity_id=None, details=None, commit=True):
    db.add(AuditLog(
        user_id=user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    ))
    if commit:
        await db.commit()


# ===== STATS =====
@router.get("/stats")
async def get_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    schools = await db.execute(select(func.count(School.id)))
    classes = await db.execute(select(func.count(Class.id)))
    students = await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    teachers = await db.execute(select(func.count(Teacher.id)))
    parents = await db.execute(select(func.count(Parent.id)))

    today_att = await db.execute(
        select(Attendance).where(Attendance.date == today)
    )
    atts = today_att.scalars().all()
    present = sum(1 for a in atts if a.status == "present")
    absent = sum(1 for a in atts if a.status == "absent")
    late = sum(1 for a in atts if a.status == "late")

    return {
        "total_schools": schools.scalar() or 0,
        "total_classes": classes.scalar() or 0,
        "total_students": students.scalar() or 0,
        "total_teachers": teachers.scalar() or 0,
        "total_parents": parents.scalar() or 0,
        "today_present": present,
        "today_absent": absent,
        "today_late": late,
    }


# ===== SCHOOLS =====
@router.get("/schools")
async def list_schools(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(School).order_by(School.name))
    schools = result.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "region": s.region,
            "city": s.city,
            "address": s.address,
            "phone": s.phone,
        }
        for s in schools
    ]


@router.post("/schools")
async def create_school(
    data: SchoolCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    school = School(**data.model_dump())
    db.add(school)
    await db.commit()
    await db.refresh(school)
    await _audit(
        db, current_user, "create_school", "school", school.id,
        details=f"Created school '{school.name}'",
    )
    return {"id": school.id, "message": "Maktab yaratildi"}


@router.put("/schools/{school_id}")
async def update_school(
    school_id: int,
    data: SchoolCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(school, key, val)
    await db.commit()
    return {"message": "Maktab yangilandi"}


@router.delete("/schools/{school_id}")
async def delete_school(
    school_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    await db.delete(school)
    await db.commit()
    return {"message": "Maktab o'chirildi"}


# ===== CLASSES =====
@router.get("/classes")
async def list_classes(
    school_id: int = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Class)
    if school_id:
        query = query.where(Class.school_id == school_id)
    result = await db.execute(query.order_by(Class.name))
    classes = result.scalars().all()

    result_list = []
    for cls in classes:
        sch_result = await db.execute(
            select(School).where(School.id == cls.school_id)
        )
        school = sch_result.scalar_one_or_none()
        teacher_name = None
        if cls.teacher_id:
            t_result = await db.execute(
                select(Teacher).where(Teacher.id == cls.teacher_id)
            )
            teacher = t_result.scalar_one_or_none()
            if teacher:
                teacher_name = f"{teacher.first_name} {teacher.last_name}"

        student_count_result = await db.execute(
            select(func.count(Student.id)).where(
                and_(Student.class_id == cls.id, Student.is_active == True)
            )
        )
        result_list.append({
            "id": cls.id,
            "name": cls.name,
            "school_id": cls.school_id,
            "school_name": school.name if school else None,
            "grade": cls.grade,
            "shift": cls.shift,
            "teacher_id": cls.teacher_id,
            "teacher_name": teacher_name,
            "student_count": student_count_result.scalar() or 0,
        })

    return result_list


@router.post("/classes")
async def create_class(
    data: ClassCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    cls = Class(**data.model_dump())
    db.add(cls)
    await db.commit()
    await db.refresh(cls)
    await _audit(
        db, current_user, "create_class", "class", cls.id,
        details=f"Created class '{cls.name}'",
    )
    return {"id": cls.id, "message": "Sinf yaratildi"}


@router.put("/classes/{class_id}")
async def update_class(
    class_id: int,
    data: ClassCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(Class.id == class_id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(cls, key, val)
    await db.commit()
    return {"message": "Sinf yangilandi"}


@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(Class.id == class_id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    await db.delete(cls)
    await db.commit()
    return {"message": "Sinf o'chirildi"}


# ===== STUDENTS =====
@router.get("/students")
async def list_students(
    class_id: int = None,
    school_id: int = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Student).where(Student.is_active == True)
    if class_id:
        query = query.where(Student.class_id == class_id)
    if school_id:
        query = query.where(Student.school_id == school_id)
    result = await db.execute(query.order_by(Student.last_name))
    students = result.scalars().all()

    result_list = []
    for st in students:
        cls_name = None
        if st.class_id:
            cls_result = await db.execute(
                select(Class).where(Class.id == st.class_id)
            )
            cls = cls_result.scalar_one_or_none()
            if cls:
                cls_name = cls.name

        parents_list = []
        ps_result = await db.execute(
            select(ParentStudent).where(
                ParentStudent.student_id == st.id
            )
        )
        for ps in ps_result.scalars().all():
            p_result = await db.execute(
                select(Parent).where(Parent.id == ps.parent_id)
            )
            p = p_result.scalar_one_or_none()
            if p:
                parents_list.append({
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "phone": p.phone,
                })

        result_list.append({
            "id": st.id,
            "first_name": st.first_name,
            "last_name": st.last_name,
            "class_id": st.class_id,
            "class_name": cls_name,
            "school_id": st.school_id,
            "parents": parents_list,
        })

    return result_list


@router.post("/students")
async def create_student(
    data: StudentCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    student = Student(**data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    await _audit(
        db, current_user, "create_student", "student", student.id,
        details=f"Created student {student.first_name} {student.last_name}",
    )
    return {"id": student.id, "message": "O'quvchi yaratildi"}


@router.put("/students/{student_id}")
async def update_student(
    student_id: int,
    data: StudentCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(student, key, val)
    await db.commit()
    return {"message": "O'quvchi yangilandi"}


@router.delete("/students/{student_id}")
async def delete_student(
    student_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.is_active = False
    await db.commit()
    return {"message": "O'quvchi o'chirildi"}


# ===== PARENTS =====
@router.get("/parents")
async def list_parents(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Parent).order_by(Parent.last_name))
    parents = result.scalars().all()

    result_list = []
    for p in parents:
        children = []
        ps_result = await db.execute(
            select(ParentStudent).where(ParentStudent.parent_id == p.id)
        )
        for ps in ps_result.scalars().all():
            st_result = await db.execute(
                select(Student).where(Student.id == ps.student_id)
            )
            st = st_result.scalar_one_or_none()
            if st:
                children.append({
                    "id": st.id,
                    "name": f"{st.first_name} {st.last_name}",
                })

        result_list.append({
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "phone": p.phone,
            "telegram_id": p.telegram_id,
            "children": children,
        })

    return result_list


@router.post("/parents")
async def create_parent(
    data: ParentCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = User(
        phone=data.phone,
        role="parent",
        first_name=data.first_name,
        last_name=data.last_name,
        telegram_id=data.telegram_id,
    )
    db.add(user)
    await db.flush()

    parent = Parent(
        user_id=user.id,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        telegram_id=data.telegram_id,
    )
    db.add(parent)
    await db.commit()
    await db.refresh(parent)
    await _audit(
        db, current_user, "create_parent", "parent", parent.id,
        details=f"Created parent {parent.first_name} {parent.last_name}",
    )
    return {"id": parent.id, "message": "Ota-ona yaratildi"}


@router.post("/parents/{parent_id}/link-child/{student_id}")
async def link_child(
    parent_id: int,
    student_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(ParentStudent).where(
            and_(
                ParentStudent.parent_id == parent_id,
                ParentStudent.student_id == student_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Aloqachon mavjud"}

    link = ParentStudent(parent_id=parent_id, student_id=student_id)
    db.add(link)
    await db.commit()
    return {"message": "Bog'landi"}


@router.delete("/parents/{parent_id}")
async def delete_parent(
    parent_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Parent).where(Parent.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    links = await db.execute(
        select(ParentStudent).where(ParentStudent.parent_id == parent_id)
    )
    for link in links.scalars().all():
        await db.delete(link)

    await db.delete(parent)
    if parent.user_id:
        user_result = await db.execute(
            select(User).where(User.id == parent.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.is_active = False

    await db.commit()
    return {"message": "Ota-ona o'chirildi"}


# ===== TEACHERS =====
@router.get("/teachers")
async def list_teachers(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Teacher).order_by(Teacher.last_name))
    teachers = result.scalars().all()

    result_list = []
    for t in teachers:
        cls_result = await db.execute(
            select(Class).where(Class.teacher_id == t.id)
        )
        classes = [
            {"id": c.id, "name": c.name}
            for c in cls_result.scalars().all()
        ]
        result_list.append({
            "id": t.id,
            "first_name": t.first_name,
            "last_name": t.last_name,
            "phone": t.phone,
            "telegram_id": t.telegram_id,
            "classes": classes,
        })

    return result_list


@router.post("/teachers")
async def create_teacher(
    data: TeacherCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = User(
        phone=data.phone,
        role="teacher",
        first_name=data.first_name,
        last_name=data.last_name,
        telegram_id=data.telegram_id,
    )
    db.add(user)
    await db.flush()

    teacher = Teacher(
        user_id=user.id,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        telegram_id=data.telegram_id,
    )
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    await _audit(
        db, current_user, "create_teacher", "teacher", teacher.id,
        details=f"Created teacher {teacher.first_name} {teacher.last_name}",
    )
    return {"id": teacher.id, "message": "O'qituvchi yaratildi"}


@router.put("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    data: TeacherCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Teacher).where(Teacher.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(teacher, key, val)
    if teacher.user_id:
        user_result = await db.execute(
            select(User).where(User.id == teacher.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            for key, val in data.model_dump(exclude_unset=True).items():
                if key in ("first_name", "last_name", "phone"):
                    setattr(user, key, val)

    await db.commit()
    return {"message": "O'qituvchi yangilandi"}


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Teacher).where(Teacher.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    await db.delete(teacher)
    if teacher.user_id:
        user_result = await db.execute(
            select(User).where(User.id == teacher.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.is_active = False

    await db.commit()
    return {"message": "O'qituvchi o'chirildi"}


# ===== ATTENDANCE =====
@router.get("/attendance")
async def list_attendance(
    class_id: int = None,
    att_date: str = None,
    current_user: User = Depends(require_admin),
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

    query = select(Attendance).where(Attendance.date == att_date_obj)
    result = await db.execute(query)
    attendances = result.scalars().all()

    result_list = []
    for att in attendances:
        st_result = await db.execute(
            select(Student).where(Student.id == att.student_id)
        )
        st = st_result.scalar_one_or_none()
        if st:
            if class_id and st.class_id != class_id:
                continue
            cls_name = None
            if st.class_id:
                cls_result = await db.execute(
                    select(Class).where(Class.id == st.class_id)
                )
                cls = cls_result.scalar_one_or_none()
                if cls:
                    cls_name = cls.name

            result_list.append({
                "id": att.id,
                "student_id": att.student_id,
                "student_name": f"{st.first_name} {st.last_name}",
                "class_name": cls_name,
                "status": att.status,
                "arrival_time": (
                    att.arrival_time.strftime("%H:%M")
                    if att.arrival_time
                    else None
                ),
                "late_minutes": att.late_minutes,
                "date": att.date.isoformat(),
            })

    return result_list
