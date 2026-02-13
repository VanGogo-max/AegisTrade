import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any


class TimeSeriesRecorder:
    """
    Записва normalized market events (trade / orderbook / ohlcv)
    в JSONL формат по символ и тип.
    """

    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False

        os.makedirs(self.base_path, exist_ok=True)

    # ========= External API =========
    async def record(self, event: Dict[str, Any]):
        """
        Приема normalized event от UnifiedMarketDataRouter
        """
        await self.queue.put(event)

    # ========= Core Loop =========
    async def start(self):
        self.running = True
        while self.running:
            event = await self.queue.get()
            await self._write_event(event)

    # ========= Internal =========
    async def _write_event(self, event: Dict[str, Any]):
        symbol = event.get("symbol")
        if not symbol:
            return

        event_type = self._detect_event_type(event)
        if not event_type:
            return

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        folder = os.path.join(self.base_path, symbol, event_type)
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, f"{date_str}.jsonl")

        # добавяме timestamp ако липсва
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().timestamp()

        with open(file_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _detect_event_type(self, event: Dict[str, Any]) -> str | None:
        if "bids" in event and "asks" in event:
            return "orderbook"
        if "open" in event and "close" in event and "interval" in event:
            return "ohlcv"
        if "price" in event and "quantity" in event:
            return "trade"
        return None
