from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth
from app.core.dependencies import get_current_user
from app.core.scheduler import start_scheduler
from fastapi import Depends
from app.api import inventory
from app.api import detection
from app.api import incoming
from app.api import dashboard
from app.api import outgoing
from app.api import admin
from app.api import cron

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# =========================
# CORS (Untuk frontend Vue)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nanti ganti ke domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    start_scheduler()

# =========================
# Root Endpoint
# =========================
@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running 🚀",
        "environment": settings.APP_ENV
    }

# =========================
# Health Check
# =========================
@app.get("/health")
def health_check():
    return {"status": "ok"}

# =========================
# Auth
# =========================
app.include_router(auth.router)

@app.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role
    }

# =========================
# Inventory Upload
# =========================
app.include_router(inventory.router)

# =========================
# Detection
# =========================
app.include_router(detection.router)

# =========================
# Incoming
# =========================
app.include_router(incoming.router)

# =========================
# Outgoing
# =========================
app.include_router(outgoing.router)

# =========================
# Dashboard
# =========================
app.include_router(dashboard.router)

# =========================
# Admin
# =========================
app.include_router(admin.router)

# =========================
# Cron
# =========================
app.include_router(cron.router)
