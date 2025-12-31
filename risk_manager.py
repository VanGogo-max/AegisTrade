from typing import Dict

from position_state import (
    PositionState,
    PositionStatus,
)


class RiskManager:
    """
    Централизиран контрол на риска.
    """

    def __init__(
        self,
        max_risk_per_position_usd: float,
        max_total_risk_usd: float,
    ) -> None:
        if max_risk_per_position_usd <= 0:
            raise ValueError("max_risk_per_position_usd must be positive")

        if max_total_risk_usd <= 0:
            raise ValueError("max_total_risk_usd must be positive")

        self.max_risk_per_position_usd = max_risk_per_position_usd
        self.max_total_risk_usd = max_total_risk_usd

    def validate_new_position(
        self,
        entry_price: float,
        quantity: float,
        stop_loss_price: float,
        existing_positions: Dict[str, PositionState],
    ) -> None:
        """
        Проверява дали нова позиция може да бъде отворена.
        Вдига exception при нарушение на риск лимит.
        """

        if entry_price <= 0 or quantity <= 0:
            raise ValueError("entry_price and quantity must be positive")

        if stop_loss_price <= 0:
            raise ValueError("stop_loss_price must be positive")

        position_risk = abs(entry_price - stop_loss_price) * quantity

        if position_risk > self.max_risk_per_position_usd:
            raise ValueError("Position risk exceeds max allowed per position")

        total_risk = position_risk

        for pos in existing_positions.values():
            if pos.status != PositionStatus.OPEN:
                continue

            # Консервативен worst-case риск
            existing_risk = pos.entry_price * pos.quantity
            total_risk += existing_risk

        if total_risk > self.max_total_risk_usd:
            raise ValueError("Total risk exceeds max allowed exposure")
