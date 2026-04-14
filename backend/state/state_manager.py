"""
AegisTrade - State Manager
"""
from __future__ import annotations
import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import Any

STATE_FILE = "aegis_state.json"


class StateManager:
    def __init__(self) -> None:
        self.balance: float = 0.0
        self.equity: float = 0.0
        self.positions: dict = {}
        self.trades: list = []
        self.daily_pnl: float = 0.0
        self.weekly_pnl: float = 0.0
        self.total_pnl: float = 0.0
        self.current_regime: str = "unknown"
        self.system_locked: bool = False
        self.trading_halted: bool = False

    async def load(self) -> None:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE) as f:
                    data = json.load(f)
                self.balance = data.get("balance", 0.0)
                self.positions = data.get("positions", {})
                self.trades = data.get("trades", [])
                self.total_pnl = data.get("total_pnl", 0.0)
            except Exception:
                pass

    async def save(self) -> None:
        with open(STATE_FILE, "w") as f:
            json.dump({
                "balance": self.balance,
                "positions": self.positions,
                "trades": self.trades,
                "total_pnl": self.total_pnl,
            }, f)

    async def add_position(self, pos: dict) -> None:
        symbol = pos.get("symbol", "unknown")
        self.positions[symbol] = pos

    async def close_position(self, symbol: str, price: float) -> None:
        pos = self.positions.pop(symbol, None)
        if pos:
            entry = pos.get("entry_price", price)
            side = pos.get("side", "long")
            qty = pos.get("qty", 0)
            pnl = (price - entry) * qty if side in ("long", "buy") else (entry - price) * qty
            self.total_pnl += pnl
            self.daily_pnl += pnl
            self.weekly_pnl += pnl
            self.trades.append({**pos, "exit_price": price, "pnl": pnl})
            await self.save()

    async def update_regime(self, regime: str) -> None:
        self.current_regime = regime

    async def daily_reset(self) -> None:
        self.daily_pnl = 0.0

    async def weekly_reset(self) -> None:
        self.weekly_pnl = 0.0

    async def set_locked(self, val: bool) -> None:
        self.system_locked = val

    async def set_halted(self, val: bool) -> None:
        self.trading_halted = val
