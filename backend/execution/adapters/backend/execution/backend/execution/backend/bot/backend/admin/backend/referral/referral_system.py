"""
AegisTrade — Referral System
"""
from __future__ import annotations
import hashlib
import secrets
import time
from typing import Optional

from backend.config.config import SUBSCRIPTION_TIERS
from backend.state.state_manager import StateManager
from backend.utils.logger import get_logger

log = get_logger(__name__)


class ReferralSystem:
    def __init__(self, state: StateManager) -> None:
        self._state = state

    def generate_code(self, owner_address: str, tier: str = "basic") -> str:
        raw = f"{owner_address}-{secrets.token_hex(6)}"
        code = hashlib.sha256(raw.encode()).hexdigest()[:10].upper()
        return code

    async def register_code(
        self,
        code: str,
        owner_address: str,
        tier: str = "basic",
    ) -> dict:
        if tier not in SUBSCRIPTION_TIERS:
            raise ValueError(f"Unknown tier: {tier}")
        data = {
            "code": code,
            "owner": owner_address,
            "tier": tier,
            "created_at": time.time(),
            "uses": 0,
            "earnings_usdt": 0.0,
            "price_usdt": SUBSCRIPTION_TIERS[tier]["price_usdt"],
        }
        await self._state.add_referral(code, data)
        log.info(
            "Referral registered: %s (tier=%s owner=%s)",
            code, tier, owner_address
        )
        return data

    async def use_code(
        self, code: str, subscriber_address: str
    ) -> Optional[dict]:
        ref = self._state.get_referral(code)
        if not ref:
            log.warning("Unknown referral code: %s", code)
            return None
        ref["uses"] += 1
        ref["last_used_by"] = subscriber_address
        ref["last_used_at"] = time.time()
        reward = ref["price_usdt"] * 0.10
        ref["earnings_usdt"] = round(
            ref.get("earnings_usdt", 0) + reward, 4
        )
        await self._state.add_referral(code, ref)
        log.info(
            "Code used: %s → %s | reward=%.4f USDT",
            code, subscriber_address, reward
        )
        return ref

    def get_link(
        self, code: str, base_url: str = "https://aegistrade.app"
    ) -> str:
        return f"{base_url}/signup?ref={code}"

    def get_stats(self, code: str) -> Optional[dict]:
        return self._state.get_referral(code)

    def list_codes(self) -> dict:
        return self._state.referrals

    def subscription_tiers(self) -> dict:
        return SUBSCRIPTION_TIERS
