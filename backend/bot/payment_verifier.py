"""
backend/payments/payment_verifier.py
AegisTrade — Polygon USDT subscription verifier

Reads on-chain subscription state from AegisPayment contract.
No private keys needed — read-only calls via public RPC.

Usage:
    verifier = PaymentVerifier()
    ok = await verifier.is_active("0xUserAddress")
    plan = await verifier.get_plan("0xUserAddress")
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from loguru import logger
from web3 import AsyncWeb3
from web3.middleware import ExtraDataToPOAMiddleware

# ── Config ─────────────────────────────────────────────────────────────────

POLYGON_RPC      = "https://polygon-rpc.com"           # Free public RPC
CONTRACT_ADDRESS = ""                                   # Fill after deploy
USDT_POLYGON     = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"

# Minimal ABI — only what we need
CONTRACT_ABI = [
    {
        "name": "isActive",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "userPlan",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [{"name": "", "type": "uint8"}],
    },
    {
        "name": "planName",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [{"name": "", "type": "string"}],
    },
    {
        "name": "daysRemaining",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "subscriptions",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [
            {"name": "plan",       "type": "uint8"},
            {"name": "expiresAt",  "type": "uint256"},
            {"name": "referredBy", "type": "address"},
        ],
    },
    {
        "name": "referralEarnings",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "referralCount",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
]

PLAN_NAMES = {0: "None", 1: "Basic", 2: "Pro", 3: "Elite"}
PLAN_PRICES = {1: 50, 2: 100, 3: 200}  # USD


# ── Data classes ───────────────────────────────────────────────────────────

@dataclass
class SubscriptionInfo:
    address:        str
    is_active:      bool
    plan:           int
    plan_name:      str
    days_remaining: int
    referred_by:    Optional[str]
    pending_referral_usdt: float  # Unclaimed referral earnings
    referral_count: int


# ── Verifier ───────────────────────────────────────────────────────────────

class PaymentVerifier:
    """
    Async read-only verifier for AegisPayment contract on Polygon.
    Caches results for 60s to avoid hammering the RPC.
    """

    def __init__(
        self,
        rpc_url: str = POLYGON_RPC,
        contract_address: str = CONTRACT_ADDRESS,
    ):
        self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
        self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self._contract_address = contract_address
        self._contract = None
        self._cache: dict[str, tuple[SubscriptionInfo, float]] = {}
        self._cache_ttl = 60.0  # seconds

    def _get_contract(self):
        if not self._contract_address:
            raise RuntimeError(
                "CONTRACT_ADDRESS not set. Deploy AegisPayment.sol first."
            )
        if self._contract is None:
            self._contract = self._w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(self._contract_address),
                abi=CONTRACT_ABI,
            )
        return self._contract

    async def get_subscription(self, user_address: str) -> SubscriptionInfo:
        """Full subscription info for a wallet address."""
        import time

        addr = AsyncWeb3.to_checksum_address(user_address)

        # Cache hit?
        if addr in self._cache:
            info, ts = self._cache[addr]
            if time.monotonic() - ts < self._cache_ttl:
                return info

        contract = self._get_contract()

        try:
            # Parallel calls
            active, plan, days, sub, ref_earnings, ref_count = await asyncio.gather(
                contract.functions.isActive(addr).call(),
                contract.functions.userPlan(addr).call(),
                contract.functions.daysRemaining(addr).call(),
                contract.functions.subscriptions(addr).call(),
                contract.functions.referralEarnings(addr).call(),
                contract.functions.referralCount(addr).call(),
            )

            referred_by = sub[2] if sub[2] != "0x0000000000000000000000000000000000000000" else None
            pending_usdt = ref_earnings / 1e6  # USDT has 6 decimals on Polygon

            info = SubscriptionInfo(
                address=addr,
                is_active=active,
                plan=plan,
                plan_name=PLAN_NAMES.get(plan, "Unknown"),
                days_remaining=int(days),
                referred_by=referred_by,
                pending_referral_usdt=pending_usdt,
                referral_count=int(ref_count),
            )

            self._cache[addr] = (info, time.monotonic())
            return info

        except Exception as e:
            logger.error(f"PaymentVerifier error for {addr}: {e}")
            # Return inactive stub — fail safe, never crash the bot
            return SubscriptionInfo(
                address=addr,
                is_active=False,
                plan=0,
                plan_name="None",
                days_remaining=0,
                referred_by=None,
                pending_referral_usdt=0.0,
                referral_count=0,
            )

    async def is_active(self, user_address: str) -> bool:
        info = await self.get_subscription(user_address)
        return info.is_active

    async def get_plan(self, user_address: str) -> int:
        info = await self.get_subscription(user_address)
        return info.plan

    def invalidate_cache(self, user_address: str) -> None:
        addr = AsyncWeb3.to_checksum_address(user_address)
        self._cache.pop(addr, None)


# ── Guard decorator ────────────────────────────────────────────────────────

def require_subscription(min_plan: int = 1):
    """
    Decorator for async bot methods that require an active subscription.

    Usage:
        @require_subscription(min_plan=2)  # Requires Pro or Elite
        async def start_trading(self, user_address: str):
            ...
    """
    def decorator(func):
        async def wrapper(self, user_address: str, *args, **kwargs):
            verifier: PaymentVerifier = getattr(self, "payment_verifier", None)
            if verifier is None:
                logger.warning("No payment_verifier on instance — skipping check")
                return await func(self, user_address, *args, **kwargs)

            info = await verifier.get_subscription(user_address)

            if not info.is_active:
                logger.warning(f"[PAYMENT] {user_address} — no active subscription")
                raise PermissionError("Active subscription required to use AegisTrade.")

            if info.plan < min_plan:
                needed = PLAN_NAMES.get(min_plan, str(min_plan))
                logger.warning(
                    f"[PAYMENT] {user_address} plan={info.plan} < required={min_plan}"
                )
                raise PermissionError(
                    f"This feature requires {needed} plan or higher. "
                    f"Current: {info.plan_name}."
                )

            logger.debug(
                f"[PAYMENT] {user_address} ✓ plan={info.plan_name} "
                f"days_left={info.days_remaining}"
            )
            return await func(self, user_address, *args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# ── Quick CLI test ─────────────────────────────────────────────────────────

async def _test():
    verifier = PaymentVerifier()
    test_addr = "0x0000000000000000000000000000000000000001"
    info = await verifier.get_subscription(test_addr)
    logger.info(f"Subscription info: {info}")


if __name__ == "__main__":
    asyncio.run(_test())
