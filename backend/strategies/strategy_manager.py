# backend/strategies/strategy_manager.py

import asyncio
from typing import Dict, Optional, List

from .base_strategy import BaseStrategy


class StrategyManager:
    """
    Central registry and lifecycle controller for trading strategies.
    """

    def __init__(self) -> None:
        self._strategies: Dict[str, BaseStrategy] = {}
        self._lock = asyncio.Lock()

    # ==========================================================
    # REGISTRATION
    # ==========================================================

    async def register(self, strategy: BaseStrategy) -> None:
        async with self._lock:
            if strategy.name in self._strategies:
                raise ValueError(f"Strategy '{strategy.name}' already registered")

            self._strategies[strategy.name] = strategy

    async def unregister(self, name: str) -> None:
        async with self._lock:
            strategy = self._strategies.pop(name, None)

        if strategy and strategy.is_running:
            await strategy.stop()

    # ==========================================================
    # START / STOP
    # ==========================================================

    async def start(self, name: str) -> None:
        strategy = await self._get_strategy(name)

        if strategy.is_running:
            return

        await strategy.start()

    async def stop(self, name: str) -> None:
        strategy = await self._get_strategy(name)

        if not strategy.is_running:
            return

        await strategy.stop()

    async def start_all(self) -> None:
        strategies = await self._list_strategies()

        await asyncio.gather(
            *(s.start() for s in strategies if not s.is_running),
            return_exceptions=True,
        )

    async def stop_all(self) -> None:
        strategies = await self._list_strategies()

        await asyncio.gather(
            *(s.stop() for s in strategies if s.is_running),
            return_exceptions=True,
        )

    # ==========================================================
    # INFO
    # ==========================================================

    async def list(self) -> List[str]:
        async with self._lock:
            return list(self._strategies.keys())

    async def get(self, name: str) -> Optional[BaseStrategy]:
        async with self._lock:
            return self._strategies.get(name)

    # ==========================================================
    # INTERNALS
    # ==========================================================

    async def _get_strategy(self, name: str) -> BaseStrategy:
        async with self._lock:
            strategy = self._strategies.get(name)

        if not strategy:
            raise ValueError(f"Strategy '{name}' not found")

        return strategy

    async def _list_strategies(self) -> List[BaseStrategy]:
        async with self._lock:
            return list(self._strategies.values())
