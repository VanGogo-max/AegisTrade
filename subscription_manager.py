# subscription_manager.py
"""
Subscription Manager (Updated)

- Проверява месечен абонамент в USDT на Polygon
- Използва ReferralProgram за отстъпки
- Поддържа grace period
- Блокира CoreEngine, ако абонаментът е изтекъл
"""

import os
from datetime import datetime, timedelta
from decimal import Decimal
from loguru import logger

from referral_program import ReferralProgram, ReferralRule


class SubscriptionError(Exception):
    pass


class SubscriptionManager:
    def __init__(self, user_wallet: str, referral_rule: ReferralRule = None):
        # ENV конфигурация
        self.user_wallet = user_wallet
        self.fee_wallet = os.getenv("SUBSCRIPTION_FEE_WALLET")
        self.chain = os.getenv("SUBSCRIPTION_CHAIN", "POLYGON")
        self.token = os.getenv("SUBSCRIPTION_TOKEN", "USDT")
        self.period_days = int(os.getenv("SUBSCRIPTION_PERIOD_DAYS", 30))
        self.grace_hours = int(os.getenv("SUBSCRIPTION_GRACE_PERIOD_HOURS", 24))
        self.base_price_usdt = Decimal(os.getenv("SUBSCRIPTION_PRICE_USDT", "5"))

        self.referral = ReferralProgram(referral_rule) if referral_rule else None

        # Internal state
        self.active_until: datetime | None = None
        self.last_tx_hash: str | None = None

        # On-chain checker placeholder (трябва да се имплементира)
        self.payment_checker = None  # Например OnChainPaymentChecker()

    # --------------------------------------
    # Цена с отстъпка (реферал)
    # --------------------------------------
    def current_price(self) -> Decimal:
        if self.referral:
            return Decimal(self.referral.current_price())
        return self.base_price_usdt

    # --------------------------------------
    # Проверка на плащане
    # --------------------------------------
    def verify_payment(self) -> bool:
        if not self.payment_checker:
            raise SubscriptionError("Payment checker not configured")

        price = self.current_price()
        tx = self.payment_checker.find_payment(
            from_address=self.user_wallet,
            to_address=self.fee_wallet,
            amount_usdt=float(price),
            token=self.token,
            chain=self.chain,
        )

        if not tx:
            logger.warning(f"❌ Subscription payment of {price} {self.token} not found on-chain")
            return False

        self.last_tx_hash = tx["tx_hash"]
        self.active_until = datetime.utcnow() + timedelta(days=self.period_days)
        if self.referral:
            self.referral.apply()

        logger.info(
            f"✅ Subscription activated for {self.user_wallet}: "
            f"{price} {self.token}, valid until {self.active_until.isoformat()}, tx={self.last_tx_hash}"
        )
        return True

    # --------------------------------------
    # Статус на абонамент
    # --------------------------------------
    def is_active(self) -> bool:
        if not self.active_until:
            return False
        now = datetime.utcnow()
        # Добавя grace period
        return now < self.active_until + timedelta(hours=self.grace_hours)

    def require_active_subscription(self):
        if not self.is_active():
            raise SubscriptionError("Active subscription required to run the system")

    # --------------------------------------
    # Информация за абонамент
    # --------------------------------------
    def status(self) -> dict:
        return {
            "active": self.is_active(),
            "active_until": self.active_until.isoformat() if self.active_until else None,
            "price_usdt": float(self.current_price()),
            "chain": self.chain,
            "token": self.token,
            "fee_wallet": self.fee_wallet,
            "last_tx_hash": self.last_tx_hash,
            "referral_discount_applied": self.referral.usage_count() if self.referral else 0,
        }
