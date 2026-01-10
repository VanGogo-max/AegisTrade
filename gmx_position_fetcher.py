# gmx_position_fetcher.py
"""
FINAL

Purpose:
- Read-only on-chain state reader for GMX positions
- Fetches current open positions for a wallet
- No signing, no execution, no private keys
- Deterministic, side-effect free

Source of truth:
- GMX PositionRouter / Vault contracts
- https://docs.gmx.io
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from web3 import Web3


@dataclass(frozen=True)
class GMXPosition:
    market: str
    side: str
    size_usd: float
    collateral_usd: float
    entry_price: float
    leverage: float
    unrealized_pnl: float
    liquidation_price: float


class GMXPositionFetcher:
    """
    Reads live GMX positions from chain.
    """

    def __init__(self, rpc_url: str, vault_address: str, vault_abi: list):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.vault = self.w3.eth.contract(
            address=Web3.to_checksum_address(vault_address),
            abi=vault_abi
        )

    def fetch_positions(self, account: str) -> List[GMXPosition]:
        """
        Return all open positions for wallet.
        """
        account = Web3.to_checksum_address(account)

        raw_positions = self.vault.functions.getPositions(account).call()
        positions: List[GMXPosition] = []

        for p in raw_positions:
            positions.append(
                GMXPosition(
                    market=p[0],
                    side="long" if p[1] else "short",
                    size_usd=p[2] / 1e30,
                    collateral_usd=p[3] / 1e30,
                    entry_price=p[4] / 1e30,
                    leverage=(p[2] / p[3]) if p[3] > 0 else 0,
                    unrealized_pnl=p[5] / 1e30,
                    liquidation_price=p[6] / 1e30,
                )
            )

        return positions
