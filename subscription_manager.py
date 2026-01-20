# subscription_manager.py
"""
Subscription Manager (On-Chain, Non-Custodial)

- Проверява USDT плащания на Polygon към SUBSCRIPTION_FEE_WALLET
- Цена и параметри се четат от .env
- Поддържа:
  - месечен абонамент
  - grace period
  - реферална отстъпка (чрез ReferralProgram)
  - блокиране на търговия без активен абонамент
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict

from onchain_payment_checker import OnChainPaymentChecker
from referral_program import ReferralProgram, ReferralRule


class SubscriptionManager:
    def __init__(self):
        self.price_usdt = float(os.getenv("SUBSCRIPTION_PRICE_USDT", "5"))
        self.period_days = int(os.getenv("SUBSCRIPTION_PERIOD_DAYS", "30"))
        self.grace_hours = int(os.getenv("SUBSCRIPTION_GRACE_PERIOD_HOURS", "24"))
        self.fee_wallet = os.getenv("SUBSCRIPTION_FEE_WALLET")
        self.chain = os.getenv("SUBSCRIPTION_CHAIN", "POLYGON")
        self.token = os.getenv("SUBSCRIPTION_TOKEN", "USDT")

        rpc = os.getenv("POLYGON_RPC_URL")
        usdt_contract = os.getenv("USDT_POLYGON_ADDRESS")

        self.payment_checker = OnChainPaymentChecker(rpc, usdt_contract)

        # Referral
        discount = float(os.getenv("REFERRAL_DISCOUNT_PERCENT", "0"))
        max_uses = os.getenv("REFERRAL_MAX_USES")
        max_uses = int(max_uses) if max_uses else None

        self.referral_program = ReferralProgram(
            ReferralRule(discount_percent=discount, max_uses=max_uses)
        )

        self._active_until: Optional[datetime] = None

    def required_payment_amount(self) -> float:
        return self.referral_program.current_price()

    def check_and_activate(self, user_wallet: str) -> Optional[Dict]:
        amount = self.required_payment_amount()

        payment = self.payment_checker.find_payment(
            from_address=user_wallet,
            to_address=self.fee_wallet,
            amount_usdt=amount,
            token=self.token,
            chain=self.chain,
        )

        if not payment:
            return None

        self.referral_program.apply()
        self._active_until = datetime.utcnow() + timedelta(days=self.period_days)

        return {
            "status": "ACTIVE",
            "paid_amount": amount,
            "valid_until": self._active_until.isoformat(),
            "tx_hash": payment["tx_hash"],
        }

    def is_active(self) -> bool:
        if not self._active_until:
            return False

        if datetime.utcnow() <= self._active_until:
            return True

        # Grace period
        grace_limit = self._active_until + timedelta(hours=self.grace_hours)
        return datetime.utcnow() <= grace_limit

    def block_trading_if_inactive(self):
        if not self.is_active():
            raise PermissionError("Subscription inactive. Trading is blocked.")
