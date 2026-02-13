import asyncio
from typing import Dict, Any, List

from backend.storage.timeseries_recorder import TimeSeriesRecorder


class MarketDataOrchestrator:
    """
    Централен coordinator между:
    - Exchange Connectors (Binance, Hyperliquid и др.)
    - Recorder
    - Future strategy engines
    """

    def __init__(self):
        self.recorder = TimeSeriesRecorder()
        self.subscribers: List = []
        self._tasks: List[asyncio.Task] = []

    # ========= Lifecycle =========

    async def start(self):
        """
        Стартира background services
        """
        recorder_task = asyncio.create_task(self.recorder.start())
        self._tasks.append(recorder_task)

    async def stop(self):
        for task in self._tasks:
            task.cancel()

    # ========= Event Entry Point =========

    async def handle_event(self, event: Dict[str, Any]):
        """
        Всички normalized events минават оттук
        """
        # 1. Запис в storage
        await self.recorder.record(event)

        # 2. Notify subscribers (strategies, websocket broadcast и др.)
        for subscriber in self.subscribers:
            await subscriber(event)

    # ========= Subscribers =========

    def subscribe(self, callback):
        """
        Позволява добавяне на strategy engine или broadcast handler
        """
        self.subscribers.append(callback)
