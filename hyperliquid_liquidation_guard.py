
"""
Hyperliquid Liquidation Guard (FINAL)

Role:
- Real-time safety layer against liquidation
- Blocks opening / increasing positions if:
    - margin ratio is below threshold
    - price is too close to liquidation
- Works with:
    - hyperliquid_position_tracker
    - risk_engine
    - execution_engine
"""

from typing import Dict, Any


class HyperliquidLiquidationRisk(Exception):
    pass


class HyperliquidLiquidationGuard:
    def __init__(self, min_margin_ratio: float = 0.12, min_distance_pct: float = 0.01):
        """
        Args:
            min_margin_ratio: minimal collateral / position size
            min_distance_pct: minimal distance to liquidation price (1% default)
        """
        self.min_margin_ratio = min_margin_ratio
        self.min_distance_pct = min_distance_pct

    def evaluate(self, position_state: Dict[str, Any]) -> None:
        required = {
            "collateral_usd",
            "size_usd",
            "liquidation_price",
            "mark_price",
        }
        missing = required - position_state.keys()
        if missing:
            raise ValueError(f"Missing fields for liquidation check: {missing}")

        margin_ratio = position_state["collateral_usd"] / position_state["size_usd"]

        if margin_ratio < self.min_margin_ratio:
            raise HyperliquidLiquidationRisk(
                f"Margin ratio too low: {margin_ratio:.4f} < {self.min_margin_ratio}"
            )

        distance = abs(
            position_state["mark_price"] - position_state["liquidation_price"]
        ) / position_state["mark_price"]

        if distance < self.min_distance_pct:
            raise HyperliquidLiquidationRisk(
                f"Price too close to liquidation: {distance*100:.2f}%"
            )
hyperliquid_liquidation_guard.py
