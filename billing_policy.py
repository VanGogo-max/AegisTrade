from enum import Enum
from datetime import datetime, timedelta
from typing import Optional

from subscription_plan import SubscriptionPlan


class BillingStatus(Enum):
    ADMIN_FREE = "admin_free"
    ACTIVE = "active"
    GRACE = "grace"
    EXPIRED = "expired"


class BillingPolicy:
    """
    Subscription billing status rules (no payments, no blockchain).
    """

    SUBSCRIPTION_DAYS = 30
    GRACE_DAYS = 3

    def __init__(
        self,
        plan: SubscriptionPlan,
        last_payment_at: Optional[datetime],
    ) -> None:
        self._plan = plan
        self._last_payment_at = last_payment_at

    def status(self, now: Optional[datetime] = None) -> BillingStatus:
        current_time = now or datetime.utcnow()

        if self._plan.is_free():
            return BillingStatus.ADMIN_FREE

        if self._last_payment_at is None:
            return BillingStatus.EXPIRED

        expiry_time = self._last_payment_at + timedelta(days=self.SUBSCRIPTION_DAYS)

        if current_time <= expiry_time:
            return BillingStatus.ACTIVE

        if current_time <= expiry_time + timedelta(days=self.GRACE_DAYS):
            return BillingStatus.GRACE

        return BillingStatus.EXPIRED

    def has_access(self, now: Optional[datetime] = None) -> bool:
        return self.status(now) in {
            BillingStatus.ADMIN_FREE,
            BillingStatus.ACTIVE,
            BillingStatus.GRACE,
        }
