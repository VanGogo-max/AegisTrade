# strategy_base.py
"""
Strategy Base Interface

Role:
- Unified abstract interface for all trading strategies
- Plug-and-play with CoreEngine
- Strategy contains ONLY signal logic
- No execution, no risk, no position sizing

Flow:
MarketDataAggregator -> Strategy -> FilterStack -> RiskEngine -> CoreEngine -> Execution
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class StrategySignal:
    def __init__(self, market: str, side: str, confidence: float, metadata: Dict[str, Any] = None):
        self.market = market
        self.side = side            # "LONG" or "SHORT"
        self.confidence = confidence
        self.metadata = metadata or {}


class StrategyBase(ABC):
    name: str = "BaseStrategy"
    version: str = "1.0"

    @abstractmethod
    def on_market_data(self, data: Dict[str, Any]) -> StrategySignal | None:
        """
        Called on each market snapshot.
        Returns StrategySignal or None.
        """
        pass

    @abstractmethod
    def warmup(self, historical_data: list[Dict[str, Any]]):
        """
        Optional: preload indicators, ML models, regimes.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Clears internal state (useful for backtests / shadow mode).
        """
        pass
