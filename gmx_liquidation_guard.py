# gmx_liquidation_guard.py
"""
GMX Liquidation Guard (FINAL)

Role:
- Prevent opening or increasing positions too close to liquidation
- Continuously evaluate margin safety
- Hard-block execution if liquidation risk exceeds threshold
- Used by:
    - execution_engine
    - state_reconciler
    - margin_monitor
"""

from typing import Dict, Any


class LiquidationRiskError(Exception):
    pass


class GMXLiquidationGuard:
    def __init__(self, min_margin_ratio: float = 0.15):
        """
        Args:
            min_margin_ratio: minimal allowed margin ratio (e.g. 0.15 = 15%)
        """
        self.min_margin_ratio = min_margin_ratio

    def evaluate(self, position_state: Dict[str, Any]) -> None:
        """
        position_state must contain:
            - collateral_usd
            - size_usd
            - liquidation_price
            - mark_price
        """
        required = {"collateral_usd", "size_usd", "liquidation_price", "mark_price"}
        missing = required - position_state.keys()
        if missing:
            raise ValueError(f"Missing liquidation fields: {missing}")

        margin_ratio = position_state["collateral_usd"] / position_state["size_usd"]

        if margin_ratio < self.min_margin_ratio:
            raise LiquidationRiskError(
                f"Margin ratio too low: {margin_ratio:.4f} < {self.min_margin_ratio}"
            )

        distance_to_liq = abs(
            position_state["mark_price"] - position_state["liquidation_price"]
        ) / position_state["mark_price"]

        if distance_to_liq < 0.01:
            raise LiquidationRiskError(
                f"Price too close to liquidation: {distance_to_liq*100:.2f}%"
            )
