"""In-process WebSocket fan-out with polling retained as a fallback."""

from fastapi import WebSocket


class EventHub:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def publish(self, event_type: str, payload: dict) -> None:
        stale = []
        for connection in self.connections:
            try:
                await connection.send_json({"type": event_type, "payload": payload})
            except RuntimeError:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)
