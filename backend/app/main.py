from fastapi import FastAPI

app = FastAPI(
    title="Riskly API",
    description="Personal Fraud Risk Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status":"ok",
        "service":"riskly-backend",
    }