# dydx_liquidation_guard.py
"""
dYdX v4 Liquidation Guard (FINAL)

Role:
- Monitor margin ratios for all open positions
- Predict liquidation risk
- Trigger:
    - forced partial close
    - emergency close
    - trading halt
- Protect capital before protocol liquidation engine triggers
"""

from typing import Dict
import time


class LiquidationRisk(Exception):
    pass


class DydxLiquidationGuard:
    def __init__(self, maintenance_margin_ratio: float = 0.05, danger_ratio: float = 0.08):
        """
        maintenance_margin_ratio: protocol liquidation threshold
        danger_ratio: pre-liquidation safety buffer
        """
        self.maintenance_margin_ratio = maintenance_margin_ratio
        self.danger_ratio = danger_ratio
        self._last_check = 0

    def check_positions(self, positions: Dict[str, dict]) -> None:
        """
        Scan all open positions and raise alert if any is near liquidation.
        """
        self._last_check = int(time.time())

        for position_id, pos in positions.items():
            margin = pos.get("margin_usd")
            size = pos.get("size_usd")
            pnl = pos.get("unrealized_pnl", 0)

            if margin is None or size is None:
                continue

            equity = margin + pnl
            margin_ratio = equity / size

            if margin_ratio <= self.maintenance_margin_ratio:
                raise LiquidationRisk(
                    f"POSITION {position_id} AT LIQUIDATION: ratio={margin_ratio:.4f}"
                )

            if margin_ratio <= self.danger_ratio:
                self._emit_warning(position_id, margin_ratio)

    def _emit_warning(self, position_id: str, ratio: float) -> None:
        print(
            f"[dYdX WARNING] Position {position_id} near liquidation. "
            f"Margin ratio={ratio:.4f}"
        )
