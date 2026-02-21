from typing import Dict
import time


class CircuitBreaker:

    def __init__(
        self,
        max_daily_loss: float = 0.1,
        max_drawdown: float = 0.2,
        max_errors_per_exchange: int = 5,
        cooldown_seconds: int = 300,
    ):

        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_errors_per_exchange = max_errors_per_exchange
        self.cooldown_seconds = cooldown_seconds

        self.start_equity = None
        self.current_equity = None

        self.exchange_errors: Dict[str, int] = {}
        self.exchange_blocked_until: Dict[str, float] = {}

        self.trading_paused_until = 0

    # -------------------------------------------------

    def update_equity(self, equity: float):

        if self.start_equity is None:
            self.start_equity = equity

        self.current_equity = equity

    # -------------------------------------------------

    def check_global_risk(self):

        if self.start_equity is None or self.current_equity is None:
            return True

        loss = (self.start_equity - self.current_equity) / self.start_equity

        if loss >= self.max_daily_loss:
            self.trading_paused_until = time.time() + self.cooldown_seconds
            return False

        return True

    # -------------------------------------------------

    def check_drawdown(self, peak_equity: float):

        if self.current_equity is None:
            return True

        dd = (peak_equity - self.current_equity) / peak_equity

        if dd >= self.max_drawdown:
            self.trading_paused_until = time.time() + self.cooldown_seconds
            return False

        return True

    # -------------------------------------------------

    def allow_trading(self):

        if time.time() < self.trading_paused_until:
            return False

        return True

    # -------------------------------------------------

    def report_exchange_error(self, exchange: str):

        count = self.exchange_errors.get(exchange, 0) + 1
        self.exchange_errors[exchange] = count

        if count >= self.max_errors_per_exchange:
            self.exchange_blocked_until[exchange] = (
                time.time() + self.cooldown_seconds
            )

    # -------------------------------------------------

    def exchange_allowed(self, exchange: str):

        blocked_until = self.exchange_blocked_until.get(exchange)

        if blocked_until is None:
            return True

        return time.time() > blocked_until

    # -------------------------------------------------

    def reset_exchange(self, exchange: str):
        self.exchange_errors[exchange] = 0
