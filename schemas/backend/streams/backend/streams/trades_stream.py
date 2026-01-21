# streams/trades_stream.py

import random
import uuid
from datetime import datetime
from schemas.messages import Trade, TradesMessage


class TradesStream:
    def __init__(self, symbol: str, last_price: float = 30000.0):
        self.symbol = symbol
        self.last_price = last_price

    def tick(self) -> TradesMessage:
        # Simulate small price movement
        price_change = random.uniform(-10, 10)
        self.last_price = max(1, self.last_price + price_change)

        trade = Trade(
            trade_id=str(uuid.uuid4()),
            symbol=self.symbol,
            side="buy" if price_change >= 0 else "sell",
            price=round(self.last_price, 2),
            size=round(random.uniform(0.001, 1.0), 4),
            timestamp=datetime.utcnow()
        )

        return TradesMessage(trades=[trade])
