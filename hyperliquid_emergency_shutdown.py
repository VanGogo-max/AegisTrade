# hyperliquid_emergency_shutdown.py
"""
Hyperliquid Emergency Shutdown (FINAL)

Role:
- Global kill-switch for Hyperliquid trading
- Immediately blocks all new orders on:
    - repeated execution failures
    - liquidation cascade
    - API instability
    - signer compromise
    - risk engine hard-stop
- Requires manual operator reset to resume
"""

import time
from typing import Dict, Any


class HyperliquidEmergencyActive(Exception):
    pass


class HyperliquidEmergencyShutdown:
    def __init__(self):
        self._active = False
        self._reason = None
        self._triggered_at = None

    def trigger(self, reason: str) -> None:
        if not self._active:
            self._active = True
            self._reason = reason
            self._triggered_at = int(time.time())

    def clear(self) -> None:
        self._active = False
        self._reason = None
        self._triggered_at = None

    def assert_not_active(self) -> None:
        if self._active:
            raise HyperliquidEmergencyActive(
                f"HYPERLIQUID EMERGENCY SHUTDOWN | reason={self._reason} | at={self._triggered_at}"
            )

    def status(self) -> Dict[str, Any]:
        return {
            "active": self._active,
            "reason": self._reason,
            "triggered_at": self._triggered_at,
        }
