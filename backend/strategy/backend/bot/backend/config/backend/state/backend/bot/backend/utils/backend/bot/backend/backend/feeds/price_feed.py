import aiohttp


class PriceFeed:
    """
    Реален price feed (API базиран)
    Поддържа няколко DEX / източника
    """

    def __init__(self):
        self.session = None

    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    # ---------------- HYPERLIQUID ----------------

    async def get_hyperliquid_price(self, symbol: str):
        """
        Hyperliquid public API
        """
        url = "https://api.hyperliquid.xyz/info"

        payload = {
            "type": "allMids"
        }

        session = await self._get_session()

        async with session.post(url, json=payload) as resp:
            data = await resp.json()

            if symbol in data:
                return float(data[symbol])

        return None

    # ---------------- DYDX ----------------

    async def get_dydx_price(self, symbol: str):
        """
        dYdX public API
        """
        url = f"https://api.dydx.exchange/v3/markets/{symbol}-USD"

        session = await self._get_session()

        async with session.get(url) as resp:
            data = await resp.json()

            market = data.get("market")

            if market:
                return float(market["oraclePrice"])

        return None

    # ---------------- FALLBACK ----------------

    async def get_price(self, symbol: str):
        """
        Взима цена от няколко източника
        """

        # пробваме Hyperliquid
        price = await self.get_hyperliquid_price(symbol)
        if price:
            return price

        # fallback към dYdX
        price = await self.get_dydx_price(symbol)
        if price:
            return price

        return None

    # ---------------- CLOSE SESSION ----------------

    async def close(self):
        if self.session:
            await self.session.close()
