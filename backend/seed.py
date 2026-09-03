import asyncio
from datetime import date, time as dtime
from app.database import async_session, init_db
from app.models.models import (
    User, School, Class, Student, Parent,
    ParentStudent, Attendance, Teacher,
)


async def seed():
    await init_db()
    async with async_session() as db:
        from sqlalchemy import select

        existing = await db.execute(select(School).limit(1))
        if existing.scalar_one_or_none():
            print("Database already seeded.")
            return

        school = School(
            name="20-maktab",
            region="Qashqadaryo",
            city="Shahrisabz shahri",
            address="Shahrisabz shahar Uymovut MFY Kuhnur 52",
            phone="+998662331234",
        )
        db.add(school)
        await db.flush()

        teacher_user = User(
            phone="+998901112233",
            role="teacher",
            first_name="Sherzod",
            last_name="Karimov",
        )
        db.add(teacher_user)
        await db.flush()

        teacher = Teacher(
            user_id=teacher_user.id,
            first_name="Sherzod",
            last_name="Karimov",
            phone="+998901112233",
        )
        db.add(teacher)
        await db.flush()

        cls = Class(
            name="9-A",
            school_id=school.id,
            grade=9,
            shift="1-smena",
            teacher_id=teacher.id,
        )
        db.add(cls)
        await db.flush()

        parent_user = User(
            phone="+998901234567",
            role="parent",
            first_name="Feruza",
            last_name="Yuldosheva",
        )
        db.add(parent_user)
        await db.flush()

        parent = Parent(
            user_id=parent_user.id,
            first_name="Feruza",
            last_name="Yuldosheva",
            phone="+998901234567",
            telegram_id=None,
        )
        db.add(parent)
        await db.flush()

        student = Student(
            first_name="Ibroxijon",
            last_name="Alimardonov",
            class_id=cls.id,
            school_id=school.id,
        )
        db.add(student)
        await db.flush()

        link = ParentStudent(parent_id=parent.id, student_id=student.id)
        db.add(link)

        att1 = Attendance(
            student_id=student.id,
            date=date(2026, 9, 3),
            status="present",
            arrival_time=dtime(7, 55),
            late_minutes=0,
        )
        att2 = Attendance(
            student_id=student.id,
            date=date(2026, 9, 2),
            status="absent",
        )
        att3 = Attendance(
            student_id=student.id,
            date=date(2026, 9, 1),
            status="absent",
        )
        db.add_all([att1, att2, att3])

        await db.commit()
        print("Seed data created successfully!")
        print(f"  School: {school.name} (id={school.id})")
        print(f"  Class: {cls.name} (id={cls.id})")
        print(f"  Teacher: {teacher.first_name} {teacher.last_name} (id={teacher.id})")
        print(f"  Parent: {parent.first_name} {parent.last_name} (id={parent.id})")
        print(f"  Student: {student.first_name} {student.last_name} (id={student.id})")
        print(f"  Phone: {parent.phone}")
        print(f"  Attendance: 3 days seeded")


if __name__ == "__main__":
    asyncio.run(seed())
