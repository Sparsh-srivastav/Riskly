from fastapi import FastAPI

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.contact import router as contact_router


app = FastAPI(
    title=f"{settings.app_name} API",
    description="Personal Fraud Risk Intelligence Platform",
    version="0.1.0",
)


app.include_router(auth_router)
app.include_router(contact_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "riskly-backend",
        "environment": settings.app_env,
    }