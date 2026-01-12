# kwenta_position_tracker.py
"""
Kwenta Position Tracker (FINAL)

Responsibility:
- Track open positions on Kwenta Perps
- Maintain local shadow state for:
    - size
    - entry price
    - leverage
    - PnL
    - liquidation price
- No execution, no signing, no RPC sending

Data source (real mode):
- Kwenta Perps subgraph / RPC
Docs:
- https://docs.kwenta.io
"""

from typing import Dict, Any
import time


class KwentaPositionTracker:
    def __init__(self):
        self._positions: Dict[str, Dict[str, Any]] = {}

    def update_position(self, account: str, market: str, data: Dict[str, Any]) -> None:
        """
        Update or insert position state.
        """
        key = f"{account}:{market}"
        self._positions[key] = {
            "account": account,
            "market": market,
            "size": data["size"],
            "side": data["side"],
            "entry_price": data["entry_price"],
            "leverage": data["leverage"],
            "liquidation_price": data.get("liquidation_price"),
            "unrealized_pnl": data.get("unrealized_pnl"),
            "last_update": int(time.time()),
        }

    def get_position(self, account: str, market: str) -> Dict[str, Any] | None:
        """
        Return tracked position or None.
        """
        return self._positions.get(f"{account}:{market}")

    def close_position(self, account: str, market: str) -> None:
        """
        Remove closed position from tracker.
        """
        self._positions.pop(f"{account}:{market}", None)

    def all_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        Snapshot of all open positions.
        """
        return dict(self._positions)
