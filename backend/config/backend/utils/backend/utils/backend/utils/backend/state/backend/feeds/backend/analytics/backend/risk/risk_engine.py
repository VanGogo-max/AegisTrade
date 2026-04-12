"""
AegisTrade — Risk Engine
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from backend.config.config import (
    RISK_PER_TRADE_PCT, DAILY_LOSS_LIMIT_PCT, DAILY_STOP_PCT,
    WEEKLY_LOSS_LIMIT_PCT, WEEKLY_SYSTEM_LOCK_PCT,
    MIN_FEE_PCT, MAX_SLIPPAGE_PCT,
)
from backend.state.state_manager import StateManager
from backend.utils.logger import get_logger
from backend.utils.i18n import t
from backend.utils import ux_effects

log = get_logger(__name__)


@dataclass
class RiskDecision:
    allowed: bool
    reason: str
    qty: float = 0.0
    risk_amount: float = 0.0
    circuit_breaker: Optional[str] = None


class RiskEngine:
    def __init__(self, state: StateManager) -> None:
        self._state = state

    async def check_circuit_breakers(self) -> Optional[str]:
        daily_loss = -self._state.daily_pnl
        weekly_loss = -self._state.weekly_pnl
        balance = self._state.balance

        if weekly_loss / max(balance, 1) >= WEEKLY_SYSTEM_LOCK_PCT:
            if not self._state.system_locked:
                await self._state.set_locked(True)
                log.critical(t("risk_weekly_lock", pct=weekly_loss / balance))
                await ux_effects.anim_risk_warning("lock")
            return "lock"

        if daily_loss / max(balance, 1) >= DAILY_STOP_PCT:
            if not self._state.trading_halted:
                await self._state.set_halted(True)
                log.error(t("risk_daily_stop", pct=daily_loss / balance))
                await ux_effects.anim_risk_warning("halt")
            return "halt"

        if daily_loss / max(balance, 1) >= DAILY_LOSS_LIMIT_PCT:
            log.warning(t("risk_daily_limit", pct=daily_loss / balance))
            await ux_effects.anim_risk_warning("reduce")
            return "reduce"

        return None

    def compute_position_size(
        self,
        price: float,
        stop_loss: float,
    ) -> Tuple[float, float]:
        balance = self._state.balance
        risk_amount = balance * RISK_PER_TRADE_PCT
        distance = abs(price - stop_loss)
        if distance == 0:
            return 0.0, 0.0
        qty = risk_amount / distance
        return round(qty, 6), round(risk_amount, 4)

    async def pre_trade_check(
        self,
        symbol: str,
        price: float,
        stop_loss: float,
        estimated_fee_pct: float = MIN_FEE_PCT,
        estimated_slippage_pct: float = 0.0,
    ) -> RiskDecision:
        if self._state.system_locked:
            return RiskDecision(False, "System locked", circuit_breaker="lock")
        if self._state.trading_halted:
            return RiskDecision(False, "Trading halted", circuit_breaker="halt")

        cb = await self.check_circuit_breakers()
        if cb == "lock":
            return RiskDecision(False, "System locked", circuit_breaker="lock")
        if cb == "halt":
            return RiskDecision(False, "Trading halted", circuit_breaker="halt")

        if estimated_fee_pct >= 0.01:
            return RiskDecision(False, f"Fee {estimated_fee_pct:.2%} too high")

        if estimated_slippage_pct > MAX_SLIPPAGE_PCT:
            return RiskDecision(False, f"Slippage {estimated_slippage_pct:.4%} too high")

        if self._state.balance < 5.0:
            return RiskDecision(False, t("insufficient_balance"))

        qty, risk_amount = self.compute_position_size(price, stop_loss)
        if qty <= 0:
            return RiskDecision(False, "Invalid qty")

        if qty * price < 1.0:
            return RiskDecision(False, "Notional too small")

        if cb == "reduce":
            qty = round(qty * 0.5, 6)
            risk_amount = round(risk_amount * 0.5, 4)

        log.info(t("risk_ok") + f" | {symbol} qty={qty} risk=${risk_amount:.2f}")
        return RiskDecision(
            allowed=True,
            reason=t("risk_ok"),
            qty=qty,
            risk_amount=risk_amount,
            circuit_breaker=cb,
        )

    def snapshot(self) -> dict:
        balance = self._state.balance
        daily_loss = -self._state.daily_pnl
        weekly_loss = -self._state.weekly_pnl
        return {
            "balance": round(balance, 2),
            "daily_pnl": round(self._state.daily_pnl, 2),
            "weekly_pnl": round(self._state.weekly_pnl, 2),
            "daily_loss_pct": round(daily_loss / max(balance, 1) * 100, 2),
            "weekly_loss_pct": round(weekly_loss / max(balance, 1) * 100, 2),
            "daily_limit_pct": DAILY_LOSS_LIMIT_PCT * 100,
            "daily_stop_pct": DAILY_STOP_PCT * 100,
            "weekly_lock_pct": WEEKLY_SYSTEM_LOCK_PCT * 100,
            "system_locked": self._state.system_locked,
            "trading_halted": self._state.trading_halted,
            "open_positions": len(self._state.positions),
        }
