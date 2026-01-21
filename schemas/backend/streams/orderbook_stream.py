# streams/orderbook_stream.py

import random
from datetime import datetime
from typing import List
from schemas.messages import OrderbookSnapshot, OrderbookLevel


class OrderbookStream:
    def __init__(self, symbol: str, mid_price: float = 30000.0, levels: int = 10):
        self.symbol = symbol
        self.mid_price = mid_price
        self.levels = levels

    def _generate_side(self, side: str) -> List[OrderbookLevel]:
        levels = []
        for i in range(1, self.levels + 1):
            price_offset = i * random.uniform(0.5, 2.0)
            price = (
                self.mid_price - price_offset if side == "bid"
                else self.mid_price + price_offset
            )
            size = round(random.uniform(0.01, 2.0), 4)
            levels.append(OrderbookLevel(price=round(price, 2), size=size))
        return levels

    def snapshot(self) -> OrderbookSnapshot:
        # Simulate small mid price movement
        self.mid_price += random.uniform(-5, 5)

        bids = self._generate_side("bid")
        asks = self._generate_side("ask")

        return OrderbookSnapshot(
            symbol=self.symbol,
            bids=bids,
            asks=asks,
            timestamp=datetime.utcnow()
        )
