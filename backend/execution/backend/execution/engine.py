"""
AegisTrade — Execution Engine
"""
from __future__ import annotations
from dataclasses import dataclass
from backend.execution.multi_dex_router import MultiDEXRouter
from backend.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class Signal:
    side: str
    symbol: str
    price: float
    qty: float
    regime: str = ""
    strategy: str = ""
    dex: str = "hyperliquid"


class ExecutionEngine:
    def __init__(self, router: MultiDEXRouter, risk, state, dry_run: bool = True) -> None:
        self.router = router
        self.risk = risk
        self.state = state
        self.dry_run = dry_run

    async def execute_signal(self, signal) -> None:
        symbol = signal.symbol
        side   = signal.side
        price  = signal.price
        qty    = getattr(signal, "qty", 0.01)
        dex    = getattr(signal, "dex", None)

        if dex is None:
            dex = await self.router.best_dex(symbol, qty, price)

        log.info("Executing %s %s qty=%.4f price=%.4f dex=%s dry=%s",
                 side, symbol, qty, price, dex, self.dry_run)

        result = await self.router.place_order(dex, symbol, side, qty, price)

        if result.success:
            await self.state.add_position({
                "symbol":      symbol,
                "side":        side,
                "qty":         result.filled_qty,
                "entry_price": result.filled_price,
                "dex":         dex,
                "simulated":   result.simulated,
            })
            log.info("Order filled: %s @ %.4f fee=%.6f", dex, result.filled_price, result.fee)
        else:
            log.error("Order failed on %s: %s", dex, result.error)

    async def check_open_positions(self, prices: dict[str, float]) -> None:
        for symbol, pos in list(self.state.positions.items()):
            price = prices.get(symbol)
            if not price:
                continue
            entry = pos.get("entry_price", price)
            side  = pos.get("side", "long")
            pnl   = (price - entry) if side == "long" else (entry - price)
            should_close = await self.risk.should_close(pos, price)
            if should_close:
                log.info("Closing position %s pnl=%.4f", symbol, pnl)
                qty = pos.get("qty", 0.01)
                dex = pos.get("dex", "hyperliquid")
                close_side = "sell" if side in ("long", "buy") else "buy"
                result = await self.router.place_order(dex, symbol, close_side, qty, price)
                if result.success:
                    await self.state.close_position(symbol, price)
