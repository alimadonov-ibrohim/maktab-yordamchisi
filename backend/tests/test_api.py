import pytest
import asyncio
from datetime import date, time as dtime
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base, get_db, async_session
from app.models.models import (
    User, School, Class, Student, Parent, Teacher,
    ParentStudent, Attendance,
)
from app.main import app


TEST_DB_URL = "sqlite+aiosqlite:///./test_school_assistant.db"


@pytest.fixture()
async def engine_db():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        school = School(
            name="20-maktab",
            region="Qashqadaryo",
            city="Shahrisabz shahri",
            address="Shahrisabz Uymovut Kuhnur 52",
        )
        db.add(school)
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
        )
        db.add(parent)
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
        )
        att2 = Attendance(
            student_id=student.id,
            date=date(2026, 9, 2),
            status="absent",
        )
        db.add_all([att1, att2])

        await db.commit()

        yield {
            "engine": engine,
            "factory": session_factory,
            "parent_user_id": parent_user.id,
            "teacher_user_id": teacher_user.id,
            "parent_id": parent.id,
            "teacher_id": teacher.id,
            "class_id": cls.id,
            "student_id": student.id,
            "school_id": school.id,
        }

    await engine.dispose()


@pytest.fixture()
async def client(engine_db):
    factory = engine_db["factory"]

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


async def get_parent_token(client):
    res = await client.post("/api/auth/contact", json={
        "phone": "+998901234567",
    })
    return res.json()["access_token"]


async def get_teacher_token(client):
    res = await client.post("/api/auth/contact", json={
        "phone": "+998901112233",
    })
    return res.json()["access_token"]


# ===== AUTH TESTS =====
@pytest.mark.asyncio
async def test_auth_valid_parent(client, engine_db):
    res = await client.post("/api/auth/contact", json={
        "phone": "+998901234567",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "parent"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_auth_invalid_phone(client, engine_db):
    res = await client.post("/api/auth/contact", json={
        "phone": "+9999999999",
    })
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_auth_me(client, engine_db):
    token = await get_parent_token(client)
    res = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "parent"


# ===== PARENT TESTS =====
@pytest.mark.asyncio
async def test_parent_children(client, engine_db):
    token = await get_parent_token(client)
    res = await client.get(
        "/api/parent/children",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["first_name"] == "Ibroxijon"


@pytest.mark.asyncio
async def test_parent_statistics(client, engine_db):
    token = await get_parent_token(client)
    res = await client.get(
        f"/api/parent/statistics/{engine_db['student_id']}",
        params={"month": 9, "year": 2026},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["present_days"] == 1
    assert data["absent_days"] == 1


@pytest.mark.asyncio
async def test_parent_today_attendance(client, engine_db):
    token = await get_parent_token(client)
    res = await client.get(
        f"/api/parent/attendance/today/{engine_db['student_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_parent_class_info(client, engine_db):
    token = await get_parent_token(client)
    res = await client.get(
        f"/api/parent/class/{engine_db['student_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["class_name"] == "9-A"
    assert data["teacher_name"] == "Sherzod Karimov"


# ===== TEACHER TESTS =====
@pytest.mark.asyncio
async def test_teacher_classes(client, engine_db):
    token = await get_teacher_token(client)
    res = await client.get(
        "/api/teacher/classes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["name"] == "9-A"


@pytest.mark.asyncio
async def test_teacher_class_students(client, engine_db):
    token = await get_teacher_token(client)
    res = await client.get(
        f"/api/teacher/classes/{engine_db['class_id']}/students",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_teacher_mark_attendance(client, engine_db):
    token = await get_teacher_token(client)
    res = await client.post(
        "/api/teacher/attendance",
        json={
            "student_id": engine_db["student_id"],
            "status": "present",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "present"


@pytest.mark.asyncio
async def test_teacher_unauthorized(client, engine_db):
    res = await client.post(
        "/api/teacher/attendance",
        json={
            "student_id": engine_db["student_id"],
            "status": "absent",
        },
    )
    assert res.status_code == 401
