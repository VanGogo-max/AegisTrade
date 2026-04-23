"""
AegisTrade - Risk Engine
"""
from __future__ import annotations
from backend.config.config import MAX_DAILY_LOSS, MAX_DRAWDOWN_PCT, MAX_POSITION_SIZE
from backend.utils.logger import get_logger

log = get_logger(__name__)


class RiskEngine:
    def __init__(self, state) -> None:
        self.state = state
        self._peak_balance = 0.0

    def snapshot(self) -> dict:
        balance = self.state.balance or 0.0
        if balance > self._peak_balance:
            self._peak_balance = balance
        drawdown = 0.0
        if self._peak_balance > 0:
            drawdown = (self._peak_balance - balance) / self._peak_balance * 100
        return {
            "max_drawdown": round(drawdown, 2),
            "exposure": round(len(self.state.positions) * 10.0, 2),
            "open_positions": len(self.state.positions),
            "daily_loss": round(self.state.daily_pnl, 2),
        }

    async def check_circuit_breakers(self) -> str:
        if self.state.system_locked:
            return "lock"
        if self.state.trading_halted:
            return "halt"
        if self.state.daily_pnl < -abs(MAX_DAILY_LOSS):
            log.warning("Daily loss limit hit")
            await self.state.set_halted(True)
            return "halt"
        return "ok"

    async def should_close(self, pos: dict, current_price: float) -> bool:
        entry = pos.get("entry_price", current_price)
        side = pos.get("side", "long")
        qty = pos.get("qty", 0)
        pnl = (current_price - entry) * qty if side in ("long", "buy") else (entry - current_price) * qty
        stop_loss = -abs(entry * qty * 0.02)
        take_profit = abs(entry * qty * 0.04)
        return pnl <= stop_loss or pnl >= take_profit
