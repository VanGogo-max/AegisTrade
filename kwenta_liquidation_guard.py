# kwenta_liquidation_guard.py
"""
Kwenta Liquidation Guard (FINAL)

Responsibility:
- Monitors positions for liquidation risk
- Computes safety margin vs liquidation price
- Emits alerts / hard blocks execution when risk threshold is crossed
- No execution, no signing, no RPC

References:
- Kwenta Perps Risk Model: https://docs.kwenta.io
"""

from typing import Dict, Any


class KwentaLiquidationRisk(Exception):
    pass


class KwentaLiquidationGuard:
    def __init__(self, min_buffer_ratio: float = 0.05):
        """
        min_buffer_ratio: minimal distance from liquidation price (e.g. 5%)
        """
        self.min_buffer_ratio = min_buffer_ratio

    def evaluate(self, position: Dict[str, Any], mark_price: float) -> None:
        """
        Raises KwentaLiquidationRisk if position is too close to liquidation.
        """
        liq_price = position.get("liquidation_price")
        side = position.get("side")

        if liq_price is None:
            return  # Cannot evaluate, assume safe (or handled upstream)

        if side == "long":
            buffer = (mark_price - liq_price) / mark_price
        else:
            buffer = (liq_price - mark_price) / mark_price

        if buffer < self.min_buffer_ratio:
            raise KwentaLiquidationRisk(
                f"Liquidation risk too high. Buffer={buffer:.4f}, "
                f"Threshold={self.min_buffer_ratio}"
            )
