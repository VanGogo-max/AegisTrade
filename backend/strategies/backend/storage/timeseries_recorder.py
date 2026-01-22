import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any

class TimeseriesRecorder:
    """
    Async recorder за normalized market data
    """
    def __init__(self, base_path: str = "./data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # async queue за входящи събития
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False

        # файлови дескриптори по symbol+stream
        self.files: Dict[str, Any] = {}

        # lock за файлове
        self.lock = asyncio.Lock()

    # ===== Ingress from Unified Router =====
    async def publish(self, event: Dict):
        await self.queue.put(event)

    # ===== Core Recording Loop =====
    async def start(self):
        self.running = True
        while self.running:
            event = await self.queue.get()
            await self._write_event(event)

    async def _write_event(self, event: Dict):
        """
        Асинхронно записва всяко събитие във файл по symbol + stream
        """
        symbol = event.get("symbol")
        if not symbol:
            return

        stream = self.detect_event_type(event)
        if not stream:
            return

        file_key = f"{symbol}_{stream}"
        async with self.lock:
            if file_key not in self.files:
                file_path = self.base_path / f"{file_key}.jsonl"
                self.files[file_key] = open(file_path, "a", encoding="utf-8")

            f = self.files[file_key]
            f.write(json.dumps(event) + "\n")
            f.flush()

    # ===== Event Type Detection =====
    def detect_event_type(self, event: Dict) -> str:
        if "bids" in event and "asks" in event:
            return "orderbook"
        if "open" in event and "close" in event and "interval" in event:
            return "ohlcv"
        if "price" in event and "quantity" in event:
            return "trade"
        return None

    # ===== Shutdown =====
    async def stop(self):
        self.running = False
        await asyncio.sleep(0.1)  # малко време за drain
        async with self.lock:
            for f in self.files.values():
                f.close()
            self.files.clear()


# ========== Bootstrap Example ==========
async def bootstrap_recorder(router_publish_callable):
    recorder = TimeseriesRecorder(base_path="./data")
    router_publish_callable("trade", recorder.publish)
    router_publish_callable("orderbook", recorder.publish)
    router_publish_callable("ohlcv", recorder.publish)

    asyncio.create_task(recorder.start())
    return recorder
