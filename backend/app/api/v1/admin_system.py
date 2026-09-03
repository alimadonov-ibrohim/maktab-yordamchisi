from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.models import (
    User, Teacher, Parent, School, AuditLog, Setting, SchoolDay, Notification,
)
from app.api.deps import get_current_user, require_admin, require_super_admin

router = APIRouter(prefix="/admin/system", tags=["Admin System"])


# ===== ADMINS =====
@router.get("/admins")
async def list_admins(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.role.in_(["super_admin", "admin", "school_admin"])
        ).order_by(User.role)
    )
    admins = result.scalars().all()
    return [
        {
            "id": u.id,
            "phone": u.phone,
            "role": u.role,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "telegram_id": u.telegram_id,
            "is_active": u.is_active,
        }
        for u in admins
    ]


@router.post("/admins")
async def create_admin(
    phone: str,
    role: str = "admin",
    first_name: str = "",
    last_name: str = "",
    telegram_id: int = None,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    if role not in ("admin", "school_admin"):
        raise HTTPException(status_code=400, detail="Invalid admin role")

    existing = await db.execute(select(User).where(User.phone == phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Phone already exists")

    user = User(
        phone=phone,
        role=role,
        first_name=first_name or "Admin",
        last_name=last_name,
        telegram_id=telegram_id,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await db.add(AuditLog(
        user_id=current_user.id,
        action="create_admin",
        entity_type="user",
        entity_id=user.id,
        details=f"Created admin group='{role}' phone={phone}",
    ))
    await db.commit()

    return {"id": user.id, "message": f"{role} yaratildi"}


@router.put("/admins/{user_id}")
async def update_admin(
    user_id: int,
    role: str = None,
    first_name: str = None,
    last_name: str = None,
    is_active: bool = None,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="O'z rolingizni o'zgartira olmaysiz"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if role is not None:
        if role not in ("admin", "school_admin", "teacher", "parent"):
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = role
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if is_active is not None:
        user.is_active = is_active

    await db.commit()
    return {"message": "Admin yangilandi"}


@router.delete("/admins/{user_id}")
async def delete_admin(
    user_id: int,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="O'zingizni o'chira olmaysiz"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.role = "parent"
    await db.commit()
    return {"message": "Admin o'chirildi"}


# ===== AUDIT LOG =====
@router.get("/audit")
async def list_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    )
    logs = result.scalars().all()

    result_list = []
    for log in logs:
        actor_name = ""
        if log.user_id:
            u_result = await db.execute(
                select(User).where(User.id == log.user_id)
            )
            actor = u_result.scalar_one_or_none()
            if actor:
                actor_name = f"{actor.first_name or ''} {actor.last_name or ''}".strip()
        result_list.append({
            "id": log.id,
            "user_id": log.user_id,
            "actor_name": actor_name,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": (
                log.created_at.isoformat() if log.created_at else None
            ),
        })

    return result_list


# ===== SETTINGS =====
@router.get("/settings")
async def get_settings(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Setting))
    settings = result.scalars().all()
    return [
        {"key": s.key, "value": s.value, "description": s.description}
        for s in settings
    ]


@router.put("/settings")
async def update_setting(
    key: str,
    value: str,
    description: str = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
    else:
        setting = Setting(key=key, value=value, description=description)
        db.add(setting)

    await db.commit()
    return {"message": "Sozlama saqlandi", "key": key, "value": value}


# ===== SCHOOL DAYS =====
@router.get("/school-days")
async def list_school_days(
    school_id: int = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(SchoolDay)
    if school_id:
        query = query.where(SchoolDay.school_id == school_id)
    result = await db.execute(query.order_by(desc(SchoolDay.date)))
    days = result.scalars().all()
    return [
        {
            "id": d.id,
            "school_id": d.school_id,
            "date": d.date.isoformat(),
            "is_active": d.is_active,
            "start_time": d.start_time.strftime("%H:%M") if d.start_time else None,
        }
        for d in days
    ]


@router.post("/school-days")
async def create_school_day(
    school_id: int,
    day_date: str,
    start_time: str = "08:00",
    is_active: bool = True,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        d = date.fromisoformat(day_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date")

    from datetime import time as dtime
    try:
        h, m = map(int, start_time.split(":"))
        t = dtime(h, m)
    except (ValueError, TypeError):
        t = None

    existing = await db.execute(
        select(SchoolDay).where(
            SchoolDay.school_id == school_id,
            SchoolDay.date == d,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu kun allaqachon mavjud")

    day = SchoolDay(
        school_id=school_id,
        date=d,
        is_active=is_active,
        start_time=t,
    )
    db.add(day)
    await db.commit()
    await db.refresh(day)
    return {"id": day.id, "message": "O'quv kuni yaratildi"}


@router.put("/school-days/{day_id}")
async def update_school_day(
    day_id: int,
    is_active: bool = None,
    start_time: str = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SchoolDay).where(SchoolDay.id == day_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")

    if is_active is not None:
        day.is_active = is_active
    if start_time is not None:
        from datetime import time as dtime
        h, m = map(int, start_time.split(":"))
        day.start_time = dtime(h, m)

    await db.commit()
    return {"message": "O'quv kuni yangilandi"}


@router.delete("/school-days/{day_id}")
async def delete_school_day(
    day_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SchoolDay).where(SchoolDay.id == day_id))
    day = result.scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")

    await db.delete(day)
    await db.commit()
    return {"message": "O'quv kuni o'chirildi"}


# ===== NOTIFICATIONS (broadcast) =====
@router.get("/notifications")
async def list_all_notifications(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).order_by(desc(Notification.created_at)).limit(100)
    )
    notifs = result.scalars().all()
    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


@router.post("/notifications/broadcast")
async def broadcast_notification(
    title: str,
    message: str,
    role: str = "parent",
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.role == role))
    users = result.scalars().all()

    sent = 0
    for u in users:
        db.add(Notification(
            user_id=u.id,
            title=title,
            message=message,
            notification_type="broadcast",
        ))
        sent += 1

    await db.commit()
    return {"message": f"{sent} ta foydalanuvchiga xabar yuborildi"}
