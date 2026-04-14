"""
AegisTrade - Price Feed
"""
from __future__ import annotations
import aiohttp
from dataclasses import dataclass
from typing import Optional
from backend.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class Ticker:
    symbol: str
    price: float
    volume: float = 0.0


class PriceFeed:
    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

    async def stop(self) -> None:
        if self._session:
            await self._session.close()

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        try:
            clean = symbol.replace("-PERP", "").replace("-", "")
            url = f"https://api.hyperliquid.xyz/info"
            async with self._session.post(url, json={"type": "allMids"}) as r:
                if r.status == 200:
                    data = await r.json()
                    price = float(data.get(clean, 0))
                    if price > 0:
                        return Ticker(symbol=symbol, price=price)
        except Exception as e:
            log.warning("Price feed error: %s", e)
        return Ticker(symbol=symbol, price=0.0)

    async def get_candles(self, symbol: str, limit: int = 60) -> list:
        try:
            clean = symbol.replace("-PERP", "").replace("-", "")
            url = "https://api.hyperliquid.xyz/info"
            payload = {
                "type": "candleSnapshot",
                "req": {"coin": clean, "interval": "1h", "startTime": 0, "endTime": 9999999999999}
            }
            async with self._session.post(url, json=payload) as r:
                if r.status == 200:
                    data = await r.json()
                    return data[-limit:] if isinstance(data, list) else []
        except Exception as e:
            log.warning("Candles error: %s", e)
        return []
