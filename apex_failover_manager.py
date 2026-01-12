# apex_failover_manager.py
"""
Apex Failover Manager (FINAL)

Responsibility:
- Detect repeated execution / RPC / adapter failures
- Temporarily disable Apex trading
- Provide cooldown-based auto-recovery

No strategy.
No signing.
No order building.
"""

import time


class ApexFailoverError(Exception):
    pass


class ApexFailoverManager:
    def __init__(self, max_failures: int = 3, cooldown_seconds: int = 60):
        self.max_failures = max_failures
        self.cooldown_seconds = cooldown_seconds
        self._failure_count = 0
        self._last_failure_ts = None
        self._disabled = False

    def record_failure(self, reason: str) -> None:
        self._failure_count += 1
        self._last_failure_ts = time.time()

        if self._failure_count >= self.max_failures:
            self._disabled = True
            raise ApexFailoverError(
                f"Apex disabled after {self._failure_count} failures: {reason}"
            )

    def record_success(self) -> None:
        self._failure_count = 0
        self._last_failure_ts = None
        self._disabled = False

    def is_enabled(self) -> bool:
        if not self._disabled:
            return True

        if self._last_failure_ts is None:
            return False

        if time.time() - self._last_failure_ts > self.cooldown_seconds:
            self._disabled = False
            self._failure_count = 0
            return True

        return False

    def assert_available(self) -> None:
        if not self.is_enabled():
            raise ApexFailoverError("Apex is in failover cooldown state")
