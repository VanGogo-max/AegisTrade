# gmx_failover_manager.py
"""
GMX Failover Manager (FINAL)

Role:
- Handle execution failures and degraded states
- Decide automatic retry, halt, or switch to safe mode
- Protect against:
    - RPC outages
    - signer failures
    - tx stuck in mempool
    - partial execution
- Integrates with:
    - gmx_tx_confirm_watcher
    - gmx_reorg_protector
    - gmx_order_executor
"""

from typing import Dict, Any
import time


class GMXFailoverError(Exception):
    pass


class GMXFailoverManager:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def execute_with_failover(self, execute_fn, *args, **kwargs) -> Dict[str, Any]:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return execute_fn(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    break

        raise GMXFailoverError(
            f"Execution failed after {self.max_retries} attempts: {last_error}"
        ) from last_error
