import asyncio
import json
from typing import Dict, Set, DefaultDict
from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect


class MarketWSHub:
    def __init__(self):
        # client_id -> websocket
        self.clients: Dict[str, WebSocket] = {}

        # client_id -> set of subscriptions: {("BTCUSDT","trade"), ("ETHUSDT","orderbook")}
        self.subscriptions: DefaultDict[str, Set] = defaultdict(set)

        # (symbol, event_type) -> set(client_id)
        self.reverse_index: DefaultDict[tuple, Set[str]] = defaultdict(set)

        # outbound async queue
        self.queue: asyncio.Queue = asyncio.Queue()

        self.running = False

    # ===== Client Lifecycle =====

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.clients[client_id] = websocket
        print(f"[WSHub] Client connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.clients:
            del self.clients[client_id]

        for key in list(self.subscriptions[client_id]):
            self.reverse_index[key].discard(client_id)

        self.subscriptions.pop(client_id, None)
        print(f"[WSHub] Client disconnected: {client_id}")

    # ===== Subscription Protocol =====

    async def handle_client_message(self, client_id: str, message: str):
        """
        Протокол:
        {
          "action": "subscribe" | "unsubscribe",
          "symbol": "BTCUSDT",
          "stream": "trade" | "orderbook" | "ohlcv"
        }
        """
        msg = json.loads(message)
        key = (msg["symbol"], msg["stream"])

        if msg["action"] == "subscribe":
            self.subscriptions[client_id].add(key)
            self.reverse_index[key].add(client_id)

        elif msg["action"] == "unsubscribe":
            self.subscriptions[client_id].discard(key)
            self.reverse_index[key].discard(client_id)

    # ===== Ingress from Unified Router =====

    async def publish(self, event: Dict):
        """
        Получава normalized събитие от UnifiedMarketDataRouter
        """
        await self.queue.put(event)

    # ===== Fan-out Dispatcher =====

    async def start(self):
        self.running = True
        while self.running:
            event = await self.queue.get()
            await self.dispatch(event)

    async def dispatch(self, event: Dict):
        symbol = event.get("symbol")
        event_type = self.detect_event_type(event)

        if not symbol or not event_type:
            return

        key = (symbol, event_type)
        targets = self.reverse_index.get(key, set())

        if not targets:
            return

        payload = json.dumps(event)

        coros = []
        for client_id in targets:
            ws = self.clients.get(client_id)
            if ws:
                coros.append(ws.send_text(payload))

        await asyncio.gather(*coros, return_exceptions=True)

    # ===== Event Type Detection (same logic as Unified Router) =====

    def detect_event_type(self, event: Dict) -> str:
        if "bids" in event and "asks" in event:
            return "orderbook"
        if "open" in event and "close" in event and "interval" in event:
            return "ohlcv"
        if "price" in event and "quantity" in event:
            return "trade"
        return None


# ========== FastAPI Adapter Layer ==========

market_ws_hub = MarketWSHub()


async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await market_ws_hub.connect(client_id, websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            await market_ws_hub.handle_client_message(client_id, msg)
    except WebSocketDisconnect:
        market_ws_hub.disconnect(client_id)
