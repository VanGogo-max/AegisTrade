# position_state_store.py
"""
Position State Store

Role:
- Tracks open positions per market/strategy
- Maintains PnL, leverage, size, side
- Provides cooldowns and exposure checks
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger


class PositionStateStore:
    def __init__(self):
        self.positions: Dict[str, Dict[str, Any]] = {}  # key: market|strategy
        self.closed_positions: list[Dict[str, Any]] = []

        # Optional cooldown tracker per market/strategy
        self.cooldowns: Dict[str, datetime] = {}
        self.default_cooldown = timedelta(seconds=0)  # Can be set via config

    # ----------------------------
    # Open position
    # ----------------------------
    def open_position(self, market: str, strategy: str, side: str, size_usd: float, leverage: float, entry_price: float):
        key = f"{market}|{strategy}"
        if key in self.positions:
            logger.warning(f"Overwriting existing position for {key}")

        self.positions[key] = {
            "market": market,
            "strategy": strategy,
            "side": side,
            "size_usd": size_usd,
            "leverage": leverage,
            "entry_price": entry_price,
            "opened_at": datetime.utcnow(),
        }

        logger.info(f"Opened position: {self.positions[key]}")

    # ----------------------------
    # Close position
    # ----------------------------
    def close_position(self, market: str, strategy: str, exit_price: float) -> Dict[str, Any] | None:
        key = f"{market}|{strategy}"
        pos = self.positions.pop(key, None)
        if not pos:
            logger.warning(f"No open position found for {key}")
            return None

        pnl = (exit_price - pos["entry_price"]) / pos["entry_price"]
        if pos["side"].lower() == "short":
            pnl *= -1
        pnl_usd = pnl * pos["size_usd"] * pos["leverage"]

        closed_pos = pos.copy()
        closed_pos.update({
            "exit_price": exit_price,
            "closed_at": datetime.utcnow(),
            "pnl_usd": pnl_usd
        })
        self.closed_positions.append(closed_pos)

        # set cooldown
        self.cooldowns[key] = datetime.utcnow() + self.default_cooldown

        logger.info(f"Closed position: {closed_pos}")
        return closed_pos

    # ----------------------------
    # Check if market/strategy is on cooldown
    # ----------------------------
    def is_on_cooldown(self, market: str, strategy: str) -> bool:
        key = f"{market}|{strategy}"
        cd_until = self.cooldowns.get(key)
        if not cd_until:
            return False
        return datetime.utcnow() < cd_until

    # ----------------------------
    # Get open positions
    # ----------------------------
    def get_open_positions(self) -> Dict[str, Dict[str, Any]]:
        return self.positions.copy()

    # ----------------------------
    # Get closed positions
    # ----------------------------
    def get_closed_positions(self) -> list[Dict[str, Any]]:
        return list(self.closed_positions)

    # ----------------------------
    # Reset store
    # ----------------------------
    def reset(self):
        self.positions.clear()
        self.closed_positions.clear()
        self.cooldowns.clear()
        logger.info("PositionStateStore reset")
