from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, and_
from datetime import date, datetime, time as dtime
from app.database import async_session
from app.models.models import (
    User, Teacher, Student, Class, Attendance,
)
from app.config import settings
from bot.keyboards.reply import (
    get_teacher_classes_keyboard,
    get_attendance_keyboard,
)

router = Router()


class AttendanceState(StatesGroup):
    selecting_class = State()
    selecting_student = State()
    marking_attendance = State()


@router.callback_query(F.data == "teacher_attendance")
async def teacher_attendance(callback: CallbackQuery, state: FSMContext):
    async with async_session() as db:
        user_result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        if not user or user.role != "teacher":
            await callback.answer("Ruxsat yo'q")
            return

        teacher_result = await db.execute(
            select(Teacher).where(Teacher.user_id == user.id)
        )
        teacher = teacher_result.scalar_one_or_none()
        if not teacher:
            await callback.answer("Profil topilmadi")
            return

        cls_result = await db.execute(
            select(Class).where(Class.teacher_id == teacher.id)
        )
        classes = cls_result.scalars().all()

        if not classes:
            await callback.message.edit_text(
                "📋 Sizga biriktirilgan sinflar topilmadi."
            )
            await callback.answer()
            return

        class_list = []
        for cls in classes:
            sc_result = await db.execute(
                select(Student).where(
                    and_(
                        Student.class_id == cls.id,
                        Student.is_active == True,
                    )
                )
            )
            count = len(sc_result.scalars().all())
            class_list.append({
                "id": cls.id,
                "name": cls.name,
                "student_count": count,
            })

        await callback.message.edit_text(
            "📋 <b>Davomat belgilash</b>\n\n"
            "Sinfni tanlang:",
            parse_mode="HTML",
        )
        await callback.message.edit_reply_markup(
            reply_markup=get_teacher_classes_keyboard(class_list)
        )
        await state.set_state(AttendanceState.selecting_class)
    await callback.answer()


@router.callback_query(
    F.data.startswith("teacher_class_"),
    AttendanceState.selecting_class,
)
async def select_class_attendance(
    callback: CallbackQuery, state: FSMContext
):
    class_id = int(callback.data.replace("teacher_class_", ""))

    async with async_session() as db:
        students_result = await db.execute(
            select(Student).where(
                and_(
                    Student.class_id == class_id,
                    Student.is_active == True,
                )
            ).order_by(Student.last_name)
        )
        students = students_result.scalars().all()

        if not students:
            await callback.message.edit_text(
                "Bu sinfda o'quvchilar topilmadi."
            )
            await state.clear()
            await callback.answer()
            return

        today = date.today()
        cls_result = await db.execute(
            select(Class).where(Class.id == class_id)
        )
        cls = cls_result.scalar_one_or_none()
        class_name = cls.name if cls else "Noma'lum"

        await state.update_data(class_id=class_id)

        text = f"📋 <b>{class_name} — Davomat</b>\n"
        text += f"📅 {today.strftime('%d.%m.%Y')}\n\n"

        for i, st in enumerate(students, 1):
            att_result = await db.execute(
                select(Attendance).where(
                    and_(
                        Attendance.student_id == st.id,
                        Attendance.date == today,
                    )
                )
            )
            att = att_result.scalar_one_or_none()

            if att:
                status_emoji = {
                    "present": "🟢",
                    "absent": "🔴",
                    "late": "🟠",
                    "excused": "🔵",
                }.get(att.status, "⚪")
                status_text = att.status
            else:
                status_emoji = "⚪"
                status_text = "belgilanmagan"

            text += f"{i}. {status_emoji} {st.first_name} {st.last_name} — {status_text}\n"

        text += "\nO'quvchini tanlang (raqamini yuboring):"

        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        builder_parts = []
        row = []
        for st in students:
            row.append(
                InlineKeyboardButton(
                    text=f"{st.first_name[0]}.{st.last_name}",
                    callback_data=f"mark_student_{st.id}",
                )
            )
            if len(row) == 2:
                builder_parts.append(row)
                row = []
        if row:
            builder_parts.append(row)

        kb = InlineKeyboardMarkup(inline_keyboard=builder_parts)
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.message.edit_reply_markup(reply_markup=kb)
        await state.set_state(AttendanceState.marking_attendance)
    await callback.answer()


