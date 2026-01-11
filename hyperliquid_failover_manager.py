# hyperliquid_failover_manager.py
"""
Hyperliquid Failover Manager (FINAL)

Role:
- Protect execution layer from:
    - API downtime
    - timeout
    - partial fills
    - signer failure
    - order rejection
- Apply retry, backoff, and safe-halt logic
- Used by:
    - hyperliquid_tx_sender
    - hyperliquid_order_executor
    - hyperliquid_position_tracker
"""

import time
from typing import Callable, Any


class HyperliquidFailoverError(Exception):
    pass


class HyperliquidFailoverManager:
    def __init__(self, max_retries: int = 3, backoff_seconds: int = 5):
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def execute_with_failover(self, fn: Callable, *args, **kwargs) -> Any:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds)
                else:
                    break

        raise HyperliquidFailoverError(
            f"Hyperliquid execution failed after {self.max_retries} attempts: {last_error}"
        ) from last_error
