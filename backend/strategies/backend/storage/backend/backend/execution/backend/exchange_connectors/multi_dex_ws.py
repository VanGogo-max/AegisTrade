import asyncio
from typing import List, Callable, Dict, Any
from enum import Enum

# Stub connector classes за различните DEX
class ExchangeName(str, Enum):
    BINANCE = "binance"
    GMX = "gmx"
    HYPERLIQUID = "hyperliquid"
    DYDX = "dydx"

class MultiDEXWSConnector:
    """
    Production-ready multi-DEX websocket connector
    """
    def __init__(self,
                 symbols: List[str],
                 exchanges: List[ExchangeName],
                 intervals: List[str],
                 on_message: Callable[[Dict], Any]):
        """
        symbols: ["BTCUSDT", "ETHUSDT"]
        exchanges: ["binance", "gmx"]
        intervals: ["1m", "5m"]
        on_message: callable(event)
        """
        self.symbols = symbols
        self.exchanges = exchanges
        self.intervals = intervals
        self.on_message = on_message
        self.running = False
        self.tasks: List[asyncio.Task] = []

        # state for reconnect / failover
        self.state: Dict[str, Any] = {}

    # ===== Connect =====
    async def connect(self):
        self.running = True
        for exch in self.exchanges:
            task = asyncio.create_task(self._connect_exchange(exch))
            self.tasks.append(task)
        print(f"[MultiDEXWS] Started connections for exchanges: {self.exchanges}")

    async def _connect_exchange(self, exchange: ExchangeName):
        """
        Stub: В production заменете с реален WS client per DEX
        """
        print(f"[{exchange}] Connecting...")
        while self.running:
            try:
                # симулираме получаване на събития на всеки 100ms
                for symbol in self.symbols:
                    for interval in self.intervals:
                        event = {
                            "exchange": exchange.value,
                            "symbol": symbol,
                            "interval": interval,
                            "price": 1000.0,  # stub
                            "quantity": 0.001,  # stub
                            "bids": [[1000, 1]],
                            "asks": [[1001, 1]]
                        }
                        await self.on_message(event)
                        await asyncio.sleep(0.1)
            except Exception as e:
                print(f"[{exchange}] Error: {e}, reconnecting in 1s...")
                await asyncio.sleep(1)

    # ===== Stop =====
    async def stop(self):
        self.running = False
        for t in self.tasks:
            t.cancel()
        print(f"[MultiDEXWS] All exchange connections stopped")
