import asyncio
from collections import defaultdict, deque
from typing import Dict, List


class SnapshotCache:
    def __init__(self, max_trades: int = 200, max_candles: int = 200):
        self.orderbooks: Dict[str, Dict] = {}
        self.trades: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_trades))
        self.ohlcv: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=max_candles)))

        self.lock = asyncio.Lock()

    # ===== Ingest from Unified Router =====

    async def ingest(self, event: Dict):
        async with self.lock:
            symbol = event.get("symbol")

            if "bids" in event and "asks" in event:
                self.orderbooks[symbol] = event

            elif "price" in event and "quantity" in event:
                self.trades[symbol].append(event)

            elif "open" in event and "interval" in event:
                interval = event["interval"]
                self.ohlcv[symbol][interval].append(event)

    # ===== Snapshot API =====

    async def get_snapshot(self, symbol: str) -> Dict:
        async with self.lock:
            return {
                "symbol": symbol,
                "orderbook": self.orderbooks.get(symbol),
                "trades": list(self.trades.get(symbol, [])),
                "ohlcv": {
                    interval: list(candles)
                    for interval, candles in self.ohlcv.get(symbol, {}).items()
                }
            }

    async def get_orderbook(self, symbol: str):
        async with self.lock:
            return self.orderbooks.get(symbol)

    async def get_trades(self, symbol: str):
        async with self.lock:
            return list(self.trades.get(symbol, []))

    async def get_ohlcv(self, symbol: str, interval: str):
        async with self.lock:
            return list(self.ohlcv.get(symbol, {}).get(interval, []))

    # ===== Maintenance =====

    async def clear_symbol(self, symbol: str):
        async with self.lock:
            self.orderbooks.pop(symbol, None)
            self.trades.pop(symbol, None)
            self.ohlcv.pop(symbol, None)

    async def clear_all(self):
        async with self.lock:
            self.orderbooks.clear()
            self.trades.clear()
            self.ohlcv.clear()
