# gmx_emergency_shutdown.py
"""
GMX Emergency Shutdown (FINAL)

Role:
- Global kill-switch for the entire GMX execution system
- Hard-blocks all new trades on:
    - critical loss
    - liquidation cascade
    - chain instability
    - oracle failure
    - repeated reorgs
    - signer compromise
- Can be triggered by:
    - risk engine
    - liquidation guard
    - reorg protector
    - failover manager
- Once activated, only manual operator unlock can resume trading
"""

import time
from typing import Dict, Any


class EmergencyShutdownActive(Exception):
    pass


class GMXEmergencyShutdown:
    def __init__(self):
        self._active = False
        self._reason = None
        self._timestamp = None

    def trigger(self, reason: str) -> None:
        if not self._active:
            self._active = True
            self._reason = reason
            self._timestamp = int(time.time())

    def clear(self) -> None:
        """
        Manual operator reset only.
        """
        self._active = False
        self._reason = None
        self._timestamp = None

    def assert_not_active(self) -> None:
        if self._active:
            raise EmergencyShutdownActive(
                f"GMX EMERGENCY SHUTDOWN ACTIVE | reason={self._reason} | at={self._timestamp}"
            )

    def status(self) -> Dict[str, Any]:
        return {
            "active": self._active,
            "reason": self._reason,
            "triggered_at": self._timestamp,
        }
