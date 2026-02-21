from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionSizeResult:
    size: float
    risk_amount: float
    stop_distance: float


class PositionSizer:
    """
    Calculates safe position sizes based on:

    - account equity
    - max risk per trade
    - stop distance
    - optional leverage
    """

    def __init__(
        self,
        equity: float,
        max_risk_per_trade: float = 0.01,
        max_position_pct: float = 0.20,
    ):
        """
        equity: total capital
        max_risk_per_trade: % of equity allowed to risk
        max_position_pct: maximum allocation per trade
        """

        self.equity = equity
        self.max_risk_per_trade = max_risk_per_trade
        self.max_position_pct = max_position_pct

    def update_equity(self, new_equity: float):
        self.equity = new_equity

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
        leverage: float = 1.0,
    ) -> Optional[PositionSizeResult]:

        if entry_price <= 0 or stop_price <= 0:
            return None

        stop_distance = abs(entry_price - stop_price)

        if stop_distance == 0:
            return None

        # how much money we are willing to lose
        risk_amount = self.equity * self.max_risk_per_trade

        # position size based on stop distance
        raw_size = risk_amount / stop_distance

        # leverage
        raw_size *= leverage

        # max capital allocation
        max_position_value = self.equity * self.max_position_pct
        max_size_allowed = max_position_value / entry_price

        final_size = min(raw_size, max_size_allowed)

        return PositionSizeResult(
            size=final_size,
            risk_amount=risk_amount,
            stop_distance=stop_distance,
        )
