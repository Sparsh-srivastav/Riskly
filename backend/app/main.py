from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=f"{settings.app_name} API",
    description="Personal Fraud Risk Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "riskly-backend",
        "environment": settings.app_env,
    }