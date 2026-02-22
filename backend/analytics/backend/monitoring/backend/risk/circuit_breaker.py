# backend/risk/circuit_breaker.py

import time


class CircuitBreaker:

    def __init__(
        self,
        max_daily_loss: float = 0.1,
        max_consecutive_losses: int = 5,
        cooldown_time: int = 900
    ):
        """
        max_daily_loss = 0.1 -> 10%
        cooldown_time в секунди
        """

        self.max_daily_loss = max_daily_loss
        self.max_consecutive_losses = max_consecutive_losses
        self.cooldown_time = cooldown_time

        self.start_balance = None
        self.current_balance = None

        self.consecutive_losses = 0

        self.tripped = False
        self.trip_time = None

    def start_day(self, balance: float):

        self.start_balance = balance
        self.current_balance = balance
        self.consecutive_losses = 0
        self.tripped = False
        self.trip_time = None

    def update_balance(self, balance: float):

        self.current_balance = balance

        if self.start_balance is None:
            return

        drawdown = (self.start_balance - self.current_balance) / self.start_balance

        if drawdown >= self.max_daily_loss:
            self.trip("MAX_DAILY_LOSS")

    def record_trade(self, pnl: float):

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        if self.consecutive_losses >= self.max_consecutive_losses:
            self.trip("CONSECUTIVE_LOSSES")

    def trip(self, reason: str):

        self.tripped = True
        self.trip_time = time.time()
        print(f"CIRCUIT BREAKER TRIPPED: {reason}")

    def can_trade(self):

        if not self.tripped:
            return True

        if (time.time() - self.trip_time) > self.cooldown_time:
            self.reset()
            return True

        return False

    def reset(self):

        self.tripped = False
        self.consecutive_losses = 0
        self.trip_time = None
