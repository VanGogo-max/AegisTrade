import asyncio
import json
import websockets
from typing import List, Dict, Any, Callable

from backend.exchange_connectors.base import BaseExchangeConnector


class HyperliquidWSConnector(BaseExchangeConnector):
    WS_URL = "wss://api.hyperliquid.xyz/ws"

    def __init__(
        self,
        symbols: List[str],
        on_message: Callable[[Dict[str, Any]], None]
    ):
        super().__init__("hyperliquid", symbols, on_message)
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
            sub_msg = {
                "method": "subscribe",
                "subscription": {
                    "type": "l2Book",
                    "coin": symbol
                }
            }
            await self._ws.send(json.dumps(sub_msg))

            trade_sub = {
                "method": "subscribe",
                "subscription": {
                    "type": "trades",
                    "coin": symbol
                }
            }
            await self._ws.send(json.dumps(trade_sub))

    async def _handle_message(self, msg: Dict[str, Any]):
        if "channel" not in msg:
            return

        channel = msg["channel"]
        data = msg.get("data", {})

        if channel == "l2Book":
            await self._emit_orderbook(data)

        elif channel == "trades":
            for trade in data:
                await self._emit_trade(trade)

    async def _emit_orderbook(self, d: Dict[str, Any]):
        event = {
            "type": "orderbook",
            "symbol": d["coin"],
            "timestamp": d["time"],
            "data": {
                "bids": [(float(p), float(q)) for p, q in d["levels"][0]],
                "asks": [(float(p), float(q)) for p, q in d["levels"][1]]
            }
        }
        await self._safe_emit(event)

    async def _emit_trade(self, t: Dict[str, Any]):
        event = {
            "type": "trade",
            "symbol": t["coin"],
            "timestamp": t["time"],
            "data": {
                "price": float(t["px"]),
                "qty": float(t["sz"]),
                "side": t["side"],
                "trade_id": t["tid"]
            }
        }
        await self._safe_emit(event)

    async def start(self):
        await self.run_forever()
