# subscription_manager.py

from datetime import datetime, timedelta
from typing import Optional, Dict


class SubscriptionManager:
    """
    Handles subscription validation, admin access and referral discounts.
    """

    MONTHLY_PRICE_USDT = 10.0
    PAYMENT_NETWORK = "Polygon"
    PAYMENT_ADDRESS = "0xfee37e7e64d70f37f96c42375131abb57c1481c2"

    def __init__(self, admin_user_id: str) -> None:
        self._admin_user_id = admin_user_id
        self._subscriptions: Dict[str, datetime] = {}
        self._referrals: Dict[str, float] = {}

        # Grant lifetime admin access to the owner
        self._subscriptions[admin_user_id] = datetime.max

    def is_admin(self, user_id: str) -> bool:
        """
        Checks if the user is the platform admin.
        """
        return user_id == self._admin_user_id

    def add_referral(self, referral_code: str, discount_percent: float) -> None:
        """
        Registers a referral code with a discount percentage.
        """
        if not (0 < discount_percent < 100):
            raise ValueError("Discount percent must be between 0 and 100")

        self._referrals[referral_code] = discount_percent

    def activate_subscription(
        self,
        user_id: str,
        months: int = 1,
        referral_code: Optional[str] = None,
    ) -> float:
        """
        Activates a subscription and returns the final price after discount.
        """
        if months <= 0:
            raise ValueError("Subscription duration must be positive")

        base_price = self.MONTHLY_PRICE_USDT * months
        discount = 0.0

        if referral_code and referral_code in self._referrals:
            discount = base_price * (self._referrals[referral_code] / 100.0)

        final_price = base_price - discount
        expiry = datetime.utcnow() + timedelta(days=30 * months)
        self._subscriptions[user_id] = expiry

        return round(final_price, 2)

    def is_active(self, user_id: str) -> bool:
        """
        Checks whether the user's subscription is active.
        """
        if self.is_admin(user_id):
            return True

        expiry = self._subscriptions.get(user_id)
        if not expiry:
            return False

        return expiry > datetime.utcnow()

    def get_subscription_expiry(self, user_id: str) -> Optional[datetime]:
        """
        Returns subscription expiry date if exists.
        """
        return self._subscriptions.get(user_id)
