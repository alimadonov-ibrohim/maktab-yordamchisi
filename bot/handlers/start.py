from aiogram import Router, F
from aiogram.types import Message, Contact
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from app.database import async_session
from app.models.models import User, Parent, Teacher
from app.utils.token import create_access_token
from bot.keyboards.reply import get_phone_keyboard, get_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Men <b>Maktab yordamchisi</b> botiman!\n\n"
        "📱 Bu bot orqali:\n\n"
        "👨‍👩‍👧 <b>Ota-onalar:</b>\n"
        "- farzandlarining davomatini ko'rish\n"
        "- bugungi holatini ko'rish\n"
        "- kechikishlarni ko'rish\n"
        "- statistikasini ko'rish\n\n"
        "👨‍🏫 <b>O'qituvchilar:</b>\n"
        "- o'quvchilar davomatini belgilash\n"
        "- bildirishnomalar yuborish\n"
        "- sinfni boshqarish\n\n"
        "🔐 Ro'yxatdan o'tish uchun "
        "telefon raqamingizni yuboring.",
        reply_markup=get_phone_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🤖 <b>Maktab Yordamchisi</b>\n\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Yordam\n"
        "/menu - Asosiy menyu\n"
        "/profile - Profil",
        parse_mode="HTML",
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

    if not user:
        await message.answer(
            "❌ Siz tizimda ro'yxatdan o'tmagan.\n"
            "Iltimos, /start buyrug'ini bosing."
        )
        return

    await message.answer(
        f"👋 Xush kelibsiz, {user.first_name}!\n\n"
        f"Sizning rolingiz: {user.role}",
        reply_markup=get_main_menu(user.role),
        parse_mode="HTML",
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

    if not user:
        await message.answer("❌ Profil topilmadi. /start ni bosing.")
        return

    role_text = {
        "parent": "👨‍👩‍👧 Ota-ona",
        "teacher": "👨‍🏫 O'qituvchi",
        "admin": "🔐 Administrator",
    }.get(user.role, user.role)

    await message.answer(
        f"👤 <b>Profil</b>\n\n"
        f"Ism: {user.first_name} {user.last_name}\n"
        f"Telefon: {user.phone}\n"
        f"Roli: {role_text}\n"
        f"Telegram ID: {user.telegram_id or 'Yoqilmagan'}",
        parse_mode="HTML",
    )


@router.message(F.contact)
async def handle_contact(message: Message):
    contact: Contact = message.contact
    phone = contact.phone_number

    if not phone.startswith("+"):
        phone = "+" + phone

    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.phone == phone)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ Telefon raqamingiz tizimda topilmadi.\n"
                "Maktab administratoriga murojaat qiling.",
            )
            return

        if not user.is_active:
            await message.answer(
                "❌ Hisobingiz faollashtirilmagan.\n"
                "Admin bilan bog'laning.",
            )
            return

        user.telegram_id = message.from_user.id

        if user.role == "parent":
            parent_result = await db.execute(
                select(Parent).where(Parent.user_id == user.id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent:
                parent.telegram_id = message.from_user.id
            await message.answer(
                f"✅ Assalomu alaykum, {user.first_name}!\n\n"
                "Siz <b>ota-ona</b> sifatida tizimga kirdingiz.\n\n"
                "Quyidagi tugmalardan foydalaning:",
                reply_markup=get_main_menu("parent"),
                parse_mode="HTML",
            )
        elif user.role == "teacher":
            teacher_result = await db.execute(
                select(Teacher).where(Teacher.user_id == user.id)
            )
            teacher = teacher_result.scalar_one_or_none()
            if teacher:
                teacher.telegram_id = message.from_user.id
            await message.answer(
                f"✅ Assalomu alaykum, {user.first_name}!\n\n"
                "Siz <b'o'qituvchi</b> sifatida tizimga kirdingiz.\n\n"
                "Quyidagi tugmalardan foydalaning:",
                reply_markup=get_main_menu("teacher"),
                parse_mode="HTML",
            )
        elif user.role == "admin":
            await message.answer(
                f"✅ Assalomu alaykum, {user.first_name}!\n\n"
                "Siz <b>administrator</b> sifatida tizimga kirdingiz.\n\n"
                "Web Dashboard: /dashboard",
                parse_mode="HTML",
            )

        await db.commit()
