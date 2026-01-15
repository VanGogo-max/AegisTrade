# gmx_gas_optimizer.py

import time
from typing import Dict
from web3 import Web3


class GMXGasOptimizer:
    """
    Intelligent gas price optimizer for GMX transactions (EIP-1559).
    """

    def __init__(
        self,
        web3: Web3,
        max_gas_gwei: float = 300,
        min_priority_gwei: float = 1.5,
        urgency_multiplier: float = 1.0,
        cache_ttl: int = 10
    ):
        self.web3 = web3
        self.max_gas_gwei = max_gas_gwei
        self.min_priority_gwei = min_priority_gwei
        self.urgency_multiplier = urgency_multiplier
        self.cache_ttl = cache_ttl

        self._last_fetch_time = 0
        self._cached_fees = None

    def _fetch_base_fee(self) -> int:
        block = self.web3.eth.get_block("latest")
        return block["baseFeePerGas"]

    def _estimate_priority_fee(self) -> int:
        try:
            priority = self.web3.eth.max_priority_fee
        except Exception:
            priority = self.web3.to_wei(self.min_priority_gwei, "gwei")
        return priority

    def _apply_ceiling(self, value_wei: int) -> int:
        max_wei = self.web3.to_wei(self.max_gas_gwei, "gwei")
        return min(value_wei, max_wei)

    def _calculate_fees(self) -> Dict[str, int]:
        base_fee = self._fetch_base_fee()
        priority_fee = self._estimate_priority_fee()

        priority_fee = int(priority_fee * self.urgency_multiplier)
        max_fee = int((base_fee * 2 + priority_fee) * self.urgency_multiplier)

        priority_fee = self._apply_ceiling(priority_fee)
        max_fee = self._apply_ceiling(max_fee)

        return {
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee
        }

    def get_optimized_fees(self, force_refresh: bool = False) -> Dict[str, int]:
        now = time.time()

        if (
            not force_refresh
            and self._cached_fees
            and now - self._last_fetch_time < self.cache_ttl
        ):
            return self._cached_fees

        fees = self._calculate_fees()
        self._cached_fees = fees
        self._last_fetch_time = now

        return fees

    def emergency_boost(self, multiplier: float = 2.0) -> Dict[str, int]:
        original = self.urgency_multiplier
        self.urgency_multiplier *= multiplier
        boosted = self._calculate_fees()
        self.urgency_multiplier = original
        return boosted
