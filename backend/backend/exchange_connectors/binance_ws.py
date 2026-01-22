import asyncio
import json
import time
import websockets
from typing import List, Dict, Any, Callable

from backend.exchange_connectors.base import BaseExchangeConnector


class BinanceWSConnector(BaseExchangeConnector):
    BASE_WS = "wss://stream.binance.com:9443/stream"

    def __init__(
        self,
        symbols: List[str],
        intervals: List[str],
        on_message: Callable[[Dict[str, Any]], None]
    ):
        super().__init__("binance", symbols, on_message)
        self.intervals = intervals
        self._ws = None

    def _build_streams(self):
        streams = []
        for s in self.symbols:
            s = s.lower()
            streams.append(f"{s}@trade")
            streams.append(f"{s}@depth@100ms")
            for i in self.intervals:
                streams.append(f"{s}@kline_{i}")
        return streams

    def _build_url(self):
        streams = "/".join(self._build_streams())
        return f"{self.BASE_WS}?streams={streams}"

    async def connect(self):
        url = self._build_url()
        print(f"[Binance] Connecting to {url}")

        async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
            self._ws = ws
            async for msg in ws:
                await self._handle_message(json.loads(msg))

    async def disconnect(self):
        if self._ws:
            await self._ws.close()

    async def _handle_message(self, raw: Dict[str, Any]):
        stream = raw.get("stream", "")
        data = raw.get("data", {})
        event_type = data.get("e")

        if event_type == "trade":
            await self._emit_trade(data)

        elif event_type == "depthUpdate":
            await self._emit_orderbook(data)

        elif event_type == "kline":
            await self._emit_kline(data)

    async def _emit_trade(self, d: Dict[str, Any]):
        event = {
            "type": "trade",
            "symbol": d["s"],
            "timestamp": d["T"],
            "data": {
                "price": float(d["p"]),
                "qty": float(d["q"]),
                "side": "buy" if d["m"] is False else "sell",
                "trade_id": d["t"]
            }
        }
        await self._safe_emit(event)

    async def _emit_orderbook(self, d: Dict[str, Any]):
        event = {
            "type": "orderbook",
            "symbol": d["s"],
            "timestamp": d["E"],
            "data": {
                "bids": [(float(p), float(q)) for p, q in d["b"]],
                "asks": [(float(p), float(q)) for p, q in d["a"]],
                "first_update_id": d["U"],
                "last_update_id": d["u"]
            }
        }
        await self._safe_emit(event)

    async def _emit_kline(self, d: Dict[str, Any]):
        k = d["k"]
        event = {
            "type": "ohlcv",
            "symbol": k["s"],
            "timestamp": k["t"],
            "data": {
                "interval": k["i"],
                "open": float(k["o"]),
                "high": float(k["h"]),
                "low": float(k["l"]),
                "close": float(k["c"]),
                "volume": float(k["v"]),
                "is_closed": k["x"]
            }
        }
        await self._safe_emit(event)

    async def start(self):
        await self.run_forever()
