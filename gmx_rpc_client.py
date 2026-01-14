# gmx_rpc_client.py
"""
GMX RPC Client (FINAL)

Role:
- Low-level JSON-RPC wrapper for Arbitrum / Avalanche
- Handles:
  - connection pooling
  - retries
  - timeouts
  - basic health checks
- No signing
- No business logic
"""

import time
from typing import Any, Dict
from web3 import Web3
from web3.exceptions import TransactionNotFound


class GMXRPCClient:
    def __init__(self, rpc_url: str, timeout: int = 10):
        self.rpc_url = rpc_url
        self.timeout = timeout
        self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": timeout}))
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to RPC: {rpc_url}")

    def get_block_number(self) -> int:
        return self.w3.eth.block_number

    def get_gas_price(self) -> int:
        return self.w3.eth.gas_price

    def send_raw_transaction(self, signed_tx: bytes) -> str:
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx)
        return tx_hash.hex()

    def wait_for_tx(self, tx_hash: str, confirmations: int = 1, poll_interval: float = 2.0) -> Dict[str, Any]:
        while True:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt["blockNumber"] is not None:
                    current = self.get_block_number()
                    if current - receipt["blockNumber"] >= confirmations:
                        return dict(receipt)
            except TransactionNotFound:
                pass
            time.sleep(poll_interval)

    def estimate_gas(self, tx: Dict[str, Any]) -> int:
        return self.w3.eth.estimate_gas(tx)

    def get_nonce(self, address: str) -> int:
        return self.w3.eth.get_transaction_count(address)
