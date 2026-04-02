from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RiskLimits:
    max_position_size: float
    max_notional: float
    max_leverage: float


class RiskEngine:

    def __init__(self):
        self.symbol_limits: Dict[str, RiskLimits] = {}
        self.account_equity: float = 0.0

    def set_account_equity(self, equity: float):
        self.account_equity = equity

    def set_symbol_limits(self, symbol: str, max_position_size: float, max_notional: float, max_leverage: float):
        self.symbol_limits[symbol] = RiskLimits(
            max_position_size=max_position_size,
            max_notional=max_notional,
            max_leverage=max_leverage,
        )

    def validate_order(self, symbol: str, side: str, price: float, size: float, current_position: float) -> bool:
        limits = self.symbol_limits.get(symbol)
        if limits is None:
            return True

        signed_size = size if side == "buy" else -size
        new_position = current_position + signed_size

        if abs(new_position) > limits.max_position_size:
            return False

        notional = abs(new_position * price)
        if notional > limits.max_notional:
            return False

        if self.account_equity > 0:
            leverage = notional / self.account_equity
            if leverage > limits.max_leverage:
                return False

        return True

    def calculate_notional(self, price: float, size: float) -> float:
        return abs(price * size)

    def calculate_leverage(self, notional: float) -> float:
        if self.account_equity == 0:
            return 0.0
        return notional / self.account_equity
