"""
AegisTrade — Price Feed
"""
from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import aiohttp

from backend.config.config import (
    HYPERLIQUID_API, DYDX_API, PRICE_FEED_TIMEOUT_S, TIMEFRAME
)
from backend.utils.logger import get_logger
from backend.utils.i18n import t

log = get_logger(__name__)


@dataclass
class Candle:
    ts: float
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Ticker:
    symbol: str
    price: float
    bid: float
    ask: float
    ts: float = 0.0


COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum",
    "SOL": "solana", "ARB": "arbitrum",
}


def _hl_symbol(symbol: str) -> str:
    return symbol.split("-")[0]

def _dydx_symbol(symbol: str) -> str:
    return f"{symbol.split('-')[0]}-USD"


class PriceFeed:
    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Ticker] = {}

    async def start(self) -> None:
        timeout = aiohttp.ClientTimeout(total=PRICE_FEED_TIMEOUT_S)
        self._session = aiohttp.ClientSession(timeout=timeout)
        log.info("PriceFeed session opened")

    async def stop(self) -> None:
        if self._session:
            await self._session.close()
        log.info("PriceFeed session closed")

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        ticker = await self._hl_ticker(symbol)
        if ticker:
            self._cache[symbol] = ticker
            return ticker
        log.warning(t("price_feed_fallback"))
        ticker = await self._dydx_ticker(symbol)
        if ticker:
            self._cache[symbol] = ticker
            return ticker
        ticker = await self._coingecko_ticker(symbol)
        if ticker:
            self._cache[symbol] = ticker
            return ticker
        log.error(t("price_feed_error", symbol=symbol))
        return self._cache.get(symbol)

    async def get_candles(
        self, symbol: str, limit: int = 50
    ) -> List[Candle]:
        candles = await self._hl_candles(symbol, limit)
        if candles:
            return candles
        candles = await self._dydx_candles(symbol, limit)
        return candles or []

    async def _hl_ticker(self, symbol: str) -> Optional[Ticker]:
        try:
            async with self._session.post(
                f"{HYPERLIQUID_API}/info",
                json={"type": "allMids"},
            ) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                coin = _hl_symbol(symbol)
                price_str = data.get(coin)
                if not price_str:
                    return None
                price = float(price_str)
                return Ticker(
                    symbol=symbol, price=price,
                    bid=price * 0.9999, ask=price * 1.0001,
                    ts=time.time()
                )
        except Exception as e:
            log.debug("HL ticker error: %s", e)
            return None

    async def _hl_candles(self, symbol: str, limit: int) -> List[Candle]:
        try:
            coin = _hl_symbol(symbol)
            interval_map = {"15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
            interval = interval_map.get(TIMEFRAME, "15m")
            end_ms = int(time.time() * 1000)
            start_ms = end_ms - limit * 15 * 60 * 1000
            async with self._session.post(
                f"{HYPERLIQUID_API}/info",
                json={
                    "type": "candleSnapshot",
                    "req": {
                        "coin": coin,
                        "interval": interval,
                        "startTime": start_ms,
                        "endTime": end_ms
                    },
                },
            ) as r:
                if r.status != 200:
                    return []
                raw = await r.json()
                return [
                    Candle(
                        ts=c["t"] / 1000,
                        open=float(c["o"]),
                        high=float(c["h"]),
                        low=float(c["l"]),
                        close=float(c["c"]),
                        volume=float(c["v"]),
                    )
                    for c in raw
                ]
        except Exception as e:
            log.debug("HL candles error: %s", e)
            return []

    async def _dydx_ticker(self, symbol: str) -> Optional[Ticker]:
        try:
            mkt = _dydx_symbol(symbol)
            async with self._session.get(
                f"{DYDX_API}/perpetualMarkets?ticker={mkt}"
            ) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                mkt_data = data.get("markets", {}).get(mkt, {})
                price = float(mkt_data.get("oraclePrice", 0))
                if price == 0:
                    return None
                return Ticker(
                    symbol=symbol, price=price,
                    bid=price * 0.9999, ask=price * 1.0001,
                    ts=time.time()
                )
        except Exception as e:
            log.debug("dYdX ticker error: %s", e)
            return None

    async def _dydx_candles(self, symbol: str, limit: int) -> List[Candle]:
        try:
            mkt = _dydx_symbol(symbol)
            res_map = {"15m": "15MINS", "1h": "1HOUR", "1d": "1DAY"}
            resolution = res_map.get(TIMEFRAME, "15MINS")
            async with self._session.get(
                f"{DYDX_API}/candles/perpetualMarkets/{mkt}"
                f"?resolution={resolution}&limit={limit}"
            ) as r:
                if r.status != 200:
                    return []
                raw = (await r.json()).get("candles", [])
                return [
                    Candle(
                        ts=time.time(),
                        open=float(c["open"]),
                        high=float(c["high"]),
                        low=float(c["low"]),
                        close=float(c["close"]),
                        volume=float(c["usdVolume"]),
                    )
                    for c in raw
                ]
        except Exception as e:
            log.debug("dYdX candles error: %s", e)
            return []

    async def _coingecko_ticker(self, symbol: str) -> Optional[Ticker]:
        coin_id = COINGECKO_IDS.get(_hl_symbol(symbol))
        if not coin_id:
            return None
        try:
            url = (
                "https://api.coingecko.com/api/v3/simple/price"
                f"?ids={coin_id}&vs_currencies=usd"
            )
            async with self._session.get(url) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                price = float(data[coin_id]["usd"])
                return Ticker(
                    symbol=symbol, price=price,
                    bid=price * 0.9999, ask=price * 1.0001,
                    ts=time.time()
                )
        except Exception as e:
            log.debug("CoinGecko error: %s", e)
            return None
