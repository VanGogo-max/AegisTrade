from dataclasses import dataclass
from typing import Dict


@dataclass
class PortfolioRiskState:
    total_exposure: float
    exposure_pct: float
    positions: int
    allowed: bool


class PortfolioRiskManager:

    def __init__(
        self,
        equity: float,
        max_total_exposure_pct: float = 0.5,
        max_positions: int = 10
    ):
        self.equity = equity
        self.max_total_exposure_pct = max_total_exposure_pct
        self.max_positions = max_positions

        self.positions: Dict[str, float] = {}

    def update_equity(self, equity: float):
        self.equity = equity

    def register_position(self, symbol: str, notional_value: float):
        self.positions[symbol] = notional_value

    def close_position(self, symbol: str):
        if symbol in self.positions:
            del self.positions[symbol]

    def evaluate(self) -> PortfolioRiskState:

        total_exposure = sum(self.positions.values())

        exposure_pct = 0
        if self.equity > 0:
            exposure_pct = total_exposure / self.equity

        allowed = True

        if exposure_pct > self.max_total_exposure_pct:
            allowed = False

        if len(self.positions) > self.max_positions:
            allowed = False

        return PortfolioRiskState(
            total_exposure=total_exposure,
            exposure_pct=exposure_pct,
            positions=len(self.positions),
            allowed=allowed
        )
