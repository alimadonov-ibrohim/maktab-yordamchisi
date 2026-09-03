from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Maktab Yordamchisi API",
    description="School Assistant Telegram Bot & Web App API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.v1.auth import router as auth_router
from app.api.v1.parent import router as parent_router
from app.api.v1.teacher import router as teacher_router
from app.api.v1.admin import router as admin_router
from app.api.v1.admin_system import router as admin_system_router

app.include_router(auth_router, prefix="/api")
app.include_router(parent_router, prefix="/api")
app.include_router(teacher_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(admin_system_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Maktab Yordamchisi API"}
