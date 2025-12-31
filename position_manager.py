from datetime import datetime
from typing import Dict

from position_state import (
    PositionState,
    MarketType,
    PositionSide,
    PositionStatus,
)


class PositionManager:
    """
    Управлява всички активни и затворени позиции в паметта.
    """

    def __init__(self) -> None:
        self._positions: Dict[str, PositionState] = {}

    def open_position(
        self,
        position_id: str,
        symbol: str,
        market_type: MarketType,
        side: PositionSide,
        entry_price: float,
        quantity: float,
    ) -> PositionState:
        if position_id in self._positions:
            raise ValueError("Position with this ID already exists")

        position = PositionState(
            position_id=position_id,
            symbol=symbol,
            market_type=market_type,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            status=PositionStatus.OPEN,
            opened_at=datetime.utcnow(),
        )

        self._positions[position_id] = position
        return position

    def close_position(
        self,
        position_id: str,
        exit_price: float,
    ) -> PositionState:
        if position_id not in self._positions:
            raise KeyError("Position not found")

        position = self._positions[position_id]

        if position.status != PositionStatus.OPEN:
            raise ValueError("Position is not open")

        pnl = self._calculate_pnl(position, exit_price)

        position.exit_price = exit_price
        position.realized_pnl = pnl
        position.closed_at = datetime.utcnow()
        position.status = PositionStatus.CLOSED

        return position

    def get_position(self, position_id: str) -> PositionState:
        if position_id not in self._positions:
            raise KeyError("Position not found")
        return self._positions[position_id]

    def all_positions(self) -> Dict[str, PositionState]:
        """
        Връща snapshot на всички позиции.
        PositionManager остава owner на state-а.
        """
        return dict(self._positions)

    @staticmethod
    def _calculate_pnl(position: PositionState, exit_price: float) -> float:
        if exit_price <= 0:
            raise ValueError("exit_price must be positive")

        price_diff = exit_price - position.entry_price

        if position.side == PositionSide.SHORT:
            price_diff = -price_diff

        return price_diff * position.quantity
