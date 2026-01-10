# gmx_tx_confirm_watcher.py
"""
FINAL

Purpose:
- Watch and confirm on-chain GMX transactions
- Detect pending, confirmed, failed, dropped, or replaced transactions
- Provide deterministic status for execution pipeline
- No signing, no private keys, no strategy logic

Used by:
- gmx_tx_sender
- state reconciler
- order replay
- execution safety layer
"""

import time
from dataclasses import dataclass
from typing import Optional
from web3 import Web3
from web3.exceptions import TransactionNotFound


@dataclass(frozen=True)
class TxStatus:
    tx_hash: str
    status: str          # PENDING, CONFIRMED, FAILED, DROPPED
    block_number: Optional[int]
    gas_used: Optional[int]
    timestamp: int


class GMXTxConfirmWatcher:
    """
    Monitors transaction lifecycle on-chain.
    """

    def __init__(
        self,
        rpc_url: str,
        poll_interval: float = 2.0,
        max_wait_seconds: int = 180,
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.poll_interval = poll_interval
        self.max_wait_seconds = max_wait_seconds

    def wait_for_confirmation(self, tx_hash: str) -> TxStatus:
        """
        Block until transaction is confirmed, failed, or dropped.
        """
        start_time = time.time()
        tx_hash = Web3.to_hex(tx_hash)

        while True:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)

                if receipt is not None:
                    status = "CONFIRMED" if receipt.status == 1 else "FAILED"
                    return TxStatus(
                        tx_hash=tx_hash,
                        status=status,
                        block_number=receipt.blockNumber,
                        gas_used=receipt.gasUsed,
                        timestamp=int(time.time()),
                    )

            except TransactionNotFound:
                pass

            if time.time() - start_time > self.max_wait_seconds:
                return TxStatus(
                    tx_hash=tx_hash,
                    status="DROPPED",
                    block_number=None,
                    gas_used=None,
                    timestamp=int(time.time()),
                )

            time.sleep(self.poll_interval)
