"""
dYdX WebSocket Connector

Responsibilities:
- Subscribe to derivatives symbols (perpetuals/futures)
- Track trades, orderbook, funding rates
- Normalize events into internal unified format
- Automatic reconnect & failover
- Async / HFT-ready
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, Callable, Any, List

import websockets


class DYDXWS:

    BASE_URL = "wss://api.dydx.exchange/v3/ws"

    def __init__(self):
        self.symbols: List[str] = []
        self.callbacks: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self._ws: Any = None
        self._running = False
        self._reconnect_interval = 5.0

    # ---------------------------------------------------
    # Subscription
    # ---------------------------------------------------

    def subscribe(self, symbol: str, callback: Callable[[Dict[str, Any]], None]):
        if symbol not in self.symbols:
            self.symbols.append(symbol)
        self.callbacks[symbol] = callback

    # ---------------------------------------------------
    # WebSocket handling
    # ---------------------------------------------------

    async def _connect(self):
        async with websockets.connect(self.BASE_URL) as ws:
            self._ws = ws
            await self._subscribe_all()
            await self._listen()

    async def _subscribe_all(self):
        for symbol in self.symbols:
            # Subscribe to trades & orderbook
            msg_trades = json.dumps({"type": "subscribe", "channel": "trades", "id": symbol})
            msg_orderbook = json.dumps({"type": "subscribe", "channel": "orderbook", "id": symbol})
            await self._ws.send(msg_trades)
            await self._ws.send(msg_orderbook)

    async def _listen(self):
        async for msg in self._ws:
            try:
                data = json.loads(msg)
                symbol = data.get("id") or data.get("market")
                if symbol and symbol in self.callbacks:
                    normalized = self._normalize_event(data)
                    self.callbacks[symbol](normalized)
            except Exception as e:
                print("Error processing message:", e)

    # ---------------------------------------------------
    # Event normalization
    # ---------------------------------------------------

    def _normalize_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert dYdX WS event to internal format
        Supports trades and orderbook updates
        """
        event_type = data.get("type")
        symbol = data.get("id") or data.get("market")
        if event_type == "trade":
            return {
                "exchange": "dydx",
                "symbol": symbol,
                "trade_id": str(data.get("tradeId")),
                "price": float(data.get("price")),
                "size": float(data.get("size")),
                "side": data.get("side"),
                "timestamp": float(data.get("timestamp")),
                "type": "trade",
            }
        elif event_type == "orderbook":
            return {
                "exchange": "dydx",
                "symbol": symbol,
                "bids": data.get("bids", []),
                "asks": data.get("asks", []),
                "timestamp": float(data.get("timestamp")),
                "type": "orderbook",
            }
        else:
            # fallback raw
            return {"exchange": "dydx", "symbol": symbol, "raw": data, "type": "unknown"}

    # ---------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------

    async def start(self):
        self._running = True
        while self._running:
            try:
                await self._connect()
            except Exception as e:
                print("WebSocket error, reconnecting in", self._reconnect_interval, "s", e)
                await asyncio.sleep(self._reconnect_interval)

    async def stop(self):
        self._running = False
        if self._ws:
            await self._ws.close()
