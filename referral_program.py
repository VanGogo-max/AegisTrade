from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ReferralRule:
    discount_percent: float
    max_uses: Optional[int] = None

    def is_valid(self) -> bool:
        return 0.0 <= self.discount_percent <= 100.0


@dataclass
class ReferralUsage:
    used_count: int = 0


class ReferralProgram:
    """
    Referral discount calculation logic.
    """

    BASE_MONTHLY_PRICE_USDT = 10.0

    def __init__(self, rule: ReferralRule) -> None:
        if not rule.is_valid():
            raise ValueError("Invalid referral discount percent")
        self._rule = rule
        self._usage = ReferralUsage()

    def can_apply(self) -> bool:
        if self._rule.max_uses is None:
            return True
        return self._usage.used_count < self._rule.max_uses

    def current_price(self) -> float:
        if not self.can_apply():
            return self.BASE_MONTHLY_PRICE_USDT

        discount = self.BASE_MONTHLY_PRICE_USDT * (
            self._rule.discount_percent / 100.0
        )
        return round(self.BASE_MONTHLY_PRICE_USDT - discount, 2)

    def apply(self) -> float:
        price = self.current_price()
        if self.can_apply():
            self._usage.used_count += 1
        return price

    def usage_count(self) -> int:
        return self._usage.used_count
