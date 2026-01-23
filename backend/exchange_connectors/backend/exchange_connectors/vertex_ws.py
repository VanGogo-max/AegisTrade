# backend/exchange_connectors/vertex_ws.py

import asyncio
import json
import logging
import websockets
from typing import Dict, Any
from backend.core.unified_router import UnifiedMarketDataRouter

log = logging.getLogger("VertexWS")


class VertexWSConnector:
    """
    Real-time market data connector for Vertex Protocol (Arbitrum).
    Uses official Vertex WebSocket API for orderbook & ticker streams.
    """

    VERTEX_WS_URL = "wss://gateway.prod.vertexprotocol.com/v1/ws"

    def __init__(self, router: UnifiedMarketDataRouter, symbols=None):
        self.router = router
        self.symbols = symbols or ["BTC-PERP", "ETH-PERP"]
        self.ws = None
        self.running = False

    async def connect(self):
        log.info("Connecting to Vertex WebSocket...")
        self.ws = await websockets.connect(self.VERTEX_WS_URL)
        self.running = True

        subscribe_msg = {
            "type": "subscribe",
            "channels": [
                {
                    "name": "ticker",
                    "symbols": self.symbols
                }
            ]
        }

        await self.ws.send(json.dumps(subscribe_msg))
        log.info(f"Subscribed to Vertex tickers: {self.symbols}")

        asyncio.create_task(self._listen())

    async def _listen(self):
        while self.running:
            try:
                msg = await self.ws.recv()
                data = json.loads(msg)

                if data.get("type") != "ticker":
                    continue

                parsed = self._parse_ticker(data)
                if parsed:
                    await self.router.publish(parsed)

            except Exception as e:
                log.error(f"Vertex WS error: {e}")
                await asyncio.sleep(5)
                await self.reconnect()

    def _parse_ticker(self, data: Dict[str, Any]):
        try:
            symbol = data["symbol"]
            price = float(data["last_price"])
            ts = int(data["timestamp"])

            return {
                "exchange": "vertex",
                "symbol": symbol,
                "price": price,
                "timestamp": ts,
                "type": "ticker"
            }
        except Exception as e:
            log.warning(f"Vertex parse error: {e}")
            return None

    async def reconnect(self):
        log.info("Reconnecting Vertex WS...")
        try:
            await self.ws.close()
        except:
            pass
        await asyncio.sleep(3)
        await self.connect()

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()
