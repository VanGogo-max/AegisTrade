# gmx_liquidity_monitor.py

import time
from typing import Dict, List
from web3 import Web3


class GMXLiquidityMonitor:
    """
    Monitors liquidity, open interest and funding rates for GMX perpetuals.
    """

    def __init__(
        self,
        web3: Web3,
        pool_addresses: List[str],
        oi_threshold: float = 1_000_000,  # USD
        funding_threshold: float = 0.05,  # 5%
        check_interval: int = 10  # seconds
    ):
        self.web3 = web3
        self.pool_addresses = [addr.lower() for addr in pool_addresses]
        self.oi_threshold = oi_threshold
        self.funding_threshold = funding_threshold
        self.check_interval = check_interval

        self.recent_liquidity: Dict[str, float] = {}
        self.recent_oi: Dict[str, float] = {}
        self.recent_funding: Dict[str, float] = {}

    def _fetch_pool_liquidity(self, pool_address: str) -> float:
        """
        Fetch pool liquidity (USD) from on-chain data or oracle.
        Placeholder – replace with actual contract call.
        """
        # Example:
        # return pool_contract.getAvailableLiquidity()
        return 1_000_000  # dummy

    def _fetch_pool_oi(self, pool_address: str) -> float:
        """
        Fetch open interest (USD)
        """
        return 800_000  # dummy

    def _fetch_funding_rate(self, pool_address: str) -> float:
        """
        Fetch latest funding rate
        """
        return 0.02  # dummy 2%

    def update_metrics(self):
        for pool in self.pool_addresses:
            liquidity = self._fetch_pool_liquidity(pool)
            oi = self._fetch_pool_oi(pool)
            funding = self._fetch_funding_rate(pool)

            self.recent_liquidity[pool] = liquidity
            self.recent_oi[pool] = oi
            self.recent_funding[pool] = funding

    def evaluate_risk(self, pool_address: str) -> Dict[str, object]:
        pool = pool_address.lower()
        liquidity = self.recent_liquidity.get(pool, 0)
        oi = self.recent_oi.get(pool, 0)
        funding = self.recent_funding.get(pool, 0)

        risk_flags = {
            "low_liquidity": liquidity < 500_000,
            "high_oi": oi > self.oi_threshold,
            "high_funding": abs(funding) > self.funding_threshold
        }

        overall_risk = any(risk_flags.values())

        return {
            "liquidity": liquidity,
            "open_interest": oi,
            "funding_rate": funding,
            "risk_flags": risk_flags,
            "overall_risk": overall_risk
        }

    def monitor_loop(self):
        """
        Continuous monitoring (optional, can run in background thread)
        """
        while True:
            self.update_metrics()
            time.sleep(self.check_interval)
