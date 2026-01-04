from enum import Enum
from typing import Optional

from referral_program import ReferralProgram


class SubscriptionType(Enum):
    ADMIN = "admin"
    STANDARD = "standard"


class SubscriptionPlan:
    """
    Subscription pricing logic (no payments, no users).
    """

    def __init__(
        self,
        plan_type: SubscriptionType,
        referral: Optional[ReferralProgram] = None,
    ) -> None:
        self._plan_type = plan_type
        self._referral = referral

    def is_free(self) -> bool:
        return self._plan_type == SubscriptionType.ADMIN

    def price_usdt(self) -> float:
        if self.is_free():
            return 0.0

        if self._referral:
            return self._referral.apply()

        return ReferralProgram.BASE_MONTHLY_PRICE_USDT
