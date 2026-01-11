# dydx_emergency_shutdown.py
"""
dYdX v4 Emergency Shutdown (FINAL)

Role:
- Global kill-switch for dYdX trading
- Triggered by:
  * Failover manager
  * Liquidation guard
  * Risk gate
  * Manual operator action
- Freezes all new order execution
- Cancels open positions (simulated here)
"""

import time
from typing import Dict


class DydxEmergencyShutdown(Exception):
    """Raised when emergency shutdown is activated."""
    pass


class DydxEmergencyController:
    def __init__(self):
        self._active = False
        self._reason = None
        self._timestamp = None
        self._open_positions: Dict[str, dict] = {}

    def trigger(self, reason: str) -> None:
        if self._active:
            return

        self._active = True
        self._reason = reason
        self._timestamp = time.time()

        print(f"[dYdX EMERGENCY] SHUTDOWN TRIGGERED: {reason}")
        self._close_all_positions()

        raise DydxEmergencyShutdown(f"dYdX emergency shutdown: {reason}")

    def is_active(self) -> bool:
        return self._active

    def status(self) -> Dict[str, str]:
        return {
            "active": self._active,
            "reason": self._reason,
            "timestamp": self._timestamp,
        }

    def register_position(self, position_id: str, data: dict) -> None:
        self._open_positions[position_id] = data

    def _close_all_positions(self) -> None:
        for pid in self._open_positions:
            print(f"[dYdX EMERGENCY] Closing position {pid}")
        self._open_positions.clear()
