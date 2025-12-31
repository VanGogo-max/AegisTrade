# turtle_rsi_strategy.py
"""
Responsibility:
- Implements Turtle breakout strategy combined with RSI filter
- Generates BUY / SELL / HOLD signals

Does NOT depend on:
- position management
- risk management
- exchange logic
"""

from collections import deque
from typing import Deque, List

from strategy_base import StrategyBase


class TurtleRSIStrategy(StrategyBase):
    NAME = "turtle_rsi"

    def __init__(
        self,
        breakout_period: int = 20,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
    ):
        self.breakout_period = breakout_period
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

        self.prices: Deque[float] = deque(maxlen=max(breakout_period, rsi_period) + 1)

    def on_price(self, price: float) -> str:
        self.prices.append(price)

        if len(self.prices) < self.breakout_period:
            return "HOLD"

        highest = max(list(self.prices)[-self.breakout_period :])
        lowest = min(list(self.prices)[-self.breakout_period :])
        rsi = self._calculate_rsi()

        if price >= highest and rsi < self.rsi_overbought:
            return "BUY"

        if price <= lowest and rsi > self.rsi_oversold:
            return "SELL"

        return "HOLD"

    def _calculate_rsi(self) -> float:
        if len(self.prices) < self.rsi_period + 1:
            return 50.0

        gains: List[float] = []
        losses: List[float] = []

        prices_list = list(self.prices)
        for i in range(-self.rsi_period, 0):
            delta = prices_list[i] - prices_list[i - 1]
            if delta > 0:
                gains.append(delta)
            else:
                losses.append(abs(delta))

        average_gain = sum(gains) / self.rsi_period if gains else 0.0
        average_loss = sum(losses) / self.rsi_period if losses else 0.0

        if average_loss == 0:
            return 100.0

        rs = average_gain / average_loss
        return 100.0 - (100.0 / (1.0 + rs))
