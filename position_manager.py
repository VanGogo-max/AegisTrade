"""
position_manager.py

Manages lifecycle of trading positions.
In-memory only. No persistence, no exchange interaction.
"""

from typing import Dict, Optional
from uuid import uuid4

from types import (
    Position,
    TradingPair,
    MarketType,
    PositionSide,
    PositionStatus,
)


class PositionManager:
    """
    Central authority for position lifecycle.
    This class owns all mutations of Position state.
    """

    def __init__(self) -> None:
        self._positions: Dict[str, Position] = {}

    def open_position(
        self,
        market_type: MarketType,
        trading_pair: TradingPair,
        side: PositionSide,
        size: float,
        entry_price: float,
        leverage: Optional[float] = None,
    ) -> Position:
        position_id = str(uuid4())

        position = Position(
            position_id=position_id,
            market_type=market_type,
            trading_pair=trading_pair,
            side=side,
            size=size,
            entry_price=entry_price,
            leverage=leverage,
            status=PositionStatus.OPEN,
        )

        self._positions[position_id] = position
        return position

    def close_position(self, position_id: str) -> None:
        position = self._positions.get(position_id)
        if position is None:
            raise KeyError(f"Position {position_id} not found")

        # Centralized state transition
        position.status = PositionStatus.CLOSED

    def get_position(self, position_id: str) -> Position:
        position = self._positions.get(position_id)
        if position is None:
            raise KeyError(f"Position {position_id} not found")
        return position

    def all_positions(self) -> Dict[str, Position]:
        return dict(self._positions)
