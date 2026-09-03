# Maktab Yordamchisi 🎓

Ota-onalarga farzandining maktabga kelgan-kelmaganini ko'rsatuvchi professional
Telegram bot va Telegram Mini App / Web App.

## Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, JWT |
| Telegram | aiogram 3.x, Telegram Bot API, Telegram WebApp API |
| Frontend | React + Vite, TypeScript, Tailwind CSS, Recharts |
| Database | PostgreSQL (dev uchun SQLite fallback) |
| Deployment | Docker Compose, Render/Railway/VPS, Vercel/Netlify |

---

## Loyiha tuzilishi (Project Structure)

```
school-assistant/
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint
│   │   ├── config.py           # .env settings
│   │   ├── database.py         # SQLAlchemy async engine
│   │   ├── models/
│   │   │   └── models.py       # Database models
│   │   ├── schemas/
│   │   │   └── schemas.py      # Pydantic schemas
│   │   ├── api/
│   │   │   ├── deps.py         # Auth dependencies
│   │   │   └── v1/
│   │   │       ├── auth.py     # Auth endpoints
│   │   │       ├── parent.py   # Parent endpoints
│   │   │       ├── teacher.py  # Teacher endpoints
│   │   │       └── admin.py    # Admin endpoints
│   │   ├── services/
│   │   │   └── notifications.py # Telegram notifications
│   │   ├── telegram/           # Aiogram bot
│   │   │   └── handlers/
│   │   │       ├── start.py    # /start, contact
│   │   │       ├── parent.py   # Parent panel
│   │   │       └── teacher.py  # Teacher panel
│   │   └── utils/
│   │       ├── token.py        # JWT
│   │       └── tg_auth.py      # Telegram initData validation
│   ├── alembic/                # Migrations
│   ├── tests/                  # Pytest tests
│   ├── requirements.txt
│   ├── seed.py                 # Seed data
│   └── .env.example
│
├── bot/                        # Telegram bot entry
│   ├── bot.py
│   ├── handlers/
│   └── keyboards/
│
├── frontend/                   # React Web App
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── .env.example
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## O'rnatish bosqichma-bosqich

### 1. Python o'rnatish

Python 3.12+ kerak.

Windows:
```
https://www.python.org/downloads/  -> 3.12.x yuklab olib install
```

Install paytida **"Add Python to PATH"** ni belgilang.

Tekshirish:
```bash
python --version
```

### 2. Node.js o'rnatish

Node 18+ kerak.

```
https://nodejs.org/en/download  ->  LTS yuklab install
```

Tekshirish:
```bash
node --version
npm --version
```

### 3. PostgreSQL

**Option A — Local install:**
```
https://www.postgresql.org/download/
```
Install paytida parol o'rnating (masalan `school_password`).

**Option B — Supabase/Neon (cloud, tavsiya):**
- Supabase: https://supabase.com → New Project
- Neon: https://neon.tech → New Project
- Ular sizga connection string beradi:
```
postgresql://user:password@host:5432/database
```

### 4. Virtual environment

```bash
cd school-assistant/backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 5. pip install

```bash
pip install -r requirements.txt
```

### 6. .env sozlash

```bash
cd backend
cp .env.example .env
```

Keyin `.env` faylini ochib quyidagilarni to'ldiring:

```env
# Telegram Bot
BOT_TOKEN=123456:ABC-DEF...   # BotFather'dan olingan token
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://school:school_password@localhost:5432/school_assistant
# SQLite uchun (dev):
# DATABASE_URL=sqlite+aiosqlite:///./school_assistant.db

# JWT
JWT_SECRET=juda_uzun_tasodifiy_secret_string

# Google Maps (ixtiyoriy)
GOOGLE_MAPS_API_KEY=

# Firebase (ixtiyoriy)
FIREBASE_CREDENTIALS=

# SMS (ixtiyoriy)
SMS_API_KEY=
SMS_API_URL=https://api.sms-provider.com/send

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Maktab
DEFAULT_SCHOOL_START_TIME=08:00

SUPER_ADMIN_PHONE=+998901234567
```

Frontend uchun ham:

```bash
cd frontend
cp .env.example .env
```

