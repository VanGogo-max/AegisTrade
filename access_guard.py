a
"""
access_guard.py

Единна точка за контрол на достъпа (permission / policy layer).

Отговорност:
- Проверява ДАЛИ даден user има право да извърши действие
- НЕ управлява абонаменти
- НЕ извършва плащания
- НЕ съдържа side-effects

Зависи от:
- subscription_manager.py
"""

from typing import Tuple, Optional

from subscription_manager import SubscriptionManager


class AccessGuard:
    """
    Central access control layer.
    Всички ботове, router-и и API-та трябва да питат ТУК.
    """

    def __init__(self, subscription_manager: SubscriptionManager):
        self.subscription_manager = subscription_manager

    # ========= GENERIC =========

    def has_active_subscription(self, user_id: str) -> Tuple[bool, str]:
        """
        Проверка за активен абонамент.
        """
        active = self.subscription_manager.is_active(user_id)

        if not active:
            return False, "Subscription is not active"

        return True, "OK"

    def is_admin(self, user_id: str) -> Tuple[bool, str]:
        """
        Проверка за администраторски достъп.
        """
        if self.subscription_manager.is_admin(user_id):
            return True, "OK"

        return False, "Admin access required"

    # ========= FEATURE-LEVEL =========

    def can_trade_spot(self, user_id: str) -> Tuple[bool, str]:
        """
        Право за spot trading.
        """
        return self.has_active_subscription(user_id)

    def can_trade_futures(self, user_id: str) -> Tuple[bool, str]:
        """
        Право за futures trading.
        Може лесно да се разшири с допълнителни условия.
        """
        active, reason = self.has_active_subscription(user_id)
        if not active:
            return False, reason

        if not self.subscription_manager.has_futures_enabled(user_id):
            return False, "Futures trading not enabled for this subscription"

        return True, "OK"

    def can_run_bot(self, user_id: str) -> Tuple[bool, str]:
        """
        Право за стартиране на ботове.
        """
        return self.has_active_subscription(user_id)

    def can_access_admin_panel(self, user_id: str) -> Tuple[bool, str]:
        """
        Достъп до админ панел.
        """
        return self.is_admin(user_id)

    # ========= SAFE DEFAULT =========

    def deny_all(self, reason: Optional[str] = None) -> Tuple[bool, str]:
        """
        Fail-safe отказ.
        """
        return False, reason or "Access denied"
