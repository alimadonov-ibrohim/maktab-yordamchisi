from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.config import settings


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(
            text="📱 Telefon raqamni yuborish",
            request_contact=True,
        )
    )
    return builder.as_markup(resize_keyboard=True)


def get_main_menu(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Bitta yagona Telegram Mini App — rol backend tomonidan aniqlanadi
    builder.row(
        InlineKeyboardButton(
            text="📱 Mini App ochish",
            web_app={"url": settings.WEBAPP_URL},
        )
    )

    if role == "parent":
        builder.row(
            InlineKeyboardButton(
                text="📅 Bugun",
                callback_data="today",
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="📊 Statistika",
                callback_data="statistics",
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="🏫 Sinf",
                callback_data="class_info",
            )
        )
    elif role in ("teacher", "admin", "school_admin", "super_admin"):
        builder.row(
            InlineKeyboardButton(
                text="📋 Davomat",
                callback_data="teacher_attendance",
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="👨‍🎓 O'quvchilar",
                callback_data="teacher_students",
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="📢 Bildirishnomalar",
                callback_data="teacher_notifications",
            )
        )

    return builder.as_markup()


def get_teacher_classes_keyboard(classes: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cls in classes:
        builder.row(
            InlineKeyboardButton(
                text=f"📚 {cls['name']} ({cls.get('student_count', 0)} o'quvchi)",
                callback_data=f"teacher_class_{cls['id']}",
            )
        )
    return builder.as_markup()


def get_attendance_keyboard(student_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🟢 Kelgan",
            callback_data=f"att_present_{student_id}",
        ),
        InlineKeyboardButton(
            text="🔴 Kelmagan",
            callback_data=f"att_absent_{student_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🟠 Kechikkan",
            callback_data=f"att_late_{student_id}",
        ),
        InlineKeyboardButton(
            text="🔵 Sababli",
            callback_data=f"att_excused_{student_id}",
        ),
    )
    return builder.as_markup()
