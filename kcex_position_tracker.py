# kcex_position_tracker.py
"""
Responsibility:
- Track open positions on KCEX (simulated)
- Provide position state for risk and liquidation modules
"""

from typing import Dict


class KCEXPositionTracker:
    def __init__(self):
        # position_id -> position data
        self._positions: Dict[str, Dict] = {}

    def open_position(self, position_id: str, data: Dict):
        self._positions[position_id] = {
            **data,
            "status": "OPEN"
        }

    def close_position(self, position_id: str):
        if position_id in self._positions:
            self._positions[position_id]["status"] = "CLOSED"

    def get_position(self, position_id: str) -> Dict | None:
        return self._positions.get(position_id)

    def list_open_positions(self) -> Dict[str, Dict]:
        return {
            pid: pos for pid, pos in self._positions.items()
            if pos["status"] == "OPEN"
        }

    def is_empty(self) -> bool:
        return len(self.list_open_positions()) == 0
