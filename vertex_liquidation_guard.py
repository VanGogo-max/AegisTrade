# vertex_liquidation_guard.py
"""
Vertex Liquidation Guard (FINAL)

Responsibility:
- Evaluate distance to liquidation
- Block execution when safety buffer is violated
- Exchange-agnostic risk interface, Vertex-specific parameters

No signing.
No sending.
No strategy logic.
"""

from typing import Dict, Any


class VertexLiquidationRisk(Exception):
    pass


class VertexLiquidationGuard:
    def __init__(self, min_buffer_ratio: float = 0.05):
        """
        min_buffer_ratio: minimal safe distance to liquidation (e.g. 5%)
        """
        self.min_buffer_ratio = min_buffer_ratio

    def evaluate(self, position: Dict[str, Any], mark_price: float) -> None:
        liq_price = position.get("liquidation_price")
        side = position.get("side")

        if liq_price is None:
            return

        if side.lower() in ("long", "buy"):
            buffer = (mark_price - liq_price) / mark_price
        else:
            buffer = (liq_price - mark_price) / mark_price

        if buffer < self.min_buffer_ratio:
            raise VertexLiquidationRisk(
                f"Vertex liquidation risk too high. "
                f"Buffer={buffer:.4f}, Threshold={self.min_buffer_ratio}"
            )
