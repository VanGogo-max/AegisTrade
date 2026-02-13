import asyncio
from typing import Dict, Callable, Awaitable, List


class StrategyEngine:
    """
    Central event bus for all trading strategies.
    Receives normalized market events and forwards them to strategies.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue = asyncio.Queue()
        self._strategies: List[Callable[[dict], Awaitable[None]]] = []
        self._running: bool = False

    def register_strategy(self, handler: Callable[[dict], Awaitable[None]]) -> None:
        """
        Registers an async strategy handler.
        """
        self._strategies.append(handler)

    async def publish(self, event: Dict) -> None:
        """
        Receives market event from router.
        """
        await self._queue.put(event)

    async def start(self) -> None:
        """
        Main loop.
        """
        self._running = True
        while self._running:
            event = await self._queue.get()
            for strategy in self._strategies:
                asyncio.create_task(strategy(event))

    async def stop(self) -> None:
        self._running = False