### 7. Telegram bot token olish

1. Telegram'da [@BotFather](https://t.me/BotFather)ni oching
2. `/newbot` yuboring
3. Bot nomini yozing: `Maktab Yordamchisi`
4. Username bering: masalan `maktab_yordamchi_bot`
5. BotFather token beradi:
```
1234567890:AAH...
```
6. Shu tokenni `.env`dagi `BOT_TOKEN` va `TELEGRAM_BOT_TOKEN` ga yozing

### 8. Google Maps API olish (ixtiyoriy)

1. [Google Cloud Console](https://console.cloud.google.com/)'ga kiring
2. Yangi project yarating
3. **APIs & Services** → **Enable APIs** → `Maps JavaScript API`
4. **Credentials** → **Create Credentials** → **API key**
5. Shu `API_KEY`ni `.env`dagi `GOOGLE_MAPS_API_KEY`ga yozing

> Eslatma: xaritalar uchun Google Maps kerak bo'lsa. Agar key bo'lmasa,
> tizim xaritani ko'rsatmaydi lekin boshqa funksiyalar ishlayveradi
> (ma'lumot obuna provider/interface orqali olinadi).

### 9. Database migration

Database (PostgreSQL yoki SQLite) ulangandan keyin jadvallar avtomatik
yaratiladi (app ishga tushganda `init_db()` chaqiriladi).

Alembic bilan migration (ixtiyoriy):

```bash
cd backend
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 10. Seed data

Birinchi marta bot/admin ishlatishdan oldin test ma'lumotlarini yuklang:

```bash
cd backend
python seed.py
```

Bu quyidagilarni yaratadi:
- 🏫 **20-maktab** (Qashqadaryo, Shahrisabz shahri)
- 📚 **9-A** sinf (1-smena)
- 👨‍🏫 **Sherzod Karimov** o'qituvchi (`+998901112233`)
- 👨‍👩‍👧 **Feruza Yuldosheva** ota-ona (`+998901234567`)
- 👨‍🎓 **Ibroxijon Alimardonov** o'quvchi
- 📋 Davomat: 3-sentabr Kelgan(07:55), 2-sentabr Kelmagan, 1-sentabr Kelmagan

Test login uchun telefon: `+998901234567`

### 11. Backend ishga tushirish

**SQLite (dev, tez):**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**PostgreSQL:**
`.env`da `DATABASE_URL`ni PostgreSQL'ga o'zgartiring, keyin:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

### 12. Frontend ishga tushirish

```bash
cd frontend
npm install
npm run dev
```

http://localhost:5173 da ochiladi.

> **Muhim:** Web App asosan Telegram ichida ishlaydi. Brauzerda test
> qilish uchun `/login` orqali telefon raqam bilan kirishingiz mumkin,
> yoki sizga kerak bo'lsa mavjud Telegram initData manbani emulyatsiya
> qiling. Telegram ichida bot orqali Web App ochilganda avtomatik login bo'ladi.

### 13. Bot ishga tushirish

```bash
cd school-assistant
python -m bot.bot
```

> `bot.py` `app` paketiga bog'liq, shuning uchun backend bilan birga
> ishlashi kerak. Agar xato bersa:
> ```bash
> cd backend
> PYTHONPATH=.. python -m bot.bot
> ```

Keyin Telegram'da botga `/start` yuboring va telefon raqamingizni
(`+998901234567`) yuboring.

---

## Testlar

Backend:
```bash
cd backend
pytest
```

---

## Production Deployment

### Docker Compose (eng oson)

`.env` faylini loyiha ildizida yarating:
```env
JWT_SECRET=uzun_secret
BOT_TOKEN=your_bot_token
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_MAPS_API_KEY=your_key
```

Keyin:
```bash
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

### Render (backend)

1. [render.com](https://render.com) ga kiring
2. **New** → **Web Service** → repo'ni ulang
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Environment variables `.env` dan.

### Supabase/Neon PostgreSQL

`DATABASE_URL`ni supabase/neon connection string bilan almashtiring:
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
```

### Vercel/Netlify (frontend)

1. Repo'ni import qiling
2. Build command: `npm run build`
3. Output dir: `dist`
4. Env: `VITE_API_URL=https://your-backend-url.com`

---

## API Endpoints

### Auth
| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/api/auth/contact` | Telefon bilan login |
| POST | `/api/auth/telegram` | Telegram initData bilan login |
| GET | `/api/auth/me` | Joriy foydalanuvchi |

### Parent
| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/api/parent/profile` | Ota-ona profili |
| GET | `/api/parent/children` | Farzandlar ro'yxati + bugungi status |
| GET | `/api/parent/attendance/today/{student_id}` | Bugungi davomat |
| GET | `/api/parent/attendance/monthly/{student_id}` | Oylik davomat |
| GET | `/api/parent/statistics/{student_id}` | Statistika |
| GET | `/api/parent/class/{student_id}` | Sinf/maktab ma'lumoti |

### Teacher
| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/api/teacher/classes` | O'qituvchi sinflari |
| GET | `/api/teacher/classes/{id}/students` | Sinf o'quvchilari |
| POST | `/api/teacher/attendance` | Davomat belgilash |
| GET | `/api/teacher/attendance/{class_id}` | Sinf davomati |
| POST | `/api/teacher/notification` | Bildirishnoma yuborish |

### Admin
| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/api/admin/stats` | Statistika |
| GET/POST/PUT/DELETE | `/api/admin/schools` | Maktablar CRUD |
| GET/POST/PUT/DELETE | `/api/admin/classes` | Sinflar CRUD |
| GET/POST/PUT/DELETE | `/api/admin/students` | O'quvchilar CRUD |
| GET/POST/DELETE | `/api/admin/parents` | Ota-onalar CRUD |
| GET/POST/PUT/DELETE | `/api/admin/teachers` | O'qituvchilar CRUD |
| GET | `/api/admin/attendance` | Hammasi davomat |

---

## Xavfsizlik (Security)

- ✅ Passwordlar hash (bcrypt via passlib)
- ✅ JWT access token
- ✅ Telegram WebApp initData HMAC-SHA256 validation
- ✅ SQL injection himoyasi (SQLAlchemy ORM)
- ✅ CORS sozlangan
- ✅ Role/Permission tekshiruvi (parent/teacher/admin)
- ✅ Admin endpointlar himoyalangan
- ✅ API validation (Pydantic)
- ✅ Secret keylar `.env`da, GitHub'ga chiqmaydi
- ✅ `.env.example` yaratilgan

---

## API Integratsiyalar

| Integratsiya | Maqsad | Key manbasi | `.env` |
|---------------|--------|-------------|--------|
| Telegram Bot API | Bot + WebApp | BotFather | `BOT_TOKEN` |
| Telegram WebApp API | Mini App auth | (avtomatik) | `TELEGRAM_BOT_TOKEN` |
| PostgreSQL | Database | local/Supabase/Neon | `DATABASE_URL` |
| Google Maps | Xarita | Google Cloud Console | `GOOGLE_MAPS_API_KEY` |
| Firebase Cloud Messaging | Push xabarlar | Firebase Console | `FIREBASE_CREDENTIALS` |
| SMS provider | SMS xabarlar | SMS provider | `SMS_API_KEY` |

> Google Maps, Firebase va SMS providerlar **ixtiyoriy**. Ular uchun
> `interface`/`provider` arxitekturasi tayyor — key qo'shilsa ishlaydi,
> qo'shilmasa tizim ishlashda davom etadi.

---

## Ro'yxatdan o'tish / Login oqimi

1. Botda `/start` — telefon raqam yuboring (ReplyKeyboard, `request_contact`)
2. Backend raqamni tekshiradi:
   - Mavjud ota-ona → "ota-ona sifatida kirdingiz"
   - Mavjud o'qituvchi → "o'qituvchi sifatida kirdingiz"
   - Topilmasa → "Telefon raqamingiz tizimda topilmadi"
3. Telegram `user_id` saqlanadi
4. Web App Telegram ichida ochilganda `initData` orqali avtomatik autentifikatsiya

---

Mualliflik va loyiha sintaksisi qoidalariga muvofiq barcha ma'lumotlar
real database'da saqlanadi, hech qanday static/fake ma'lumot yo'q.
