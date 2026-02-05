"""
performance_tracker.py

Tracks trading performance metrics.
"""

from typing import List

from domain_types import PositionSide
from position_manager import Position


class PerformanceTracker:
    """
    Passive component that records closed positions
    and calculates basic performance statistics.
    """

    def __init__(self) -> None:
        self.closed_positions: List[Position] = []
        self.total_pnl: float = 0.0
        self.win_count: int = 0
        self.loss_count: int = 0

    def on_position_closed(self, position: Position) -> None:
        """
        Registers a closed position and updates metrics.
        """
        if position.exit_price is None:
            raise ValueError("Position must have exit_price to be tracked.")

        pnl = self._calculate_pnl(position)
        self.total_pnl += pnl

        if pnl > 0:
            self.win_count += 1
        else:
            self.loss_count += 1

        self.closed_positions.append(position)

    def win_rate(self) -> float:
        """
        Returns win rate as a float between 0 and 1.
        """
        total = self.win_count + self.loss_count
        if total == 0:
            return 0.0
        return self.win_count / total

    def _calculate_pnl(self, position: Position) -> float:
        """
        Calculates realized PnL for a position.
        """
        if position.side == PositionSide.LONG:
            return (position.exit_price - position.entry_price) * position.size
        return (position.entry_price - position.exit_price) * position.size
