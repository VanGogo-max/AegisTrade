"""
strategy_selector.py

Selects a single actionable signal from multiple strategies.
Returns None if no clear decision is available.
"""

from typing import List, Optional

from strategy_base import StrategyBase, StrategySignal


class StrategySelector:
    """
    Aggregates strategy signals and resolves conflicts.
    """

    def __init__(self) -> None:
        self._strategies: List[StrategyBase] = []

    def register(self, strategy: StrategyBase) -> None:
        self._strategies.append(strategy)

    def on_price_update(self, price: float) -> Optional[StrategySignal]:
        """
        Returns:
        - StrategySignal if exactly one clear decision exists
        - None if no action or conflicting signals
        """
        signals: List[StrategySignal] = []

        for strategy in self._strategies:
            signal = strategy.on_price_update(price)
            if signal.side is not None:
                signals.append(signal)

        if not signals:
            return None

        if len(signals) == 1:
            return signals[0]

        sides = {signal.side for signal in signals}
        if len(sides) > 1:
            return None

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals[0]
