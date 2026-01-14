# gmx_nonce_manager.py
"""
GMX Nonce Manager (FINAL)

Role:
- Deterministic nonce tracking per wallet
- Prevents nonce collisions in parallel tx sending
- Supports local cache + on-chain sync
"""

import threading
from typing import Dict

from gmx_rpc_client import GMXRPCClient


class NonceSyncError(Exception):
    pass


class GMXNonceManager:
    def __init__(self, rpc_client: GMXRPCClient, address: str):
        self.rpc = rpc_client
        self.address = address
        self._lock = threading.Lock()
        self._local_nonce: int | None = None

    def sync(self) -> int:
        """
        Sync nonce from chain.
        """
        try:
            nonce = self.rpc.get_nonce(self.address)
        except Exception as exc:
            raise NonceSyncError("Failed to fetch nonce from chain") from exc

        with self._lock:
            self._local_nonce = nonce
        return nonce

    def next(self) -> int:
        """
        Get next usable nonce (thread-safe).
        """
        with self._lock:
            if self._local_nonce is None:
                self._local_nonce = self.rpc.get_nonce(self.address)
            else:
                self._local_nonce += 1

            return self._local_nonce

    def current(self) -> int:
        with self._lock:
            if self._local_nonce is None:
                return self.rpc.get_nonce(self.address)
            return self._local_nonce
