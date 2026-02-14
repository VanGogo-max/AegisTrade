# backend/strategies/base_strategy.py

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Set

from backend.market_data.normalizer import (
    NormalizedTrade,
    NormalizedOrderBook,
    NormalizedOHLCV,
    MarketEventType,
)
from backend.market_data.market_router import MarketRouter


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    Responsibilities:
    - Subscribe to market router
    - Handle normalized events
    - Maintain internal state
    - Provide lifecycle control
    """

    def __init__(
        self,
        name: str,
        router: MarketRouter,
        symbols: Set[str],
    ) -> None:
        self.name = name
        self.router = router
        self.symbols = symbols

        self._running = False
        self._lock = asyncio.Lock()

        # internal per-symbol state
        self.state: Dict[str, dict] = {symbol: {} for symbol in symbols}

    # ==========================================================
    # LIFECYCLE
    # ==========================================================

    async def start(self) -> None:
        """
        Start strategy and subscribe to router.
        """
        async with self._lock:
            if self._running:
                return

            for symbol in self.symbols:
                await self.router.subscribe_symbol(symbol, self._on_event)

            self._running = True

        await self.on_start()

    async def stop(self) -> None:
        """
        Stop strategy.
        (Unsubscribe logic can be extended later.)
        """
        async with self._lock:
            if not self._running:
                return

            self._running = False

        await self.on_stop()

    @property
    def is_running(self) -> bool:
        return self._running

    # ==========================================================
    # EVENT ENTRYPOINT
    # ==========================================================

    async def _on_event(self, event) -> None:
        if not self._running:
            return

        if isinstance(event, NormalizedTrade):
            await self.on_trade(event)

        elif isinstance(event, NormalizedOrderBook):
            await self.on_orderbook(event)

        elif isinstance(event, NormalizedOHLCV):
            await self.on_ohlcv(event)

    # ==========================================================
    # EVENT HOOKS (override in child strategies)
    # ==========================================================

    async def on_start(self) -> None:
        """Optional override."""
        pass

    async def on_stop(self) -> None:
        """Optional override."""
        pass

    async def on_trade(self, trade: NormalizedTrade) -> None:
        """Override for trade events."""
        pass

    async def on_orderbook(self, orderbook: NormalizedOrderBook) -> None:
        """Override for orderbook events."""
        pass

    async def on_ohlcv(self, ohlcv: NormalizedOHLCV) -> None:
        """Override for kline events."""
        pass

    # ==========================================================
    # UTILITIES
    # ==========================================================

    def get_symbol_state(self, symbol: str) -> dict:
        return self.state.setdefault(symbol, {})

    def reset_symbol_state(self, symbol: str) -> None:
        self.state[symbol] = {}
