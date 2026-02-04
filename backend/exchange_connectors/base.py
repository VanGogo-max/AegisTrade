import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List


class BaseExchangeConnector(ABC):
    def __init__(
        self,
        name: str,
        symbols: List[str],
        on_message: Callable[[Dict[str, Any]], None],
    ):
        self.name = name
        self.symbols = symbols
        self.on_message = on_message
        self._running = False
        self._reconnect_delay = 5

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    async def _safe_emit(self, event: Dict[str, Any]):
        event["exchange"] = self.name
        await self.on_message(event)

    async def run_forever(self):
        self._running = True
        while self._running:
            try:
                await self.connect()
            except Exception as e:
                print(f"[{self.name}] error: {e}, reconnecting in {self._reconnect_delay}s")
                await asyncio.sleep(self._reconnect_delay)

    def stop(self):
        self._running = False
