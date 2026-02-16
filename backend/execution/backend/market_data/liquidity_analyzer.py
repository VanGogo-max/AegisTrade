from typing import Dict, List, Tuple


class LiquidityAnalyzer:
    """
    Calculates liquidity metrics for DEX routing decisions.
    """

    def __init__(self):
        pass

    @staticmethod
    def calculate_spread(best_bid: float, best_ask: float) -> float:
        if best_bid <= 0 or best_ask <= 0:
            return float("inf")

        return (best_ask - best_bid) / best_ask

    @staticmethod
    def calculate_weighted_price(
        orderbook_side: List[Tuple[float, float]],
        order_size: float,
    ) -> float:
        """
        orderbook_side = [(price, size), ...]
        """

        remaining = order_size
        total_cost = 0.0
        total_size = 0.0

        for price, size in orderbook_side:
            if remaining <= 0:
                break

            executed = min(size, remaining)
            total_cost += executed * price
            total_size += executed
            remaining -= executed

        if total_size == 0:
            return 0.0

        return total_cost / total_size

    def calculate_slippage(
        self,
        best_price: float,
        weighted_price: float,
    ) -> float:

        if best_price == 0:
            return float("inf")

        return abs(weighted_price - best_price) / best_price

    def analyze(
        self,
        orderbook: Dict,
        side: str,
        order_size: float,
    ) -> Dict:

        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])

        if not bids or not asks:
            return {"valid": False}

        best_bid = bids[0][0]
        best_ask = asks[0][0]

        spread = self.calculate_spread(best_bid, best_ask)

        if side.lower() == "buy":
            weighted_price = self.calculate_weighted_price(asks, order_size)
            slippage = self.calculate_slippage(best_ask, weighted_price)
        else:
            weighted_price = self.calculate_weighted_price(bids, order_size)
            slippage = self.calculate_slippage(best_bid, weighted_price)

        liquidity_score = 1 / (spread + slippage + 1e-8)

        return {
            "valid": True,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "weighted_price": weighted_price,
            "slippage": slippage,
            "liquidity_score": liquidity_score,
        }
