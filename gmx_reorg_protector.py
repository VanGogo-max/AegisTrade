# gmx_reorg_protector.py
"""
FINAL

Purpose:
- Detect blockchain reorgs affecting GMX transactions and positions
- Verify that confirmed trades remain in canonical chain
- Trigger state re-sync and safety halt on inconsistency

No signing.
No execution.
Read-only chain verification.

Used by:
- gmx_tx_confirm_watcher
- gmx_state_reconciler
- execution safety layer
"""

from dataclasses import dataclass
from typing import Dict, Optional
from web3 import Web3


@dataclass(frozen=True)
class ReorgEvent:
    tx_hash: str
    original_block: int
    current_block: Optional[int]
    reorg_detected: bool


class GMXReorgProtector:
    """
    Protects against chain reorg by re-validating confirmed transactions.
    """

    def __init__(self, rpc_url: str, confirmation_depth: int = 20):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.confirmation_depth = confirmation_depth

    def verify_tx_finality(self, tx_hash: str, confirmed_block: int) -> ReorgEvent:
        """
        Re-check that a transaction is still in canonical chain after N blocks.
        """
        latest_block = self.w3.eth.block_number

        if latest_block - confirmed_block < self.confirmation_depth:
            # Not deep enough yet, consider temporarily safe
            return ReorgEvent(
                tx_hash=tx_hash,
                original_block=confirmed_block,
                current_block=confirmed_block,
                reorg_detected=False,
            )

        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            current_block = receipt.blockNumber

            reorg = current_block != confirmed_block

            return ReorgEvent(
                tx_hash=tx_hash,
                original_block=confirmed_block,
                current_block=current_block,
                reorg_detected=reorg,
            )

        except Exception:
            # Receipt missing after being confirmed → strong reorg signal
            return ReorgEvent(
                tx_hash=tx_hash,
                original_block=confirmed_block,
                current_block=None,
                reorg_detected=True,
            )
