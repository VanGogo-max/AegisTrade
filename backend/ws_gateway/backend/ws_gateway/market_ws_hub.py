from typing import Dict
from fastapi import WebSocket


class MarketWSHub:
    def __init__(self, snapshot_cache):
        self.snapshot_cache = snapshot_cache
        self.clients: Dict[str, WebSocket] = {}

    async def start(self):
        # placeholder for background tasks
        pass

    async def publish(self, event: dict):
        for ws in self.clients.values():
            await ws.send_json(event)


async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
