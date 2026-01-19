# subscription_manager.py
"""
Subscription Manager

Role:
- Enforces monthly subscription (USDT on Polygon by default)
- Verifies on-chain payment to APP_FEE_WALLET
- Applies referral discounts via ReferralProgram
- Blocks CoreEngine start if subscription is invalid
"""

from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

# You already have this logic
from referral_program import ReferralProgram, ReferralRule


class SubscriptionError(Exception):
    pass


class SubscriptionManager:
    def __init__(
        self,
        fee_wallet: str,
        base_price_usdt: float,
        period_days: int,
        referral_rule: Optional[ReferralRule] = None,
        chain: str = "POLYGON",
        token: str = "USDT",
        payment_checker=None,  # injected on-chain checker
    ):
        self.fee_wallet = fee_wallet
        self.base_price_usdt = base_price_usdt
        self.period_days = period_days
        self.chain = chain
        self.token = token

        self.referral = ReferralProgram(referral_rule) if referral_rule else None
        self.payment_checker = payment_checker

        self.active_until: Optional[datetime] = None
        self.last_tx_hash: Optional[str] = None

    # ----------------------------
    # Price with referral
    # ----------------------------
    def current_price(self) -> float:
        if self.referral:
            return self.referral.current_price()
        return self.base_price_usdt

    # ----------------------------
    # Verify on-chain payment
    # ----------------------------
    def verify_payment(self, user_wallet: str) -> bool:
        if not self.payment_checker:
            raise SubscriptionError("No on-chain payment checker configured")

        price = self.current_price()
        tx = self.payment_checker.find_payment(
            from_address=user_wallet,
            to_address=self.fee_wallet,
            amount_usdt=price,
            token=self.token,
            chain=self.chain,
        )

        if not tx:
            logger.warning("❌ Subscription payment not found on-chain")
            return False

        self.last_tx_hash = tx["tx_hash"]
        self.active_until = datetime.utcnow() + timedelta(days=self.period_days)

        if self.referral:
            self.referral.apply()

        logger.info(
            f"✅ Subscription activated: {price} {self.token} paid, "
            f"valid until {self.active_until.isoformat()}, tx={self.last_tx_hash}"
        )
        return True

    # ----------------------------
    # Access control
    # ----------------------------
    def is_active(self) -> bool:
        if not self.active_until:
            return False
        return datetime.utcnow() < self.active_until

    def require_active_subscription(self):
        if not self.is_active():
            raise SubscriptionError("Active subscription required to run the system")

    # ----------------------------
    # Info
    # ----------------------------
    def status(self) -> dict:
        return {
            "active": self.is_active(),
            "active_until": self.active_until.isoformat() if self.active_until else None,
            "price_usdt": self.current_price(),
            "chain": self.chain,
            "token": self.token,
            "fee_wallet": self.fee_wallet,
            "last_tx_hash": self.last_tx_hash,
        }
