import asyncio
from typing import Dict, Callable, List
from collections import defaultdict
import time


class UnifiedMarketDataRouter:
    def __init__(self):
        # subscribers по тип събитие
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

        # обща опашка за входящи събития
        self.queue: asyncio.Queue = asyncio.Queue()

        # статистика
        self.stats = {
            "received": 0,
            "dispatched": 0,
            "last_event_ts": None
        }

        self.running = False

    # ===== Subscription Layer =====

    def subscribe(self, event_type: str, handler: Callable):
        """
        event_type: trade | orderbook | ohlcv | liquidation | funding | etc
        handler: async callable
        """
        self.subscribers[event_type].append(handler)

    # ===== Ingress from Exchange Connectors =====

    async def publish(self, normalized_event: Dict):
        """
        Получава вече нормализирани събития от конектори (Binance, GMX, HL...)
        """
        await self.queue.put(normalized_event)

    # ===== Core Dispatch Loop =====

    async def start(self):
        self.running = True
        while self.running:
            event = await self.queue.get()
            await self.dispatch(event)

    async def dispatch(self, event: Dict):
        self.stats["received"] += 1
        self.stats["last_event_ts"] = int(time.time() * 1000)

        event_type = self.detect_event_type(event)

        if event_type not in self.subscribers:
            return

        handlers = self.subscribers[event_type]

        # паралелно fan-out разпращане
        await asyncio.gather(
            *[handler(event) for handler in handlers],
            return_exceptions=True
        )

        self.stats["dispatched"] += len(handlers)

    # ===== Event Type Detection =====

    def detect_event_type(self, event: Dict) -> str:
        if "bids" in event and "asks" in event:
            return "orderbook"
        if "open" in event and "close" in event and "interval" in event:
            return "ohlcv"
        if "price" in event and "quantity" in event:
            return "trade"
        return "unknown"

    # ===== Shutdown =====

    async def stop(self):
        self.running = False

    # ===== Health / Monitoring =====

    def get_stats(self) -> Dict:
        return self.stats.copy()


# ========== Примерни адаптери (временно) ==========

async def ui_ws_publisher(event: Dict):
    # ще бъде заменено от FastAPI WebSocket Hub
    pass

async def strategy_engine_ingest(event: Dict):
    # вход за стратегии и ботове
    pass

async def recorder_ingest(event: Dict):
    # писане в time-series storage
    pass

async def risk_engine_ingest(event: Dict):
    # liquidation / margin / funding guards
    pass


# ========== Bootstrap Example ==========

async def bootstrap():
    router = UnifiedMarketDataRouter()

    router.subscribe("trade", ui_ws_publisher)
    router.subscribe("trade", strategy_engine_ingest)
    router.subscribe("orderbook", strategy_engine_ingest)
    router.subscribe("ohlcv", recorder_ingest)
    router.subscribe("trade", risk_engine_ingest)

    asyncio.create_task(router.start())

    return router
