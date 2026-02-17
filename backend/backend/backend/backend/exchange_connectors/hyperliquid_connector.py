# backend/exchange_connectors/hyperliquid_connector.py

import asyncio
import aiohttp
import websockets
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# =========================
# CONFIG
# =========================

@dataclass
class HyperliquidConfig:
    wallet_address: str
    private_key: str
    rest_url: str = "https://api.hyperliquid.xyz"
    ws_url: str = "wss://api.hyperliquid.xyz/ws"
    timeout: int = 10
    reconnect_delay: int = 5


# =========================
# NORMALIZED MODELS
# =========================

@dataclass
class NormalizedOrderBook:
    exchange: str
    symbol: str
    bids: List[tuple]
    asks: List[tuple]


@dataclass
class NormalizedOrder:
    symbol: str
    side: str
    size: float
    price: Optional[float]
    order_type: str
    reduce_only: bool = False
    post_only: bool = False
    time_in_force: str = "GTC"


@dataclass
class NormalizedPosition:
    symbol: str
    size: float
    entry_price: float
    unrealized_pnl: float


# =========================
# CONNECTOR
# =========================

class HyperliquidConnector:

    def __init__(self, config: HyperliquidConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws = None
        self._connected = False
        self._subscriptions: Dict[str, Any] = {}

    # ----------------------------------
    # CONNECTION
    # ----------------------------------

    async def connect(self):
        self.session = aiohttp.ClientSession()
        await self._connect_ws()

    async def _connect_ws(self):
        while True:
            try:
                self.ws = await websockets.connect(self.config.ws_url)
                self._connected = True
                logger.info("Hyperliquid WS connected")
                asyncio.create_task(self._ws_listener())
                break
            except Exception as e:
                logger.error(f"WS connection failed: {e}")
                await asyncio.sleep(self.config.reconnect_delay)

    async def _ws_listener(self):
        while self._connected:
            try:
                msg = await self.ws.recv()
                data = json.loads(msg)
                await self._handle_ws_message(data)
            except Exception as e:
                logger.error(f"WS error: {e}")
                self._connected = False
                await self._connect_ws()

    # ----------------------------------
    # MARKET DATA
    # ----------------------------------

    async def subscribe_orderbook(self, symbol: str):
        payload = {
            "type": "subscribe",
            "channel": "orderbook",
            "symbol": symbol
        }
        await self.ws.send(json.dumps(payload))

    async def subscribe_trades(self, symbol: str):
        payload = {
            "type": "subscribe",
            "channel": "trades",
            "symbol": symbol
        }
        await self.ws.send(json.dumps(payload))

    async def _handle_ws_message(self, data: Dict):
        if "orderbook" in data:
            ob = self._normalize_orderbook(data)
            # push to orchestrator/event bus here
        if "trades" in data:
            pass

    def _normalize_orderbook(self, raw: Dict) -> NormalizedOrderBook:
        bids = [(float(p), float(s)) for p, s in raw["bids"]]
        asks = [(float(p), float(s)) for p, s in raw["asks"]]

        return NormalizedOrderBook(
            exchange="hyperliquid",
            symbol=raw["symbol"],
            bids=bids,
            asks=asks
        )

    # ----------------------------------
    # EXECUTION
    # ----------------------------------

    async def place_order(self, order: NormalizedOrder):
        signed_payload = self._sign_order(order)

        async with self.session.post(
            f"{self.config.rest_url}/order",
            json=signed_payload
        ) as resp:
            return await resp.json()

    async def cancel_order(self, order_id: str):
        async with self.session.post(
            f"{self.config.rest_url}/cancel",
            json={"order_id": order_id}
        ) as resp:
            return await resp.json()

    # ----------------------------------
    # POSITIONS
    # ----------------------------------

    async def fetch_positions(self) -> List[NormalizedPosition]:
        async with self.session.get(
            f"{self.config.rest_url}/positions",
            params={"address": self.config.wallet_address}
        ) as resp:
            data = await resp.json()

        positions = []
        for p in data:
            positions.append(
                NormalizedPosition(
                    symbol=p["symbol"],
                    size=float(p["size"]),
                    entry_price=float(p["entryPrice"]),
                    unrealized_pnl=float(p["unrealizedPnl"])
                )
            )
        return positions

    # ----------------------------------
    # FUNDING
    # ----------------------------------

    async def fetch_funding_rate(self, symbol: str) -> float:
        async with self.session.get(
            f"{self.config.rest_url}/funding",
            params={"symbol": symbol}
        ) as resp:
            data = await resp.json()

        return float(data["fundingRate"])

    # ----------------------------------
    # SIGNING (placeholder)
    # ----------------------------------

    def _sign_order(self, order: NormalizedOrder) -> Dict:
        # TODO: implement proper HL signature logic
        return {
            "symbol": order.symbol,
            "side": order.side,
            "size": order.size,
            "price": order.price,
            "type": order.order_type,
            "reduceOnly": order.reduce_only,
        }

    # ----------------------------------
    # SHUTDOWN
    # ----------------------------------

    async def close(self):
        self._connected = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
