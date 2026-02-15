from dataclasses import dataclass
from typing import List


@dataclass
class DrawdownConfig:
    max_total_drawdown: float = 0.15     # 15% максимален спад
    daily_drawdown_limit: float = 0.05   # 5% дневен лимит
    recovery_threshold: float = 0.05     # 5% възстановяване преди рестарт


class DrawdownGuard:

    def __init__(self, config: DrawdownConfig):
        self.config = config

        self.equity_history: List[float] = []
        self.peak_equity: float = 0.0
        self.trading_locked: bool = False
        self.lock_reason: str = ""

    # ----------------------------------------
    # UPDATE EQUITY
    # ----------------------------------------
    def update_equity(self, current_equity: float):

        self.equity_history.append(current_equity)

        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        drawdown = self._calculate_drawdown(current_equity)

        if drawdown >= self.config.max_total_drawdown:
            self.trading_locked = True
            self.lock_reason = "MAX_TOTAL_DRAWDOWN"

    # ----------------------------------------
    # DAILY CHECK
    # ----------------------------------------
    def check_daily_drawdown(self, daily_loss_pct: float):

        if daily_loss_pct >= self.config.daily_drawdown_limit:
            self.trading_locked = True
            self.lock_reason = "DAILY_DRAWDOWN_LIMIT"

    # ----------------------------------------
    # RECOVERY MODE
    # ----------------------------------------
    def try_recover(self, current_equity: float):

        if not self.trading_locked:
            return

        recovery_needed = self.peak_equity * self.config.recovery_threshold

        if current_equity >= self.peak_equity - recovery_needed:
            self.trading_locked = False
            self.lock_reason = ""

    # ----------------------------------------
    # STATUS
    # ----------------------------------------
    def can_trade(self) -> bool:
        return not self.trading_locked

    def get_status(self):
        return {
            "trading_locked": self.trading_locked,
            "lock_reason": self.lock_reason,
            "peak_equity": self.peak_equity,
        }

    # ----------------------------------------
    # INTERNAL
    # ----------------------------------------
    def _calculate_drawdown(self, current_equity: float) -> float:

        if self.peak_equity == 0:
            return 0.0

        return (self.peak_equity - current_equity) / self.peak_equity
