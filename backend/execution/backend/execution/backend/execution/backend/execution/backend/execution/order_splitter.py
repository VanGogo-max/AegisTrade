from typing import Dict, List
from dataclasses import dataclass


# Ако вече имаш NormalizedOrder – използвай него.
# Тук давам безопасен fallback модел.

@dataclass
class NormalizedOrder:
    symbol: str
    side: str
    size: float
    order_type: str = "market"
    price: float = None
    leverage: float = 1.0


class OrderSplitter:

    def __init__(
        self,
        min_order_size: float = 0.001,
        rounding_precision: int = 6,
    ):
        self.min_order_size = min_order_size
        self.rounding_precision = rounding_precision

    # ------------------------------------------------
    # PUBLIC
    # ------------------------------------------------

    def split(
        self,
        parent_order: NormalizedOrder,
        allocations: Dict[str, float],
    ) -> List[Dict]:
        """
        Returns:
        [
            {
                "exchange": "hyperliquid",
                "order": NormalizedOrder(...)
            }
        ]
        """

        child_orders = []
        total_allocated = 0.0

        for exchange, size in allocations.items():

            size = round(size, self.rounding_precision)

            if size < self.min_order_size:
                continue

            child_order = NormalizedOrder(
                symbol=parent_order.symbol,
                side=parent_order.side,
                size=size,
                order_type=parent_order.order_type,
                price=parent_order.price,
                leverage=parent_order.leverage,
            )

            child_orders.append({
                "exchange": exchange,
                "order": child_order,
            })

            total_allocated += size

        # Ако rounding е оставил остатък → добавяме към най-голямата поръчка
        remainder = round(parent_order.size - total_allocated, self.rounding_precision)

        if remainder > self.min_order_size and child_orders:
            largest = max(child_orders, key=lambda x: x["order"].size)
            largest["order"].size += remainder

        return child_orders

    # ------------------------------------------------
    # VALIDATION
    # ------------------------------------------------

    def validate_split(
        self,
        parent_order: NormalizedOrder,
        child_orders: List[Dict],
    ) -> bool:

        total = sum(c["order"].size for c in child_orders)

        return round(total, self.rounding_precision) == round(
            parent_order.size,
            self.rounding_precision,
        )
