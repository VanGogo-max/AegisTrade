from dataclasses import dataclass
from datetime import datetime


@dataclass
class DrawdownState:
    peak_equity: float
    current_equity: float
    drawdown_pct: float
    trading_blocked: bool
    timestamp: datetime


class DrawdownGuard:

    def __init__(
        self,
        max_drawdown_pct: float = 0.20,
        daily_drawdown_pct: float = 0.10
    ):
        self.max_drawdown_pct = max_drawdown_pct
        self.daily_drawdown_pct = daily_drawdown_pct

        self.peak_equity = None
        self.start_of_day_equity = None
        self.trading_blocked = False

    def reset_daily(self, equity: float):
        self.start_of_day_equity = equity

    def update(self, equity: float) -> DrawdownState:

        if self.peak_equity is None:
            self.peak_equity = equity

        if self.start_of_day_equity is None:
            self.start_of_day_equity = equity

        if equity > self.peak_equity:
            self.peak_equity = equity

        total_dd = (self.peak_equity - equity) / self.peak_equity
        daily_dd = (self.start_of_day_equity - equity) / self.start_of_day_equity

        if total_dd >= self.max_drawdown_pct:
            self.trading_blocked = True

        if daily_dd >= self.daily_drawdown_pct:
            self.trading_blocked = True

        return DrawdownState(
            peak_equity=self.peak_equity,
            current_equity=equity,
            drawdown_pct=total_dd,
            trading_blocked=self.trading_blocked,
            timestamp=datetime.utcnow()
        )
