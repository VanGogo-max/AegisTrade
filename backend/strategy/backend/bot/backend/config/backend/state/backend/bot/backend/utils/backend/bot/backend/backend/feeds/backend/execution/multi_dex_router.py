from typing import Dict

from backend.feeds.price_feed import PriceFeed


class MultiDexRouter:
    """
    Multi-DEX Router с реални цени (price feed)
    """

    def __init__(self, adapters: Dict):
        self.adapters = adapters
        self.price_feed = PriceFeed()

    # ---------------- PRICE DISCOVERY ----------------

    async def get_prices(self, symbol: str) -> Dict:
        """
        Взима реална цена и я разпределя към всички DEX
        """

        prices = {}

        real_price = await self.price_feed.get_price(symbol)

        if not real_price:
            return prices

        # временно: една цена за всички DEX
        for dex in self.adapters.keys():
            prices[dex] = real_price

        return prices

    # ---------------- BEST DEX ----------------

    def select_best_dex(self, prices: Dict, side: str) -> str:
        """
        BUY → най-ниска цена
        SELL → най-висока цена
        """

        if not prices:
            raise Exception("No prices available")

        if side == "buy":
            return min(prices, key=prices.get)

        return max(prices, key=prices.get)

    # ---------------- EXECUTION ----------------

    async def execute(
        self,
        symbol: str,
        side: str,
        size: float,
        split: bool = False
    ) -> Dict:

        prices = await self.get_prices(symbol)

        if not prices:
            raise Exception("No liquidity / price data")

        # 🔹 SINGLE EXECUTION
        if not split:
            best_dex = self.select_best_dex(prices, side)
            adapter = self.adapters[best_dex]

            result = await adapter.place_order(
                symbol=symbol,
                side=side,
                size=size,
                price=prices[best_dex],
                order_type="market"
            )

            return {
                "mode": "single",
                "dex": best_dex,
                "price": prices[best_dex],
                "result": result
            }

        # 🔹 SPLIT EXECUTION
        return await self._split_execution(prices, symbol, side, size)

    # ---------------- SPLIT ----------------

    async def _split_execution(
        self,
        prices: Dict,
        symbol: str,
        side: str,
        size: float
    ) -> Dict:

        dexes = list(prices.keys())

        if len(dexes) == 1:
            adapter = self.adapters[dexes[0]]
            return await adapter.place_order(
                symbol=symbol,
                side=side,
                size=size,
                price=prices[dexes[0]],
                order_type="market"
            )

        size_per_dex = size / len(dexes)

        results = []

        for dex in dexes:
            adapter = self.adapters[dex]

            try:
                res = await adapter.place_order(
                    symbol=symbol,
                    side=side,
                    size=size_per_dex,
                    price=prices[dex],
                    order_type="market"
                )

                results.append({
                    "dex": dex,
                    "price": prices[dex],
                    "result": res
                })

            except Exception as e:
                results.append({
                    "dex": dex,
                    "error": str(e)
                })

        return {
            "mode": "split",
            "executions": results
        }

    # ---------------- CLEANUP ----------------

    async def close(self):
        """
        Затваря HTTP сесии (важно за aiohttp)
        """
        await self.price_feed.close()
