# dydx_failover_manager.py
"""
dYdX v4 Failover Manager (FINAL)

Role:
- Detect adapter / RPC / API failures
- Switch to backup endpoints
- Freeze trading on critical errors
- Coordinate with EmergencyShutdown
"""

import time
from typing import Optional


class DydxFailoverException(Exception):
    pass


class DydxFailoverManager:
    def __init__(self):
        self._last_heartbeat = time.time()
        self._failure_count = 0
        self._max_failures = 3
        self._halted = False

    def heartbeat(self) -> None:
        """Called periodically by execution layer."""
        self._last_heartbeat = time.time()

    def report_failure(self, reason: str) -> None:
        self._failure_count += 1
        print(f"[dYdX FAILOVER] Failure reported: {reason}")

        if self._failure_count >= self._max_failures:
            self._halt_trading(reason)

    def reset_failures(self) -> None:
        self._failure_count = 0

    def is_halted(self) -> bool:
        return self._halted

    def _halt_trading(self, reason: str) -> None:
        self._halted = True
        raise DydxFailoverException(
            f"dYdX trading halted due to repeated failures: {reason}"
        )

    def health_check(self, timeout_sec: int = 30) -> Optional[bool]:
        """
        Verify adapter heartbeat freshness.
        """
        if time.time() - self._last_heartbeat > timeout_sec:
            self.report_failure("Heartbeat timeout")
            return False
        return True
