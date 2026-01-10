# gmx_account_state.py
"""
FINAL

Purpose:
- Unified on-chain account state for GMX
- Aggregates balances, margin, positions, PnL, liquidation risk
- Pure read-only, no signing, no execution
- Deterministic snapshot used by:
  - Risk engine
  - Liquidation guard
  - Execution preflight
  - State reconciler

Sources:
- GMX Vault
- GMX PositionRouter
- https://docs.gmx.io
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from web3 import Web3

from gmx_position_fetcher import GMXPosition, GMXPositionFetcher


@dataclass(frozen=True)
class GMXAccountState:
    wallet: str
    collateral_usd: float
    total_position_size_usd: float
    unrealized_pnl_usd: float
    leverage: float
    margin_ratio: float
    liquidation_risk: float
    positions: List[GMXPosition]
    block_number: int


class GMXAccountStateReader:
    """
    Builds a full risk-aware snapshot of a GMX trading account.
    """

    def __init__(
        self,
        rpc_url: str,
        vault_address: str,
        vault_abi: list,
        price_feed_fn,
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.position_fetcher = GMXPositionFetcher(
            rpc_url=rpc_url,
            vault_address=vault_address,
            vault_abi=vault_abi,
        )
        self.price_feed_fn = price_feed_fn

    def load(self, wallet: str) -> GMXAccountState:
        wallet = Web3.to_checksum_address(wallet)
        block = self.w3.eth.block_number

        positions = self.position_fetcher.fetch_positions(wallet)

        total_collateral = sum(p.collateral_usd for p in positions)
        total_size = sum(p.size_usd for p in positions)
        total_pnl = sum(p.unrealized_pnl for p in positions)

        leverage = (total_size / total_collateral) if total_collateral > 0 else 0
        margin_ratio = (total_collateral / total_size) if total_size > 0 else 1

        liquidation_risk = self._compute_liquidation_risk(positions)

        return GMXAccountState(
            wallet=wallet,
            collateral_usd=total_collateral,
            total_position_size_usd=total_size,
            unrealized_pnl_usd=total_pnl,
            leverage=leverage,
            margin_ratio=margin_ratio,
            liquidation_risk=liquidation_risk,
            positions=positions,
            block_number=block,
        )

    def _compute_liquidation_risk(self, positions: List[GMXPosition]) -> float:
        """
        Normalized 0.0–1.0 risk score based on distance to liquidation.
        """
        if not positions:
            return 0.0

        risks = []
        for p in positions:
            mark_price = self.price_feed_fn(p.market)
            distance = abs(mark_price - p.liquidation_price) / mark_price
            risk = max(0.0, 1.0 - distance * 5)  # heuristic scaling
            risks.append(min(1.0, risk))

        return max(risks)
