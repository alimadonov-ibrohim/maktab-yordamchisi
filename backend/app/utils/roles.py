from app.config import settings

# Ro'yxatga olingan rollar (kamayish tartibida ustunlik)
ADMIN_ROLES = {
    "super_admin": 4,
    "admin": 3,
    "school_admin": 2,
    "teacher": 1,
    "parent": 0,
}


def resolve_role(
    db_role: str, telegram_id=None, phone=None
) -> str:
    """Berilgan user uchun haqiqiy rolni aniqlaydi.

    `SUPER_ADMIN_TELEGRAM_ID` yoki `SUPER_ADMIN_PHONE` ga to'g'ri
    keladigan foydalanuvchi hali 'parent' bo'lsa ham SUPER_ADMIN deb
    qaytariladi. Bu environment orqali super adminni qulay sozlash
    imkonini beradi va SQL/API orqali boshqariladi.
    """
    if settings.SUPER_ADMIN_TELEGRAM_ID:
        super_ids = [
            s.strip()
            for s in settings.SUPER_ADMIN_TELEGRAM_ID.split(",")
            if s.strip()
        ]
        if telegram_id and str(telegram_id) in super_ids:
            return "super_admin"

    if settings.SUPER_ADMIN_PHONE and phone:
        super_phones = [
            p.strip()
            for p in settings.SUPER_ADMIN_PHONE.split(",")
            if p.strip()
        ]
        if phone in super_phones:
            return "super_admin"

    return db_role


def has_admin_access(role: str) -> bool:
    return role in ("super_admin", "admin", "school_admin")


def is_super_admin(role: str) -> bool:
    return role == "super_admin"
