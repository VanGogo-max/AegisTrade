# vertex_position_tracker.py
"""
Vertex Position Tracker (FINAL)

Responsibility:
- Maintain shadow state of open positions on Vertex
- Track size, side, entry price, leverage, PnL, liquidation level
- No execution, no signing, no RPC
"""

from typing import Dict, Any
import time


class VertexPositionTracker:
    def __init__(self):
        self._positions: Dict[str, Dict[str, Any]] = {}

    def update(self, account: str, market: str, data: Dict[str, Any]) -> None:
        key = f"{account}:{market}"
        self._positions[key] = {
            "account": account,
            "market": market,
            "side": data["side"],
            "size": data["size"],
            "entry_price": data["entry_price"],
            "leverage": data.get("leverage"),
            "liquidation_price": data.get("liquidation_price"),
            "unrealized_pnl": data.get("unrealized_pnl"),
            "timestamp": int(time.time()),
        }

    def get(self, account: str, market: str) -> Dict[str, Any] | None:
        return self._positions.get(f"{account}:{market}")

    def close(self, account: str, market: str) -> None:
        self._positions.pop(f"{account}:{market}", None)

    def all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._positions)
