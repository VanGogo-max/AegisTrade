# backend/exchange_connectors/kwenta_ws.py

import asyncio
import json
import logging
import websockets
from typing import Dict, Any
from backend.core.unified_router import UnifiedMarketDataRouter

log = logging.getLogger("KwentaWS")


class KwentaWSConnector:
    """
    Real-time market data connector for Kwenta (Optimism Perps V2)
    Uses Pyth price feeds via public websocket (since Kwenta itself has no native WS).
    """

    PYTH_WS = "wss://hermes.pyth.network/ws"

    def __init__(self, router: UnifiedMarketDataRouter, symbols=None):
        self.router = router
        self.symbols = symbols or ["BTCUSD", "ETHUSD"]
        self.ws = None
        self.running = False

    async def connect(self):
        log.info("Connecting to Kwenta (via Pyth Network)...")
        self.ws = await websockets.connect(self.PYTH_WS)
        self.running = True

        subscribe_msg = {
            "type": "subscribe",
            "ids": self._pyth_price_ids()
        }

        await self.ws.send(json.dumps(subscribe_msg))
        log.info(f"Subscribed to Kwenta price feeds: {self.symbols}")

        asyncio.create_task(self._listen())

    def _pyth_price_ids(self):
        # Mapping for real mainnet feeds (can be expanded later)
        mapping = {
            "BTCUSD": "0xe62df6c8b4e8d6f0f8b71bbd0c98b1c1a3e6b6c8b6fa7b1c7e9f7b3b1b5a8d2e",
            "ETHUSD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"
        }
        return [mapping[s] for s in self.symbols if s in mapping]

    async def _listen(self):
        while self.running:
            try:
                msg = await self.ws.recv()
                data = json.loads(msg)

                if data.get("type") != "price_update":
                    continue

                price_data = self._parse_price(data)
                if price_data:
                    await self.router.publish(price_data)

            except Exception as e:
                log.error(f"Kwenta WS error: {e}")
                await asyncio.sleep(5)
                await self.reconnect()

    def _parse_price(self, data: Dict[str, Any]):
        try:
            price = float(data["price"]["price"]) / 1e8
            symbol = data["price"]["symbol"]

            return {
                "exchange": "kwenta",
                "symbol": symbol,
                "price": price,
                "timestamp": data["price"]["publish_time"],
                "type": "ticker"
            }
        except Exception as e:
            log.warning(f"Kwenta parse error: {e}")
            return None

    async def reconnect(self):
        log.info("Reconnecting Kwenta WS...")
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
