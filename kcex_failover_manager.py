# kcex_failover_manager.py
"""
Responsibility:
- Handle failover logic for KCEX
- Detect adapter outages and switch to safe mode
"""

class KCEXFailoverManager:
    def __init__(self):
        self._healthy = True
        self._last_error = None

    def mark_failure(self, error: Exception):
        self._healthy = False
        self._last_error = str(error)

    def mark_recovered(self):
        self._healthy = True
        self._last_error = None

    def is_healthy(self) -> bool:
        return self._healthy

    def status(self) -> dict:
        return {
            "exchange": "KCEX",
            "healthy": self._healthy,
            "last_error": self._last_error,
        }
