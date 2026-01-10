# gmx_margin_monitor.py
"""
FINAL

Purpose:
- Real-time margin and liquidation proximity monitor for GMX
- Consumes GMXAccountState snapshots
- Emits alerts when margin ratio or liquidation risk crosses thresholds
- No execution, no signing, no trading logic

Used by:
- gmx_liquidation_guard.py
- execution_engine (risk gate)
- alerting / monitoring systems
"""

from dataclasses import dataclass
from typing import Callable

from gmx_account_state import GMXAccountState


@dataclass(frozen=True)
class MarginAlert:
    wallet: str
    margin_ratio: float
    liquidation_risk: float
    level: str  # "SAFE", "WARNING", "CRITICAL"


class GMXMarginMonitor:
    """
    Evaluates margin health and liquidation proximity.
    """

    def __init__(
        self,
        warning_margin_ratio: float = 0.25,
        critical_margin_ratio: float = 0.15,
        critical_liquidation_risk: float = 0.8,
    ):
        self.warning_margin_ratio = warning_margin_ratio
        self.critical_margin_ratio = critical_margin_ratio
        self.critical_liquidation_risk = critical_liquidation_risk

    def evaluate(self, state: GMXAccountState) -> MarginAlert:
        """
        Classify current margin health.
        """
        level = "SAFE"

        if (
            state.margin_ratio <= self.critical_margin_ratio
            or state.liquidation_risk >= self.critical_liquidation_risk
        ):
            level = "CRITICAL"

        elif state.margin_ratio <= self.warning_margin_ratio:
            level = "WARNING"

        return MarginAlert(
            wallet=state.wallet,
            margin_ratio=state.margin_ratio,
            liquidation_risk=state.liquidation_risk,
            level=level,
        )

    def should_halt_trading(self, alert: MarginAlert) -> bool:
        """
        Hard stop for new positions when in critical state.
        """
        return alert.level == "CRITICAL"

    def should_reduce_positions(self, alert: MarginAlert) -> bool:
        """
        Signal to start reducing exposure before liquidation.
        """
        return alert.level in {"WARNING", "CRITICAL"}
