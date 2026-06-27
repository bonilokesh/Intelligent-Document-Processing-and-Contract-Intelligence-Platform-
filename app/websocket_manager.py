from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # Maps document_id to its active WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, document_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[document_id] = websocket

    def disconnect(self, document_id: str):
        if document_id in self.active_connections:
            del self.active_connections[document_id]

    async def send_status(self, document_id: str, stage: int, status: str, data: dict = None):
        """Sends a standardized JSON progress frame to the client browser."""
        if document_id in self.active_connections:
            payload = {
                "document_id": document_id,
                "stage": stage,
                "status": status,  # "processing", "completed", "failed"
                "data": data or {}
            }
            await self.active_connections[document_id].send_json(payload)

manager = ConnectionManager()