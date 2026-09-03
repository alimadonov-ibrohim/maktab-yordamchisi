from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, and_
from datetime import date, datetime
from app.database import async_session
from app.models.models import (
    User, Parent, Student, Class, School,
    Attendance, ParentStudent, Teacher,
)

router = Router()


@router.callback_query(F.data == "today")
async def today_handler(callback: CallbackQuery):
    async with async_session() as db:
        user_result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        if not user or user.role != "parent":
            await callback.answer("Ruxsat yo'q")
            return

        parent_result = await db.execute(
            select(Parent).where(Parent.user_id == user.id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            await callback.answer("Profil topilmadi")
            return

        ps_result = await db.execute(
            select(ParentStudent.student_id).where(
                ParentStudent.parent_id == parent.id
            )
        )
        student_ids = [row[0] for row in ps_result.all()]

        if not student_ids:
            await callback.message.edit_text(
                "👤 Farzandlaringiz topilmadi."
            )
            await callback.answer()
            return

        today = date.today()
        text = f"📅 <b>Bugun: {today.strftime('%d.%m.%Y')}</b>\n\n"

        for sid in student_ids:
            st_result = await db.execute(
                select(Student).where(Student.id == sid)
            )
            student = st_result.scalar_one_or_none()
            if not student:
                continue

            class_name = ""
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
                        Attendance.student_id == sid,
                        Attendance.date == today,
                    )
                )
            )
            att = att_result.scalar_one_or_none()

            text += f"👤 <b>{student.first_name} {student.last_name}</b>\n"
            text += f"🏫 {class_name}\n"

            if att:
                status_emoji = {
                    "present": "🟢",
                    "absent": "🔴",
                    "late": "🟠",
                    "excused": "🔵",
                }.get(att.status, "⚪")
                status_text = {
                    "present": "Maktabda",
                    "absent": "Maktabga kelmagan",
                    "late": f"Kechikkan ({att.late_minutes} daqiqa)",
                    "excused": "Sababli",
                }.get(att.status, "Noma'lum")

                text += f"{status_emoji} {status_text}\n"
                if att.arrival_time:
                    text += f"⏰ {att.arrival_time.strftime('%H:%M')}\n"
            else:
                text += "⚪ Davomat belgilanmagan\n"

            text += "\n"

        await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "statistics")
async def statistics_handler(callback: CallbackQuery):
    async with async_session() as db:
        user_result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        if not user or user.role != "parent":
            await callback.answer("Ruxsat yo'q")
            return

        parent_result = await db.execute(
            select(Parent).where(Parent.user_id == user.id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            await callback.answer("Profil topilmadi")
            return

        ps_result = await db.execute(
            select(ParentStudent.student_id).where(
                ParentStudent.parent_id == parent.id
            )
        )
        student_ids = [row[0] for row in ps_result.all()]

        today = date.today()

        text = f"📊 <b>Statistika — {today.strftime('%B %Y')}</b>\n\n"

        for sid in student_ids:
            st_result = await db.execute(
                select(Student).where(Student.id == sid)
            )
            student = st_result.scalar_one_or_none()
            if not student:
                continue

            att_result = await db.execute(
                select(Attendance).where(Attendance.student_id == sid)
            )
            all_att = att_result.scalars().all()

            monthly = [
                a for a in all_att
                if a.date.month == today.month and a.date.year == today.year
            ]

            school_days = today.day
            present = sum(1 for a in monthly if a.status == "present")
            absent = sum(1 for a in monthly if a.status == "absent")
            late_count = sum(1 for a in monthly if a.status == "late")
            excused = sum(1 for a in monthly if a.status == "excused")

            pct = (present / school_days * 100) if school_days > 0 else 0

            text += f"👤 <b>{student.first_name} {student.last_name}</b>\n\n"
            text += f"📊 <b>{pct:.0f}%</b> Davomat\n\n"
            text += f"🔵 O'quv kunlari: <b>{school_days}</b>\n"
            text += f"🟢 Kelgan: <b>{present}</b>\n"
            text += f"🔴 Kelmagan: <b>{absent}</b>\n"
            text += f"🟠 Kechikkan: <b>{late_count}</b>\n"
            text += f"🔵 Sababli: <b>{excused}</b>\n\n"

        await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "class_info")
async def class_info_handler(callback: CallbackQuery):
    async with async_session() as db:
        user_result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        if not user or user.role != "parent":
            await callback.answer("Ruxsat yo'q")
            return

        parent_result = await db.execute(
            select(Parent).where(Parent.user_id == user.id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            await callback.answer("Profil topilmadi")
            return

        ps_result = await db.execute(
            select(ParentStudent.student_id).where(
                ParentStudent.parent_id == parent.id
            )
        )
        student_ids = [row[0] for row in ps_result.all()]

        text = "🏫 <b>Sinf ma'lumotlari</b>\n\n"

        found = False
        for sid in student_ids:
            st_result = await db.execute(
                select(Student).where(Student.id == sid)
            )
            student = st_result.scalar_one_or_none()
            if not student or not student.class_id:
                continue

            cls_result = await db.execute(
                select(Class).where(Class.id == student.class_id)
            )
            cls = cls_result.scalar_one_or_none()
            if not cls:
                continue

            sch_result = await db.execute(
                select(School).where(School.id == cls.school_id)
            )
            school = sch_result.scalar_one_or_none()

            found = True
            text += f"👤 <b>{student.first_name} {student.last_name}</b>\n\n"
            text += f"🏫 <b>MAKTAB</b>\n"
            school_name_val = school.name if school else "Noma'lum"
            text += f"{school_name_val}\n"
            if school:
                if school.region:
                    text += f"Viloyat: {school.region}\n"
                if school.city:
                    text += f"Shahar: {school.city}\n"
                if school.address:
                    text += f"Manzil: {school.address}\n"
            text += "\n"

            text += f"📚 <b>SINF</b>\n{cls.name}\n"
            if cls.shift:
                text += f"Smena: {cls.shift}\n"
            text += "\n"

            text += "👨‍🏫 <b>SINF RAHBARI</b>\n"
            if cls.teacher_id:
                t_result = await db.execute(
                    select(Teacher).where(Teacher.id == cls.teacher_id)
                )
                teacher = t_result.scalar_one_or_none()
                if teacher:
                    text += f"{teacher.first_name} {teacher.last_name}\n"
                    text += f"📞 {teacher.phone}\n"
                else:
                    text += "Sinf rahbari topilmadi\n"
            else:
                text += "Sinf rahbari biriktirilmagan\n"

        if not found:
            text += "Sinf ma'lumotlari topilmadi."

        await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
