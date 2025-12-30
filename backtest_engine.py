"""
backtest_engine.py

Runs offline backtests on historical market data.
"""

from typing import List, Dict, Any

from strategy_base import StrategyBase
from position_manager import PositionManager
from risk_manager import RiskManager
from performance_tracker import PerformanceTracker


class BacktestEngine:
    """
    Orchestrates backtesting by feeding historical bars
    into a trading strategy and tracking performance.
    """

    def __init__(
        self,
        strategy: StrategyBase,
        initial_balance: float,
        risk_per_trade: float,
    ) -> None:
        self.position_manager = PositionManager(initial_balance)
        self.risk_manager = RiskManager(risk_per_trade)
        self.performance_tracker = PerformanceTracker()
        self.strategy = strategy

    def run(self, historical_bars: List[Dict[str, Any]]) -> None:
        """
        Runs the backtest over historical OHLCV bars.
        """
        for bar in historical_bars:
            self.strategy.on_bar(
                bar=bar,
                position_manager=self.position_manager,
                risk_manager=self.risk_manager,
            )

            closed_positions = self.position_manager.get_closed_positions()
            for position in closed_positions:
                self.performance_tracker.on_position_closed(position)
