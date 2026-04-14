"""
AegisTrade - Trading Loop
"""
from __future__ import annotations
import asyncio
import time

from backend.config.config import (
    DRY_RUN, DEFAULT_SYMBOL, POLL_INTERVAL_S,
    BACKTEST_TRAIN_DAYS, DEFAULT_LANG,
)
from backend.state.state_manager import StateManager
from backend.feeds.price_feed import PriceFeed
from backend.analytics.pnl_engine import PnLEngine
from backend.risk.risk_engine import RiskEngine
from backend.strategy.strategy_engine import StrategyEngine
from backend.execution.multi_dex_router import MultiDEXRouter
from backend.execution.engine import ExecutionEngine
from backend.utils.logger import get_logger
from backend.utils.i18n import t, set_language
from backend.utils import ux_effects

log = get_logger(__name__)

_RUNNING = False
_DRY_RUN = DRY_RUN
_SYMBOL = DEFAULT_SYMBOL


def set_running(val: bool) -> None:
    global _RUNNING
    _RUNNING = val


def set_mode(dry_run: bool) -> None:
    global _DRY_RUN
    _DRY_RUN = dry_run


def set_symbol(symbol: str) -> None:
    global _SYMBOL
    _SYMBOL = symbol


def is_running() -> bool:
    return _RUNNING


def is_dry_run() -> bool:
    return _DRY_RUN


class TradingLoop:
    def __init__(self) -> None:
        self.state = StateManager()
        self.feed = PriceFeed()
        self.pnl = PnLEngine()
        self.risk = RiskEngine(self.state)
        self.strategy = StrategyEngine()
        self.router = MultiDEXRouter(dry_run=_DRY_RUN)
        self.engine = ExecutionEngine(
            self.router, self.risk, self.state, dry_run=_DRY_RUN
        )
        self._last_daily_reset: float = time.time()
        self._last_weekly_reset: float = time.time()

    async def _startup(self) -> None:
        set_language(DEFAULT_LANG)
        await self.state.load()
        await self.feed.start()
        await self.router.start()
        mode_msg = t("dry_run_mode") if _DRY_RUN else t("live_mode")
        log.info(mode_msg)
        log.info(t("bot_started"))
        candles = await self.feed.get_candles(
            _SYMBOL, limit=BACKTEST_TRAIN_DAYS
        )
        if candles:
            self.strategy.fit_regime(candles)
            log.info("HMM fitted on %d candles", len(candles))

    async def _shutdown(self) -> None:
        await self.feed.stop()
        await self.router.stop()
        log.info(t("bot_stopped"))

    async def _tick(self) -> None:
        symbol = _SYMBOL

        ticker = await self.feed.get_ticker(symbol)
        if not ticker:
            log.warning("No price for %s — skipping tick", symbol)
            return

        candles = await self.feed.get_candles(symbol, limit=60)
        if len(candles) < 25:
            log.debug("Not enough candles yet (%d)", len(candles))
            return

        now = time.time()
        if now - self._last_daily_reset > 86400:
            await self.state.daily_reset()
            self._last_daily_reset = now
        if now - self._last_weekly_reset > 7 * 86400:
            await self.state.weekly_reset()
            self._last_weekly_reset = now

        await self.engine.check_open_positions({symbol: ticker.price})

        cb = await self.risk.check_circuit_breakers()
        if cb in ("halt", "lock"):
            log.info("Circuit breaker active (%s) — skipping", cb)
            return

        if self.state.positions:
            log.debug("Position already open — waiting")
            return

        signal = self.strategy.generate_signal(candles, symbol)
        await self.state.update_regime(signal.regime)

        if signal.side != "none":
            log.info(
                "Signal: %s %s @ %.4f (regime=%s strategy=%s)",
                signal.side, symbol, signal.price,
                signal.regime, signal.strategy
            )
            await self.engine.execute_signal(signal)
        else:
            log.debug(t("no_signal"))

        report = self.pnl.full_report(self.state.trades, 50.0)
        log.debug("PnL: %s", report)

    async def run(self) -> None:
        global _RUNNING
        _RUNNING = True
        await self._startup()
        try:
            while _RUNNING:
                try:
                    await self._tick()
                except Exception as e:
                    log.exception("Tick error: %s", e)
                await asyncio.sleep(POLL_INTERVAL_S)
        finally:
            await self._shutdown()
            _RUNNING = False


_loop_instance: TradingLoop | None = None


def get_loop() -> TradingLoop:
    global _loop_instance
    if _loop_instance is None:
        _loop_instance = TradingLoop()
    return _loop_instance
