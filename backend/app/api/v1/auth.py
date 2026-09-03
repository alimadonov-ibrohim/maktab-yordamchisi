from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models.models import User, Parent, Teacher
from app.schemas.schemas import (
    ContactAuthRequest,
    TokenResponse,
    TelegramAuthRequest,
    ParentProfile,
    TeacherProfile,
    ClassResponse,
)
from app.utils.token import create_access_token
from app.utils.tg_auth import validate_telegram_webapp
from app.utils.roles import resolve_role
from app.api.deps import get_current_user, require_parent, require_teacher

router = APIRouter(prefix="/auth", tags=["Auth"])

# Telegram ID yoki telefon orqali super admin hisobini yaratish uchun
async def _ensure_admin_users(db):
    from app.config import settings
    if settings.SUPER_ADMIN_TELEGRAM_ID:
        for tg_id in settings.SUPER_ADMIN_TELEGRAM_ID.split(","):
            tg_id = tg_id.strip()
            if not tg_id:
                continue
            try:
                tg_id_int = int(tg_id)
            except ValueError:
                continue
            res = await db.execute(
                select(User).where(User.telegram_id == tg_id_int)
            )
            admin_user = res.scalar_one_or_none()
            phone = f"+{tg_id_int}"
            if not admin_user:
                admin_user = User(
                    phone=phone,
                    role="super_admin",
                    telegram_id=tg_id_int,
                    first_name="Super",
                    last_name="Admin",
                    is_active=True,
                )
                db.add(admin_user)
                await db.flush()
            elif admin_user.role != "super_admin":
                admin_user.role = "super_admin"


@router.post("/contact", response_model=TokenResponse)
async def auth_by_contact(
    request: ContactAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    await _ensure_admin_users(db)

    result = await db.execute(
        select(User).where(User.phone == request.phone)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telefon raqamingiz tizimda topilmadi. "
            "Maktab administratoriga murojaat qiling.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisobingiz faollashtirilmagan.",
        )

    if request.telegram_id:
        user.telegram_id = request.telegram_id
        if user.role == "parent":
            parent_result = await db.execute(
                select(Parent).where(Parent.user_id == user.id)
            )
            parent = parent_result.scalar_one_or_none()
            if parent:
                parent.telegram_id = request.telegram_id
        elif user.role == "teacher":
            teacher_result = await db.execute(
                select(Teacher).where(Teacher.user_id == user.id)
            )
            teacher = teacher_result.scalar_one_or_none()
            if teacher:
                teacher.telegram_id = request.telegram_id
        await db.commit()

    role = resolve_role(user.role, telegram_id=user.telegram_id, phone=user.phone)

    token = create_access_token(
        data={"user_id": user.id, "role": role}
    )
    return TokenResponse(
        access_token=token,
        role=role,
        user_id=user.id,
    )


@router.post("/telegram", response_model=TokenResponse)
async def auth_by_telegram(
    request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    await _ensure_admin_users(db)

    validated = validate_telegram_webapp(request.init_data)
    if not validated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram authentication failed",
        )

    user_data = validated.get("user", {})
    tg_id = user_data.get("id")

    if not tg_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram user data",
        )

    result = await db.execute(
        select(User).where(User.telegram_id == tg_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not linked. "
            "Please register with phone number first.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisobingiz faollashtirilmagan.",
        )

    role = resolve_role(user.role, telegram_id=user.telegram_id, phone=user.phone)

    token = create_access_token(
        data={"user_id": user.id, "role": role}
    )
    return TokenResponse(
        access_token=token,
        role=role,
        user_id=user.id,
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "phone": current_user.phone,
        "role": current_user.role,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,        "telegram_id": current_user.telegram_id,
    }
