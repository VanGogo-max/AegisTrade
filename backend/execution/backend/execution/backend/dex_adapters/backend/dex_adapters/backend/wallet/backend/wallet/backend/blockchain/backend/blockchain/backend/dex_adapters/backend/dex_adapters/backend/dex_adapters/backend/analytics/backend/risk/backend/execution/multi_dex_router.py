from typing import Dict, List
import random


class MultiDexRouter:
    """
    Избира най-добрия DEX + поддържа split execution
    """

    def __init__(self, adapters: Dict):
        self.adapters = adapters

    # ---------------- PRICE DISCOVERY ----------------

    async def get_prices(self, symbol: str) -> Dict:
        """
        Събира цени от всички DEX adapters
        """

        prices = {}

        for name, adapter in self.adapters.items():
            try:
                price = await adapter.get_price(symbol)
                prices[name] = price
            except Exception:
                continue

        return prices

    # ---------------- BEST ROUTE ----------------

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

    # ---------------- SMART EXECUTION ----------------

    async def execute(
        self,
        symbol: str,
        side: str,
        size: float,
        split: bool = False
    ) -> Dict:

        prices = await self.get_prices(symbol)

        if not prices:
            raise Exception("No liquidity")

        # 🔹 ако няма split → най-добър DEX
        if not split:
            best_dex = self.select_best_dex(prices, side)
            adapter = self.adapters[best_dex]

            result = await adapter.place_order(
                symbol=symbol,
                side=side,
                size=size
            )

            return {
                "mode": "single",
                "dex": best_dex,
                "price": prices[best_dex],
                "result": result
            }

        # 🔹 SPLIT execution
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
            return await adapter.place_order(symbol, side, size)

        # random split (може да го заменим с liquidity-based)
        parts = len(dexes)
        size_per_dex = size / parts

        results = []

        for dex in dexes:
            adapter = self.adapters[dex]

            try:
                res = await adapter.place_order(
                    symbol=symbol,
                    side=side,
                    size=size_per_dex
                )
                results.append({
                    "dex": dex,
                    "result": res
                })
            except Exception:
                continue

        return {
            "mode": "split",
            "executions": results
        }
