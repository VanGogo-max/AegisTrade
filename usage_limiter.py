# usage_limiter.py

from typing import Dict, Tuple
from datetime import datetime, timedelta


class UsageLimiter:
    """
    Enforces quantitative usage limits per user.
    """

    def __init__(self) -> None:
        self._bot_count: Dict[str, int] = {}
        self._order_log: Dict[str, list[datetime]] = {}
        self._positions: Dict[str, int] = {}

        self._limits = {
            "basic": {
                "max_bots": 1,
                "max_orders_per_day": 50,
                "max_positions": 3,
            },
            "pro": {
                "max_bots": 3,
                "max_orders_per_day": 200,
                "max_positions": 10,
            },
            "admin": {
                "max_bots": 999,
                "max_orders_per_day": 999999,
                "max_positions": 999,
            },
        }

    def _validate_plan(self, plan: str) -> None:
        if plan not in self._limits:
            raise ValueError(f"Unknown subscription plan: {plan}")

    def can_start_bot(self, user_id: str, plan: str) -> Tuple[bool, str]:
        self._validate_plan(plan)

        active = self._bot_count.get(user_id, 0)
        limit = self._limits[plan]["max_bots"]

        if active >= limit:
            return False, "Bot limit reached"

        return True, "OK"

    def register_bot_start(self, user_id: str) -> None:
        self._bot_count[user_id] = self._bot_count.get(user_id, 0) + 1

    def register_bot_stop(self, user_id: str) -> None:
        if self._bot_count.get(user_id, 0) > 0:
            self._bot_count[user_id] -= 1

    def can_place_order(self, user_id: str, plan: str) -> Tuple[bool, str]:
        self._validate_plan(plan)

        now = datetime.utcnow()
        cutoff = now - timedelta(days=1)

        orders = self._order_log.get(user_id, [])
        orders = [t for t in orders if t > cutoff]
        self._order_log[user_id] = orders

        if len(orders) >= self._limits[plan]["max_orders_per_day"]:
            return False, "Daily order limit reached"

        return True, "OK"

    def register_order(self, user_id: str) -> None:
        self._order_log.setdefault(user_id, []).append(datetime.utcnow())

    def can_open_position(self, user_id: str, plan: str) -> Tuple[bool, str]:
        self._validate_plan(plan)

        active = self._positions.get(user_id, 0)
        limit = self._limits[plan]["max_positions"]

        if active >= limit:
            return False, "Position limit reached"

        return True, "OK"

    def register_position_open(self, user_id: str) -> None:
        self._positions[user_id] = self._positions.get(user_id, 0) + 1

    def register_position_close(self, user_id: str) -> None:
        if self._positions.get(user_id, 0) > 0:
            self._positions[user_id] -= 1
