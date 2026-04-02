import time
import aiohttp


class PriceFeed:
    """
    Price feed с caching и fallback
    - Кешира цената за 2 секунди
    - Fallback: Hyperliquid → dYdX
    - Защита от празни данни
    """

    CACHE_TTL = 2.0  # секунди

    def __init__(self):
        self.session = None
        self._cache: dict = {}

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    # ---------------- CACHE ----------------

    def _get_cached(self, symbol: str):
        entry = self._cache.get(symbol)
        if entry and (time.time() - entry["ts"]) < self.CACHE_TTL:
            return entry["price"]
        return None

    def _set_cache(self, symbol: str, price: float):
        self._cache[symbol] = {"price": price, "ts": time.time()}

    # ---------------- HYPERLIQUID ----------------

    async def _hyperliquid(self, symbol: str):
        try:
            session = await self._get_session()
            async with session.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "allMids"},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                data = await resp.json()
                price = data.get(symbol)
                if price:
                    return float(price)
        except Exception:
            pass
        return None

    # ---------------- DYDX ----------------

    async def _dydx(self, symbol: str):
        try:
            session = await self._get_session()
            async with session.get(
                f"https://api.dydx.exchange/v3/markets/{symbol}-USD",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                data = await resp.json()
                market = data.get("market", {})
                price = market.get("oraclePrice")
                if price:
                    return float(price)
        except Exception:
            pass
        return None

    # ---------------- MAIN ----------------

    async def get_price(self, symbol: str) -> float | None:
        # 1. Провери кеша
        cached = self._get_cached(symbol)
        if cached:
            return cached

        # 2. Hyperliquid
        price = await self._hyperliquid(symbol)

        # 3. Fallback към dYdX
        if not price:
            price = await self._dydx(symbol)

        # 4. Запази в кеша
        if price and price > 0:
            self._set_cache(symbol, price)
            return price

        return None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
