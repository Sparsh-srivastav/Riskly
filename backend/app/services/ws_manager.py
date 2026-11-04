import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("riskly-ws")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("[WS] Client connected. Total active: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("[WS] Client disconnected. Total active: %d", len(self.active_connections))

    async def broadcast(self, message: dict):
        logger.info("[WS] Broadcasting '%s' to %d clients", message.get("event"), len(self.active_connections))
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning("[WS] Error sending to client: %s", e)
                self.disconnect(connection)

manager = ConnectionManager()
