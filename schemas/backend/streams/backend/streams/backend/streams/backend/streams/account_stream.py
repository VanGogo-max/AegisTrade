# streams/account_stream.py

import random
from datetime import datetime
from schemas.messages import (
    Position, PositionsMessage,
    Order, OrdersMessage,
    Balance, BalancesMessage
)


class AccountStream:
    def __init__(self):
        self.positions = [
            Position(
                symbol="BTCUSDT",
                side="long",
                size=0.1,
                entry_price=29500,
                mark_price=30000,
                pnl=50,
                leverage=10
            )
        ]

        self.orders = [
            Order(
                order_id="ord-1",
                symbol="BTCUSDT",
                side="buy",
                price=29900,
                size=0.05,
                status="open"
            )
        ]

        self.balances = [
            Balance(asset="USDT", available=1000.0, locked=50.0),
            Balance(asset="BTC", available=0.2, locked=0.01)
        ]

    def tick_positions(self) -> PositionsMessage:
        # Simulate mark price and PnL changes
        for p in self.positions:
            move = random.uniform(-100, 100)
            p.mark_price = round(p.mark_price + move, 2)
            p.pnl = round((p.mark_price - p.entry_price) * p.size * p.leverage, 2)
        return PositionsMessage(positions=self.positions)

    def tick_orders(self) -> OrdersMessage:
        # Randomly fill an open order
        for o in self.orders:
            if o.status == "open" and random.random() < 0.1:
                o.status = "filled"
        return OrdersMessage(orders=self.orders)

    def tick_balances(self) -> BalancesMessage:
        # Small random balance fluctuation
        for b in self.balances:
            if b.asset == "USDT":
                b.available = round(b.available + random.uniform(-5, 5), 2)
        return BalancesMessage(balances=self.balances)
