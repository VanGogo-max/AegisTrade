"""
Hyperliquid WebSocket Connector

Responsibilities:
- Subscribe to multiple symbols (trades, orderbook, OHLCV)
- Normalize events into unified internal format
- Automatic reconnect & failover
- Async / HFT-friendly
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, Callable, Any, List

import websockets


class HyperliquidWS:

    BASE_URL = "wss://api.hyperliquid.com/ws"

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
        # Hyperliquid allows subscription via JSON
        async with websockets.connect(self.BASE_URL) as ws:
            self._ws = ws
            await self._subscribe_all()
            await self._listen()

    async def _subscribe_all(self):
        for symbol in self.symbols:
            msg = json.dumps({"op": "subscribe", "channel": "trades", "symbol": symbol})
            await self._ws.send(msg)

    async def _listen(self):
        async for msg in self._ws:
            try:
                data = json.loads(msg)
                # Example trade message: {"symbol":"BTCUSDT","price":50000,"size":0.1,"side":"buy","ts":1640000000}
                symbol = data.get("symbol")
                if symbol and symbol in self.callbacks:
                    normalized = self._normalize_trade(data)
                    self.callbacks[symbol](normalized)
            except Exception as e:
                print("Error processing message:", e)

    # ---------------------------------------------------
    # Trade normalization
    # ---------------------------------------------------

    def _normalize_trade(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hyperliquid trade format -> internal format
        """
        return {
            "exchange": "hyperliquid",
            "symbol": data.get("symbol"),
            "trade_id": str(data.get("trade_id", f"{data.get('symbol')}_{data.get('ts')}")),
            "price": float(data.get("price")),
            "size": float(data.get("size")),
            "side": data.get("side"),
            "timestamp": float(data.get("ts")),
        }

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
