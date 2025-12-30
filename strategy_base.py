"""
strategy_base.py

Abstract base class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Optional

from types import MarketType, TradingPair, PositionSide


class StrategySignal:
    """
    Represents a strategy decision.
    side = None   -> no action
    side = LONG   -> open long
    side = SHORT  -> open short
    """

    def __init__(
        self,
        side: Optional[PositionSide],
        confidence: float,
    ) -> None:
        self.side = side
        self.confidence = confidence


class StrategyBase(ABC):
    """
    Base interface for all trading strategies.
    """

    def __init__(self, market_type: MarketType, trading_pair: TradingPair) -> None:
        self.market_type = market_type
        self.trading_pair = trading_pair

    @abstractmethod
    def on_price_update(self, price: float) -> StrategySignal:
        """
        Called whenever new price data is available.
        Must return a StrategySignal.
        """
        raise NotImplementedError
