# apex_emergency_shutdown.py
"""
Apex Emergency Shutdown (FINAL)

Responsibility:
- Global hard kill-switch for Apex trading
- Immediately blocks:
    - new orders
    - position increases
    - leverage changes
- Allows only risk-reducing actions (close / reduce)
- No signing, no RPC, no strategy
"""

import time


class ApexEmergencyShutdown(Exception):
    pass


class ApexEmergencyController:
    def __init__(self):
        self._active = False
        self._reason = None
        self._activated_at = None

    def activate(self, reason: str) -> None:
        self._active = True
        self._reason = reason
        self._activated_at = int(time.time())
        raise ApexEmergencyShutdown(f"EMERGENCY SHUTDOWN: {reason}")

    def deactivate(self) -> None:
        self._active = False
        self._reason = None
        self._activated_at = None

    def is_active(self) -> bool:
        return self._active

    def assert_trading_allowed(self, action: str) -> None:
        """
        Blocks all actions except risk-reducing ones during emergency.
        Allowed during shutdown: CLOSE, REDUCE
        """
        if not self._active:
            return

        if action.upper() not in ("CLOSE", "REDUCE"):
            raise ApexEmergencyShutdown(
                f"Apex emergency active since {self._activated_at}, "
                f"blocked action: {action}, reason: {self._reason}"
            )
