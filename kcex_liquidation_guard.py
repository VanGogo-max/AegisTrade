# kcex_liquidation_guard.py
"""
Responsibility:
- Monitor positions for liquidation risk on KCEX (simulated)
- Trigger protective actions when margin thresholds are violated
"""

from typing import Dict


class KCEXLiquidationGuard:
    def __init__(self, maintenance_margin_ratio: float = 0.05):
        self.maintenance_margin_ratio = maintenance_margin_ratio

    def check_liquidation_risk(self, position: Dict) -> bool:
        """
        Returns True if position is in liquidation danger zone.
        Expected position keys:
        - equity
        - margin
        """
        equity = position.get("equity", 0)
        margin = position.get("margin", 0)

        if margin <= 0:
            return True

        ratio = equity / margin
        return ratio < self.maintenance_margin_ratio

    def enforce(self, position_id: str, position: Dict) -> str:
        if self.check_liquidation_risk(position):
            return f"LIQUIDATION_TRIGGERED:{position_id}"
        return f"SAFE:{position_id}"
      
