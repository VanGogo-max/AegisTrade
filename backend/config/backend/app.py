import asyncio
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

from backend.config.exchanges import ExchangeName, ACTIVE_EXCHANGES

from backend.exchange_connectors.binance_ws import BinanceWSConnector
from backend.exchange_connectors.hyperliquid_ws import HyperliquidWSConnector
from backend.exchange_connectors.multi_dex_ws import MultiDEXWSConnector
from backend.exchange_connectors.gmx_web3_connector import GMXWeb3Connector

from backend.market_data.unified_router import UnifiedMarketDataRouter
from backend.market_data.snapshot_cache import SnapshotCache
from backend.ws_gateway.market_ws_hub import MarketWSHub, websocket_endpoint
from backend.strategies.strategy_engine import StrategyEngine, StrategyBase, PrintTradesStrategy
from backend.storage.timeseries_recorder import TimeseriesRecorder
from backend.execution.order_manager import OrderManager, Order, OrderSide, OrderType, simple_risk_check, mock_send_order

app = FastAPI(title="Multi-DEX Trading Platform Backend")

router = UnifiedMarketDataRouter()
snapshot_cache = SnapshotCache()
market_ws_hub = MarketWSHub(snapshot_cache)
strategy_engine = StrategyEngine()
recorder = TimeseriesRecorder(base_path="./data")

order_manager: OrderManager | None = None

class StrategyOrderRouter:
    def __init__(self, order_manager: OrderManager):
        self.order_manager = order_manager

    async def send_signal(self, signal: dict):
        order = Order(
            symbol=signal['symbol'],
            side=OrderSide(signal['side']),
            qty=signal['qty'],
            price=signal.get('price'),
            type_=OrderType(signal.get('type', 'market'))
        )
        await self.order_manager.submit_order(order)

signal_router: StrategyOrderRouter | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global order_manager, signal_router

    router.subscribe("trade", snapshot_cache.ingest)
    router.subscribe("orderbook", snapshot_cache.ingest)
    router.subscribe("ohlcv", snapshot_cache.ingest)

    async def ui_publisher(event: dict):
        await market_ws_hub.publish(event)

    router.subscribe("trade", ui_publisher)
    router.subscribe("orderbook", ui_publisher)
    router.subscribe("ohlcv", ui_publisher)

    hub_task = asyncio.create_task(market_ws_hub.start())

    async def strategy_publisher(event: dict):
        await strategy_engine.publish(event)

    router.subscribe("trade", strategy_publisher)
    router.subscribe("orderbook", strategy_publisher)
    router.subscribe("ohlcv", strategy_publisher)

    engine_task = asyncio.create_task(strategy_engine.start())

    async def recorder_publisher(event: dict):
        await recorder.publish(event)

    router.subscribe("trade", recorder_publisher)
    router.subscribe("orderbook", recorder_publisher)
    router.subscribe("ohlcv", recorder_publisher)

    recorder_task = asyncio.create_task(recorder.start())

    order_manager = OrderManager(risk_check=simple_risk_check, send_order_callable=mock_send_order)
    asyncio.create_task(order_manager.start())
    signal_router = StrategyOrderRouter(order_manager)

    class ExampleBuyStrategy(StrategyBase):
        async def on_trade(self, trade_event: dict):
            if trade_event['symbol'] == "BTCUSDT" and trade_event['price'] < 20000:
                await signal_router.send_signal({
                    "symbol": "BTCUSDT",
                    "side": "buy",
                    "qty": 0.001,
                    "price": trade_event['price'],
                    "type": "market"
                })

    strategy_engine.register_strategy(ExampleBuyStrategy("BuyLowBTC", symbols=["BTCUSDT"]))
    strategy_engine.register_strategy(PrintTradesStrategy("PrintTrades", symbols=["BTCUSDT","ETHUSDT"]))

    tasks = []

    if ACTIVE_EXCHANGES[ExchangeName.BINANCE]:
        tasks.append(asyncio.create_task(
            BinanceWSConnector(
                symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
                intervals=["1m","5m"],
                on_message=lambda e: asyncio.create_task(router.publish(e))
            ).connect()
        ))

    if ACTIVE_EXCHANGES[ExchangeName.HYPERLIQUID]:
        tasks.append(asyncio.create_task(
            HyperliquidWSConnector(
                symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
                on_message=lambda e: asyncio.create_task(router.publish(e))
            ).connect()
        ))

    if ACTIVE_EXCHANGES[ExchangeName.DYDX]:
        tasks.append(asyncio.create_task(
            MultiDEXWSConnector(
                symbols=["BTCUSDT","ETHUSDT"],
                exchanges=[ExchangeName.DYDX],
                intervals=["1m"],
                on_message=lambda e: asyncio.create_task(router.publish(e))
            ).connect()
        ))

    if ACTIVE_EXCHANGES[Exchange
