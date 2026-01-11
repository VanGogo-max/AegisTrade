# dydx_position_tracker.py
"""
dYdX v4 Position Tracker (FINAL)

Role:
- Track lifecycle of all dYdX v4 positions
- Maintain authoritative in-memory state
- Detect:
    - opens
    - increases
    - partial closes
    - full closes
    - liquidations
- Provide clean state for:
    - risk engine
    - liquidation guard
    - state reconciler
    - strategy layer
"""

from typing import Dict, Any
import time


class DydxPositionNotFound(Exception):
    pass


class DydxPositionTracker:
    def __init__(self):
        self._positions: Dict[str, Dict[str, Any]] = {}

    def sync_from_exchange(self, positions: Dict[str, Dict[str, Any]]) -> None:
        """
        Replace local state with fresh snapshot from dYdX API.
        """
        self._positions = positions.copy()

    def register_open(self, position_id: str, data: Dict[str, Any]) -> None:
        self._positions[position_id] = {
            **data,
            "status": "OPEN",
            "last_update": int(time.time()),
        }

    def register_increase(self, position_id: str, delta_usd: float) -> None:
        pos = self._get(position_id)
        pos["size_usd"] += delta_usd
        pos["last_update"] = int(time.time())

    def register_decrease(self, position_id: str, delta_usd: float) -> None:
        pos = self._get(position_id)
        pos["size_usd"] -= delta_usd
        pos["last_update"] = int(time.time())
        if pos["size_usd"] <= 0:
            pos["status"] = "CLOSED"

    def register_liquidation(self, position_id: str) -> None:
        pos = self._get(position_id)
        pos["status"] = "LIQUIDATED"
        pos["last_update"] = int(time.time())

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return self._positions.copy()

    def get_open(self) -> Dict[str, Dict[str, Any]]:
        return {k: v for k, v in self._positions.items() if v["status"] == "OPEN"}

    def _get(self, position_id: str) -> Dict[str, Any]:
        if position_id not in self._positions:
            raise DydxPositionNotFound(position_id)
        return self._positions[position_id]
