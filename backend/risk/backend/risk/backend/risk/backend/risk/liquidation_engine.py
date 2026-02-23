"""
Liquidation Engine

Responsibilities
----------------
• Track margin requirements
• Calculate liquidation price
• Trigger partial/full liquidation
• Integrate with position_store and risk_engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Position:
    symbol: str
    size: float
    entry_price: float
    margin: float  # margin allocated to this position


@dataclass
class LiquidationResult:
    symbol: str
    liquidated_size: float
    reason: str
    remaining_margin: float


class LiquidationEngine:

    def __init__(self, account_equity: float = 0.0):

        self.positions: Dict[str, Position] = {}
        self.account_equity: float = account_equity
        self.maintenance_margin_ratio: float = 0.25  # 25% typical

    # ---------------------------------------------------
    # Position management
    # ---------------------------------------------------

    def update_position(
        self,
        symbol: str,
        size: float,
        entry_price: float,
        margin: float,
    ):

        self.positions[symbol] = Position(
            symbol=symbol,
            size=size,
            entry_price=entry_price,
            margin=margin,
        )

    def remove_position(self, symbol: str):

        if symbol in self.positions:
            del self.positions[symbol]

    # ---------------------------------------------------
    # Liquidation logic
    # ---------------------------------------------------

    def check_liquidations(self) -> list[LiquidationResult]:

        results: list[LiquidationResult] = []

        for symbol, pos in self.positions.items():

            if pos.size == 0:
                continue

            # simple mark-to-market loss
            current_value = pos.size * pos.entry_price
            margin_remaining = pos.margin + (self.account_equity - current_value)

            # if margin below maintenance -> liquidate
            if margin_remaining < pos.margin * self.maintenance_margin_ratio:

                results.append(
                    LiquidationResult(
                        symbol=symbol,
                        liquidated_size=pos.size,
                        reason="margin_breach",
                        remaining_margin=max(margin_remaining, 0),
                    )
                )

        return results

    def trigger_liquidation(self) -> list[LiquidationResult]:

        to_liquidate = self.check_liquidations()

        for res in to_liquidate:

            # close fully for simplicity
            if res.symbol in self.positions:
                self.positions[res.symbol].size = 0
                self.positions[res.symbol].margin = res.remaining_margin

        return to_liquidate
