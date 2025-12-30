"""
risk_manager.py

Applies risk constraints before allowing position creation.
"""

from typing import Optional

from types import MarketType, PositionSide, PositionStatus
from position_manager import PositionManager


class RiskManager:
    """
    Validates risk constraints for new positions.
    Raises exceptions if rules are violated.
    """

    def __init__(
        self,
        max_position_size: float,
        max_open_positions: int,
        max_leverage: Optional[float] = None,
    ) -> None:
        self.max_position_size = max_position_size
        self.max_open_positions = max_open_positions
        self.max_leverage = max_leverage

    def validate_new_position(
        self,
        position_manager: PositionManager,
        market_type: MarketType,
        side: PositionSide,
        size: float,
        leverage: Optional[float],
    ) -> None:
        # Rule 1: position size
        if size <= 0:
            raise ValueError("Position size must be positive")

        if size > self.max_position_size:
            raise ValueError("Position size exceeds maximum allowed")

        # Rule 2: open positions count
        open_positions = [
            p for p in position_manager.all_positions().values()
            if p.status == PositionStatus.OPEN
        ]

        if len(open_positions) >= self.max_open_positions:
            raise ValueError("Maximum number of open positions reached")

        # Rule 3: leverage constraints
        if market_type == MarketType.SPOT:
            if leverage is not None:
                raise ValueError("Leverage is not allowed on SPOT market")

        if market_type == MarketType.FUTURES:
            if leverage is None:
                raise ValueError("Leverage must be specified for FUTURES market")

            if self.max_leverage is not None and leverage > self.max_leverage:
                raise ValueError("Leverage exceeds maximum allowed")
