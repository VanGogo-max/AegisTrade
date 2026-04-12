"""
AegisTrade — Execution Engine
"""
from __future__ import annotations
import uuid
from typing import Optional

from backend.config.config import DRY_RUN
from backend.execution.multi_dex_router import MultiDEXRouter
from backend.risk.risk_engine import RiskEngine
from backend.state.state_manager import StateManager, Position
from backend.strategy.strategy_engine import Signal
from backend.utils.logger import get_logger
from backend.utils.i18n import t
from backend.utils import ux_effects

log = get_logger(__name__)


class ExecutionEngine:
    def __init__(
        self,
        router: MultiDEXRouter,
        risk: RiskEngine,
        state: StateManager,
        dry_run: bool = DRY_RUN,
    ) -> None:
        self.router = router
        self.risk = risk
        self.state = state
        self.dry_run = dry_run

    async def execute_signal(self, signal: Signal) -> Optional[str]:
        if signal.side == "none":
            log.debug(t("no_signal"))
            return None

        decision = await self.risk.pre_trade_check(
            symbol=signal.symbol,
            price=signal.price,
            stop_loss=signal.stop_loss,
        )
        if not decision.allowed:
            log.info("Trade blocked: %s", decision.reason)
            return None

        qty = decision.qty
        price = signal.price

        result = await self.router.route_order(
            signal.symbol, signal.side, qty, price
        )
        if not result.success:
            log.error("Routing failed: %s", result.error)
            return None

        filled_price = result.filled_price or price
        filled_qty = result.filled_qty or qty

        if self.dry_run:
            log.info(t("order_simulated",
                side=signal.side, qty=filled_qty,
                symbol=signal.symbol, price=filled_price))
        else:
            log.info(t("order_placed",
                side=signal.side, qty=filled_qty,
                symbol=signal.symbol, price=filled_price))

        if signal.side == "long":
            await ux_effects.sound_buy(signal.symbol, filled_price)
        else:
            await ux_effects.sound_sell(signal.symbol, filled_price)

        pos = Position(
            id=str(uuid.uuid4()),
            symbol=signal.symbol,
            side=signal.side,
            qty=filled_qty,
            entry_price=filled_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            strategy=signal.strategy,
            dex=result.dex,
        )
        await self.state.open_position(pos)
        await ux_effects.anim_new_position(signal.symbol)
        log.info("Position opened: %s %s qty=%.6f entry=%.4f",
                 pos.side, pos.symbol, pos.qty, pos.entry_price)
        return pos.id

    async def close_position(
        self, position_id: str, exit_price: float, reason: str = "manual"
    ) -> None:
        record = await self.state.close_position(
            position_id, exit_price, reason
        )
        if not record:
            return
        if record.pnl >= 0:
            await ux_effects.sound_profit(record.symbol, record.pnl)
        else:
            await ux_effects.sound_stop_loss(record.symbol, record.pnl)
        await ux_effects.anim_pnl_update(record.pnl)
        log.info(t("position_closed", symbol=record.symbol, pnl=record.pnl))

    async def check_open_positions(self, current_prices: dict) -> None:
        for pos_id, pos_data in list(self.state.positions.items()):
            symbol = pos_data["symbol"]
            price = current_prices.get(symbol)
            if price is None:
                continue
            side = pos_data["side"]
            sl = pos_data["stop_loss"]
            tp = pos_data["take_profit"]
            hit_sl = (
                (side == "long" and price <= sl) or
                (side == "short" and price >= sl)
            )
            hit_tp = (
                (side == "long" and price >= tp) or
                (side == "short" and price <= tp)
            )
            if hit_sl:
                log.warning("Stop-loss hit: %s @ %.4f", symbol, price)
                await self.close_position(pos_id, price, "stop_loss")
            elif hit_tp:
                log.info("Take-profit hit: %s @ %.4f", symbol, price)
                await self.close_position(pos_id, price, "take_profit")
