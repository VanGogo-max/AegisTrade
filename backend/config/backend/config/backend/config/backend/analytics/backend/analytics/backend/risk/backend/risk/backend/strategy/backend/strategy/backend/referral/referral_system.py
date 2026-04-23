"""
AegisTrade - Referral System
"""
from __future__ import annotations
import random
import string
from backend.utils.logger import get_logger

log = get_logger(__name__)

BASE_URL = "https://aegistrade.app/ref/"


class ReferralSystem:
    def __init__(self, state) -> None:
        self.state = state
        self._codes: dict = {}

    def generate_code(self, owner: str, tier: str = "basic") -> str:
        code = "AEGIS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return code

    async def register_code(self, code: str, owner: str, tier: str) -> dict:
        self._codes[code] = {"owner": owner, "tier": tier, "uses": 0, "earnings": 0.0}
        return self._codes[code]

    def get_link(self, code: str) -> str:
        return f"{BASE_URL}{code}"

    def list_codes(self) -> list:
        return [{"code": k, **v} for k, v in self._codes.items()]

    def subscription_tiers(self) -> dict:
        return {
            "basic": {"price_usdt": 29, "commission_pct": 10},
            "pro": {"price_usdt": 79, "commission_pct": 15},
            "elite": {"price_usdt": 149, "commission_pct": 20},
        }
