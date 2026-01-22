import asyncio
from typing import Callable, Dict, List, Any
from collections import defaultdict

class StrategyBase:
    """
    Базов клас за всяка стратегия
    """
    def __init__(self, name: str, symbols: List[str]):
        self.name = name
        self.symbols = symbols

    async def on_trade(self, trade_event: Dict[str, Any]):
        pass

    async def on_orderbook(self, orderbook_event: Dict[str, Any]):
        pass

    async def on_ohlcv(self, ohlcv_event: Dict[str, Any]):
        pass


class StrategyEngine:
    """
    Core engine за управление на стратегии и fan-out на събития
    """
    def __init__(self):
        # symbol -> list of strategies
        self.strategies_by_symbol: Dict[str, List[StrategyBase]] = defaultdict(list)
        self.running = False
        self.queue: asyncio.Queue = asyncio.Queue()

    # ===== Registration =====
    def register_strategy(self, strategy: StrategyBase):
        for symbol in strategy.symbols:
            self.strategies_by_symbol[symbol].append(strategy)
        print(f"[StrategyEngine] Registered strategy {strategy.name} for symbols: {strategy.symbols}")

    # ===== Ingress from Unified Router =====
    async def publish(self, event: Dict):
        """
        Приема normalized събитие от UnifiedMarketDataRouter
        """
        await self.queue.put(event)

    # ===== Core Dispatch Loop =====
    async def start(self):
        self.running = True
        while self.running:
            event = await self.queue.get()
            await self.dispatch(event)

    async def dispatch(self, event: Dict):
        symbol = event.get("symbol")
        if not symbol:
            return

        strategies = self.strategies_by_symbol.get(symbol, [])
        if not strategies:
            return

        event_type = self.detect_event_type(event)
        coros = []

        for strat in strategies:
            if event_type == "trade":
                coros.append(strat.on_trade(event))
            elif event_type == "orderbook":
                coros.append(strat.on_orderbook(event))
            elif event_type == "ohlcv":
                coros.append(strat.on_ohlcv(event))

        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    # ===== Event Type Detection =====
    def detect_event_type(self, event: Dict) -> str:
        if "bids" in event and "asks" in event:
            return "orderbook"
        if "open" in event and "close" in event and "interval" in event:
            return "ohlcv"
        if "price" in event and "quantity" in event:
            return "trade"
        return None


# ========== Example Strategy ==========
class PrintTradesStrategy(StrategyBase):
    async def on_trade(self, trade_event: Dict):
        print(f"[{self.name}] Trade {trade_event['symbol']}: {trade_event['price']} x {trade_event['quantity']}")


# ========== Bootstrap Example ==========
async def bootstrap_strategy_engine(router_publish_callable: Callable):
    engine = StrategyEngine()
    # регистрираме тестова стратегия
    engine.register_strategy(PrintTradesStrategy("PrintTrades", symbols=["BTCUSDT", "ETHUSDT"]))

    # свързваме engine към UnifiedMarketDataRouter
    router_publish_callable("trade", engine.publish)
    router_publish_callable("orderbook", engine.publish)
    router_publish_callable("ohlcv", engine.publish)

    # стартираме engine loop
    asyncio.create_task(engine.start())

    return engine
