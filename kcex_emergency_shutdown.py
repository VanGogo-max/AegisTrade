# kcex_emergency_shutdown.py
"""
Responsibility:
- Trigger emergency shutdown procedures for KCEX
- Block all new orders
- Cancel open positions if required
"""

class KCEXEmergencyShutdown:
    def __init__(self):
        self._shutdown_active = False
        self._reason = None

    def trigger(self, reason: str):
        self._shutdown_active = True
        self._reason = reason

    def clear(self):
        self._shutdown_active = False
        self._reason = None

    def is_active(self) -> bool:
        return self._shutdown_active

    def status(self) -> dict:
        return {
            "exchange": "KCEX",
            "shutdown": self._shutdown_active,
            "reason": self._reason,
        }
