import asyncio
import json
import websockets
from typing import List, Dict, Any, Callable

from backend.exchange_connectors.base import BaseExchangeConnector


class DydxWSConnector(BaseExchangeConnector):
    WS_URL = "wss://indexer.dydx.trade/v4/ws"

    def __init__(
        self,
        symbols: List[str],
        on_message: Callable[[Dict[str, Any]], None]
    ):
        super().__init__("dydx", symbols, on_message)
        self._ws = None

    async def connect(self):
        async with websockets.connect(self.WS_URL, ping_interval=20, ping_timeout=20) as ws:
            self._ws = ws
            await self._subscribe()
            async for msg in ws:
                await self._handle_message(json.loads(msg))

    async def disconnect(self):
        if self._ws:
            await self._ws.close()

    async def _subscribe(self):
        for symbol in self.symbols:
            orderbook_sub = {
                "type": "subscribe",
                "channel": "v4_orderbook",
                "id": symbol
            }
            trades_sub = {
                "type": "subscribe",
                "channel": "v4_trades",
                "id": symbol
            }
            await self._ws.send(json.dumps(orderbook_sub))
            await self._ws.send(json.dumps(trades_sub))

    async def _handle_message(self, msg: Dict[str, Any]):
        channel = msg.get("channel")
        data = msg.get("contents")

        if channel == "v4_orderbook":
            await self._emit_orderbook(msg["id"], data)

        elif channel == "v4_trades":
            for trade in data:
                await self._emit_trade(msg["id"], trade)

    async def _emit_orderbook(self, symbol: str, d: Dict[str, Any]):
        event = {
            "type": "orderbook",
            "symbol": symbol,
            "timestamp": d["time"],
            "data": {
                "bids": [(float(p), float(q)) for p, q in d["bids"]],
                "asks": [(float(p), float(q)) for p, q in d["asks"]]
            }
        }
        await self._safe_emit(event)

    async def _emit_trade(self, symbol: str, t: Dict[str, Any]):
        event = {
            "type": "trade",
            "symbol": symbol,
            "timestamp": t["createdAt"],
            "data": {
                "price": float(t["price"]),
                "qty": float(t["size"]),
                "side": t["side"],
                "trade_id": t["id"]
            }
        }
        await self._safe_emit(event)

    async def start(self):
        await self.run_forever()
