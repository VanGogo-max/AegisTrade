"""
gmx_tx_sender.py — FINAL

GMX Transaction Sender.

Purpose:
- Send a signed Ethereum transaction to the blockchain via RPC
- Return transaction hash
- No signing
- No strategy or execution logic

Design guarantees:
- Single responsibility
- Deterministic behavior
"""

from typing import Dict, Any
from web3 import Web3


class GMXTxSenderError(Exception):
    pass


class GMXTxSender:
    """
    Sends signed GMX transactions to the blockchain.
    """

    def __init__(self, rpc_url: str):
        if not rpc_url:
            raise GMXTxSenderError("RPC URL is required")

        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise GMXTxSenderError("Failed to connect to RPC endpoint")

    def send(self, signed_tx: Dict[str, Any]) -> str:
        """
        Send signed transaction to the blockchain.

        Expects:
            signed_tx['raw_transaction']

        Returns:
            transaction hash (hex str)
        """
        raw_tx = signed_tx.get("raw_transaction")
        if not raw_tx:
            raise GMXTxSenderError("Signed transaction missing raw_transaction")

        try:
            tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        except Exception as exc:
            raise GMXTxSenderError(f"Transaction send failed: {exc}")

        return tx_hash.hex()
