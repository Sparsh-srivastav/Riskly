from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.contact import router as contact_router
from app.routes.report import router as report_router
from app.services.kafka_producer import get_kafka_producer, stop_kafka_producer
from app.services.ws_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect producer
    try:
        await get_kafka_producer()
    except Exception as e:
        print(f"Warning: Could not connect to Kafka on startup: {e}")
    yield
    # Shutdown: clean up producer
    await stop_kafka_producer()


app = FastAPI(
    title="Riskly API",
    description="Real-time multi-signal fraud, spam, and identity risk assessment platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(report_router)


@app.get("/health", tags=["default"])
def health_check():
    return {"status": "ok"}


@app.websocket("/ws/feed")
async def websocket_feed_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
