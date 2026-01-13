# exchange_health_monitor.py
"""
Responsibility:
- Global health monitor for all registered exchanges
- Detects connectivity issues, degraded state, and outages
- Provides unified status for ExecutionEngine and FailoverManagers
"""

import time
from typing import Dict


class ExchangeHealthMonitor:
    def __init__(self):
        self._status: Dict[str, dict] = {}

    def report_ok(self, exchange: str):
        self._status[exchange] = {
            "state": "OK",
            "last_check": int(time.time()),
            "error": None,
        }

    def report_degraded(self, exchange: str, error: str):
        self._status[exchange] = {
            "state": "DEGRADED",
            "last_check": int(time.time()),
            "error": error,
        }

    def report_down(self, exchange: str, error: str):
        self._status[exchange] = {
            "state": "DOWN",
            "last_check": int(time.time()),
            "error": error,
        }

    def is_healthy(self, exchange: str) -> bool:
        return (
            exchange in self._status
            and self._status[exchange]["state"] == "OK"
        )

    def snapshot(self) -> Dict[str, dict]:
        return self._status.copy()
