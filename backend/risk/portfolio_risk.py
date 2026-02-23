"""
Portfolio Risk Engine

Aggregates risk across all positions.

Responsibilities
----------------
• Total exposure
• Portfolio leverage
• Concentration limits
• Drawdown monitoring
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PortfolioLimits:

    max_total_exposure: float
    max_leverage: float
    max_symbol_concentration: float
    max_drawdown: float


@dataclass
class Position:

    symbol: str
    size: float
    entry_price: float


class PortfolioRisk:

    def __init__(self):

        self.positions: Dict[str, Position] = {}

        self.account_equity: float = 0.0
        self.peak_equity: float = 0.0

        self.limits = PortfolioLimits(
            max_total_exposure=0,
            max_leverage=0,
            max_symbol_concentration=0,
            max_drawdown=0,
        )

    # ------------------------------------------------
    # Config
    # ------------------------------------------------

    def set_limits(
        self,
        max_total_exposure: float,
        max_leverage: float,
        max_symbol_concentration: float,
        max_drawdown: float,
    ):

        self.limits = PortfolioLimits(
            max_total_exposure,
            max_leverage,
            max_symbol_concentration,
            max_drawdown,
        )

    def update_equity(self, equity: float):

        self.account_equity = equity

        if equity > self.peak_equity:
            self.peak_equity = equity

    # ------------------------------------------------
    # Position updates
    # ------------------------------------------------

    def update_position(
        self,
        symbol: str,
        size: float,
        entry_price: float,
    ):

        self.positions[symbol] = Position(
            symbol=symbol,
            size=size,
            entry_price=entry_price,
        )

    def remove_position(self, symbol: str):

        if symbol in self.positions:
            del self.positions[symbol]

    # ------------------------------------------------
    # Metrics
    # ------------------------------------------------

    def total_exposure(self) -> float:

        exposure = 0.0

        for p in self.positions.values():
            exposure += abs(p.size * p.entry_price)

        return exposure

    def portfolio_leverage(self) -> float:

        if self.account_equity == 0:
            return 0.0

        return self.total_exposure() / self.account_equity

    def symbol_concentration(self) -> Dict[str, float]:

        total = self.total_exposure()

        if total == 0:
            return {}

        concentration = {}

        for p in self.positions.values():

            exposure = abs(p.size * p.entry_price)

            concentration[p.symbol] = exposure / total

        return concentration

    def drawdown(self) -> float:

        if self.peak_equity == 0:
            return 0.0

        return (self.peak_equity - self.account_equity) / self.peak_equity

    # ------------------------------------------------
    # Risk checks
    # ------------------------------------------------

    def check_total_exposure(self) -> bool:

        return self.total_exposure() <= self.limits.max_total_exposure

    def check_leverage(self) -> bool:

        return self.portfolio_leverage() <= self.limits.max_leverage

    def check_concentration(self) -> bool:

        concentration = self.symbol_concentration()

        for value in concentration.values():
            if value > self.limits.max_symbol_concentration:
                return False

        return True

    def check_drawdown(self) -> bool:

        return self.drawdown() <= self.limits.max_drawdown

    # ------------------------------------------------
    # Global validation
    # ------------------------------------------------

    def portfolio_ok(self) -> bool:

        if not self.check_total_exposure():
            return False

        if not self.check_leverage():
            return False

        if not self.check_concentration():
            return False

        if not self.check_drawdown():
            return False

        return True
