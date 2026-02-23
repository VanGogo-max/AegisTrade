"""
Binance WebSocket Connector

Responsibilities:
- Subscribe to multiple symbols for trades, orderbook, and kline/ohlcv
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


class BinanceWS:

    BASE_URL = "wss://stream.binance.com:9443/ws"

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
        streams = "/".join([f"{s.lower()}@trade" for s in self.symbols])
        url = f"{self.BASE_URL}/{streams}"

        async with websockets.connect(url) as ws:
            self._ws = ws
            print("Connected to Binance WS")
            await self._listen()

    async def _listen(self):
        async for msg in self._ws:
            try:
                data = json.loads(msg)
                # Normalize data
                symbol = data.get("s")
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
        Binance trade format -> internal format
        """
        return {
            "exchange": "binance",
            "symbol": data.get("s"),
            "trade_id": str(data.get("t")),
            "price": float(data.get("p")),
            "size": float(data.get("q")),
            "side": "buy" if data.get("m") is False else "sell",
            "timestamp": data.get("T") / 1000.0,
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
