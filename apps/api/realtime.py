"""In-process WebSocket fan-out with polling retained as a fallback."""

from fastapi import WebSocket, WebSocketDisconnect


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
        # A genuinely dropped connection (phone loses Wi-Fi, tab closed) surfaces as
        # WebSocketDisconnect from Starlette's send(), not RuntimeError -- catching
        # only RuntimeError let one stale client crash the whole broadcast and block
        # delivery to every client still connected after it in the list.
        stale = []
        for connection in self.connections:
            try:
                await connection.send_json({"type": event_type, "payload": payload})
            except (RuntimeError, WebSocketDisconnect):
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)
