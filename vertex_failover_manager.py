# vertex_failover_manager.py
"""
Vertex Failover Manager (FINAL)

Responsibility:
- Detect adapter / RPC / execution failures
- Disable Vertex temporarily after repeated faults
- Provide deterministic availability state to execution pipeline

No strategy logic.
No signing.
No transaction building.
"""

import time


class VertexFailoverError(Exception):
    pass


class VertexFailoverManager:
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
            raise VertexFailoverError(
                f"Vertex disabled after {self._failure_count} failures: {reason}"
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
            raise VertexFailoverError("Vertex is in failover cooldown state")
