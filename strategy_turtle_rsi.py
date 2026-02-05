"""
strategy_turtle_rsi.py

Concrete Turtle + RSI trading strategy.
"""

from collections import deque
from typing import Deque

from domain_types import MarketType, TradingPair, PositionSide
from strategy_base import StrategyBase, StrategySignal


class TurtleRSIStrategy(StrategyBase):
    """
    Combines Turtle breakout logic with RSI momentum filtering.
    """

    def __init__(
        self,
        market_type: MarketType,
        trading_pair: TradingPair,
        breakout_period: int = 20,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
    ) -> None:
        super().__init__(market_type, trading_pair)

        self.breakout_period = breakout_period
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

        self.prices: Deque[float] = deque(
            maxlen=max(breakout_period, rsi_period) + 1
        )

    def on_price_update(self, price: float) -> StrategySignal:
        self.prices.append(price)

        if len(self.prices) < self.breakout_period:
            return StrategySignal(None, 0.0)

        recent_prices = list(self.prices)
        window = recent_prices[-self.breakout_period:]

        highest = max(window)
        lowest = min(window)

        rsi = self._calculate_rsi(recent_prices)

        if price >= highest and rsi < self.rsi_overbought:
            return StrategySignal(PositionSide.LONG, confidence=rsi / 100.0)

        if price <= lowest and rsi > self.rsi_oversold:
            return StrategySignal(
                PositionSide.SHORT,
                confidence=(100.0 - rsi) / 100.0,
            )

        return StrategySignal(None, 0.0)

    def _calculate_rsi(self, prices: list[float]) -> float:
        if len(prices) <= self.rsi_period:
            return 50.0

        gains = 0.0
        losses = 0.0

        window = prices[-self.rsi_period - 1 :]

        for i in range(1, len(window)):
            delta = window[i] - window[i - 1]
            if delta > 0:
                gains += delta
            else:
                losses -= delta

        if losses == 0:
            return 100.0

        rs = gains / losses
        return 100.0 - (100.0 / (1.0 + rs))
