from typing import Dict, List, Tuple
from backend.exchange_connectors.exchange_registry import ExchangeRegistry


class LiquidityAnalyzer:

    def __init__(self, registry: ExchangeRegistry):
        self.registry = registry

    # ------------------------------------------------
    # PUBLIC
    # ------------------------------------------------

    async def analyze(
        self,
        symbol: str,
        side: str,
        total_size: float,
    ) -> Dict[str, Dict]:

        """
        Returns per-exchange liquidity metrics:
        {
            "hyperliquid": {
                "max_fill_size": float,
                "avg_price": float,
                "slippage": float,
            }
        }
        """

        analysis = {}

        for name in self.registry.list():

            connector = self.registry.get(name)

            try:
                orderbook = await connector.get_orderbook(symbol)
                result = self._calculate_fill(
                    orderbook=orderbook,
                    side=side,
                    target_size=total_size,
                )

                if result["max_fill_size"] > 0:
                    analysis[name] = result

            except Exception:
                continue

        return analysis

    # ------------------------------------------------
    # CORE LOGIC
    # ------------------------------------------------

    def _calculate_fill(
        self,
        orderbook: Dict,
        side: str,
        target_size: float,
    ) -> Dict:

        """
        Orderbook format expected:
        {
            "bids": [(price, size), ...],
            "asks": [(price, size), ...]
        }
        """

        levels = orderbook["asks"] if side == "buy" else orderbook["bids"]

        remaining = target_size
        total_cost = 0.0
        filled = 0.0

        for price, size in levels:

            if remaining <= 0:
                break

            take = min(size, remaining)

            total_cost += take * price
            filled += take
            remaining -= take

        if filled == 0:
            return {
                "max_fill_size": 0,
                "avg_price": 0,
                "slippage": 0,
            }

        avg_price = total_cost / filled
        best_price = levels[0][0]

        slippage = abs((avg_price - best_price) / best_price)

        return {
            "max_fill_size": filled,
            "avg_price": avg_price,
            "slippage": slippage,
        }

    # ------------------------------------------------
    # SPLIT CALCULATION
    # ------------------------------------------------

    def compute_optimal_split(
        self,
        liquidity_map: Dict[str, Dict],
        total_size: float,
    ) -> Dict[str, float]:

        """
        Returns size allocation per exchange
        Based on inverse slippage weighting
        """

        weights = {}
        total_inverse_slippage = 0.0

        for name, data in liquidity_map.items():

            if data["slippage"] == 0:
                weight = 1.0
            else:
                weight = 1 / data["slippage"]

            weights[name] = weight
            total_inverse_slippage += weight

        allocations = {}

        for name, weight in weights.items():

            ratio = weight / total_inverse_slippage
            allocations[name] = ratio * total_size

        return allocations