@router.callback_query(
    F.data.startswith("mark_student_"),
    AttendanceState.marking_attendance,
)
async def mark_student(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.replace("mark_student_", ""))

    async with async_session() as db:
        st_result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = st_result.scalar_one_or_none()
        if not student:
            await callback.answer("O'quvchi topilmadi")
            return

        await state.update_data(student_id=student_id)

        await callback.message.edit_text(
            f"👤 <b>{student.first_name} {student.last_name}</b>\n\n"
            "Holatni belgilang:",
            parse_mode="HTML",
            reply_markup=get_attendance_keyboard(student_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("att_present_"))
async def mark_present(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.replace("att_present_", ""))
    await _save_attendance(callback, state, student_id, "present")


@router.callback_query(F.data.startswith("att_absent_"))
async def mark_absent(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.replace("att_absent_", ""))
    await _save_attendance(callback, state, student_id, "absent")


@router.callback_query(F.data.startswith("att_late_"))
async def mark_late(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.replace("att_late_", ""))
    await _save_attendance(callback, state, student_id, "late")


@router.callback_query(F.data.startswith("att_excused_"))
async def mark_excused(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.replace("att_excused_", ""))
    await _save_attendance(callback, state, student_id, "excused")


async def _save_attendance(
    callback: CallbackQuery,
    state: FSMContext,
    student_id: int,
    status: str,
):
    today = date.today()
    now = datetime.now()
    current_time = now.time()

    start_time_str = settings.DEFAULT_SCHOOL_START_TIME
    h, m = map(int, start_time_str.split(":"))
    start_time = dtime(h, m)

    late_minutes = 0
    if status == "present" and current_time > start_time:
        delta_min = (
            current_time.hour * 60 + current_time.minute
        ) - (start_time.hour * 60 + start_time.minute)
        late_minutes = max(0, delta_min)

    status_emoji = {
        "present": "🟢",
        "absent": "🔴",
        "late": "🟠",
        "excused": "🔵",
    }.get(status, "⚪")

    status_text = {
        "present": "Kelgan",
        "absent": "Kelmagan",
        "late": "Kechikkan",
        "excused": "Sababli",
    }.get(status, status)

    async with async_session() as db:
        existing_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.date == today,
                )
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.status = status
            if status in ("present", "late"):
                existing.arrival_time = current_time
            existing.late_minutes = late_minutes
        else:
            att = Attendance(
                student_id=student_id,
                date=today,
                status=status,
                arrival_time=(
                    current_time if status in ("present", "late") else None
                ),
                late_minutes=late_minutes,
            )
            db.add(att)

        await db.commit()

    st_result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = st_result.scalar_one_or_none()
    student_name = (
        f"{student.first_name} {student.last_name}"
        if student
        else "Noma'lum"
    )

    await callback.message.edit_text(
        f"✅ Davomat belgilandi!\n\n"
        f"👤 {student_name}\n"
        f"{status_emoji} {status_text}\n"
        f"⏰ {current_time.strftime('%H:%M')}\n"
        + (
            f"⚠️ {late_minutes} daqiqa kechikdi"
            if late_minutes > 0
            else ""
        ),
        parse_mode="HTML",
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "teacher_students")
async def teacher_students(callback: CallbackQuery):
    async with async_session() as db:
        user_result = await db.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        if not user or user.role != "teacher":
            await callback.answer("Ruxsat yo'q")
            return

        teacher_result = await db.execute(
            select(Teacher).where(Teacher.user_id == user.id)
        )
        teacher = teacher_result.scalar_one_or_none()
        if not teacher:
            await callback.answer("Profil topilmadi")
            return

        cls_result = await db.execute(
            select(Class).where(Class.teacher_id == teacher.id)
        )
        classes = cls_result.scalars().all()

        text = "👨‍🎓 <b>O'quvchilar</b>\n\n"
        for cls in classes:
            students_result = await db.execute(
                select(Student).where(
                    and_(
                        Student.class_id == cls.id,
                        Student.is_active == True,
                    )
                ).order_by(Student.last_name)
            )
            students = students_result.scalars().all()
            text += f"📚 <b>{cls.name}</b> ({len(students)} ta)\n"
            for i, st in enumerate(students, 1):
                text += f"  {i}. {st.first_name} {st.last_name}\n"
            text += "\n"

        if not text.strip() or text == "👨‍🎓 <b>O'quvchilar</b>\n\n":
            text += "O'quvchilar topilmadi."

        await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "teacher_notifications")
async def teacher_notifications(callback: CallbackQuery):
    await callback.message.edit_text(
        "📢 <b>Bildirishnomalar</b>\n\n"
        "Bu funksiya tez orada qo'shiladi.\n"
        "Web Dashboard orqali bildirishnomalar yuborishingiz mumkin.",
        parse_mode="HTML",
    )
    await callback.answer()
