# backend/exchange_connectors/binance_ws.py

import asyncio
import json
import websockets
from typing import List

from backend.market_data.normalizer import (
    normalize_binance_trade,
    normalize_binance_ohlcv,
)
from backend.market_data.market_router import MarketRouter


BINANCE_WS_BASE = "wss://stream.binance.com:9443/stream?streams="


class BinanceWebSocketClient:

    def __init__(
        self,
        symbols: List[str],
        router: MarketRouter,
        reconnect_delay: int = 5,
    ) -> None:

        self.symbols = [s.lower() for s in symbols]
        self.router = router
        self.reconnect_delay = reconnect_delay
        self._running = False

    # ==========================================================
    # PUBLIC
    # ==========================================================

    async def start(self) -> None:
        self._running = True
        asyncio.create_task(self._connect_loop())

    async def stop(self) -> None:
        self._running = False

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _build_stream_url(self) -> str:
        streams = []

        for symbol in self.symbols:
            streams.append(f"{symbol}@trade")
            streams.append(f"{symbol}@kline_1m")

        return BINANCE_WS_BASE + "/".join(streams)

    async def _connect_loop(self) -> None:
        while self._running:
            try:
                url = self._build_stream_url()

                async with websockets.connect(url, ping_interval=20) as ws:
                    await self._listen(ws)

            except Exception:
                await asyncio.sleep(self.reconnect_delay)

    async def _listen(self, ws) -> None:
        async for message in ws:
            data = json.loads(message)

            if "data" not in data:
                continue

            payload = data["data"]
            event_type = payload.get("e")

            if event_type == "trade":
                normalized = normalize_binance_trade(payload)
                await self.router.publish(normalized)

            elif event_type == "kline":
                normalized = normalize_binance_ohlcv(payload)
                await self.router.publish(normalized)
      
