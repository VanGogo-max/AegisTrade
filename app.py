import asyncio
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

# ========== Core Modules ==========
from backend.exchange_connectors.binance_ws import BinanceWSConnector
from backend.exchange_connectors.hyperliquid_ws import HyperliquidWSConnector
from backend.exchange_connectors.multi_dex_ws import MultiDEXWSConnector, ExchangeName
from backend.exchange_connectors.gmx_web3_connector import GMXWeb3Connector  # Web3 streaming stub
from backend.market_data.unified_router import UnifiedMarketDataRouter
from backend.market_data.snapshot_cache import SnapshotCache
from backend.ws_gateway.market_ws_hub import MarketWSHub, websocket_endpoint
from backend.strategies.strategy_engine import StrategyEngine, StrategyBase, PrintTradesStrategy
from backend.storage.timeseries_recorder import TimeseriesRecorder
from backend.execution.order_manager import OrderManager, Order, OrderSide, OrderType, simple_risk_check, mock_send_order

# ========== FastAPI ==========
app = FastAPI(title="Multi-DEX Trading Platform Backend")

# ========== Core Instances ==========
router = UnifiedMarketDataRouter()
snapshot_cache = SnapshotCache()
market_ws_hub = MarketWSHub(snapshot_cache)
strategy_engine = StrategyEngine()
recorder = TimeseriesRecorder(base_path="./data")
order_manager: OrderManager | None = None

# ========== Strategy → OrderManager Router ==========
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

# ========== Lifespan / Bootstrap ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    global order_manager, signal_router

    # --- SnapshotCache ingestion ---
    router.subscribe("trade", snapshot_cache.ingest)
    router.subscribe("orderbook", snapshot_cache.ingest)
    router.subscribe("ohlcv", snapshot_cache.ingest)

    # --- WS Hub ---
    async def ui_publisher(event: dict):
        await market_ws_hub.publish(event)

    router.subscribe("trade", ui_publisher)
    router.subscribe("orderbook", ui_publisher)
    router.subscribe("ohlcv", ui_publisher)
    hub_task = asyncio.create_task(market_ws_hub.start())

    # --- StrategyEngine ingestion ---
    async def strategy_publisher(event: dict):
        await strategy_engine.publish(event)

    router.subscribe("trade", strategy_publisher)
    router.subscribe("orderbook", strategy_publisher)
    router.subscribe("ohlcv", strategy_publisher)
    engine_task = asyncio.create_task(strategy_engine.start())

    # --- Timeseries Recorder ingestion ---
    async def recorder_publisher(event: dict):
        await recorder.publish(event)

    router.subscribe("trade", recorder_publisher)
    router.subscribe("orderbook", recorder_publisher)
    router.subscribe("ohlcv", recorder_publisher)
    recorder_task = asyncio.create_task(recorder.start())

    # --- OrderManager ---
    order_manager = OrderManager(risk_check=simple_risk_check, send_order_callable=mock_send_order)
    asyncio.create_task(order_manager.start())
    signal_router = StrategyOrderRouter(order_manager)

    # --- Example Strategy ---
    class ExampleBuyStrategy(StrategyBase):
        async def on_trade(self, trade_event: dict):
            if trade_event['symbol'] == "BTCUSDT" and trade_event['price'] < 20000:
                signal = {
                    "symbol": "BTCUSDT",
                    "side": "buy",
                    "qty": 0.001,
                    "price": trade_event['price'],
                    "type": "market"
                }
                await signal_router.send_signal(signal)

    strategy_engine.register_strategy(ExampleBuyStrategy("BuyLowBTC", symbols=["BTCUSDT"]))
    strategy_engine.register_strategy(PrintTradesStrategy("PrintTrades", symbols=["BTCUSDT","ETHUSDT"]))

    # --- Binance WS ---
    binance_connector = BinanceWSConnector(
        symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
        intervals=["1m","5m"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    binance_task = asyncio.create_task(binance_connector.connect())

    # --- Hyperliquid WS ---
    hyperliquid_connector = HyperliquidWSConnector(
        symbols=["BTCUSDT","ETHUSDT","SOLUSDT"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    hyperliquid_task = asyncio.create_task(hyperliquid_connector.connect())

    # --- dYdX WS (stub) ---
    dydx_connector = MultiDEXWSConnector(
        symbols=["BTCUSDT","ETHUSDT"],
        exchanges=[ExchangeName.DYDX],
        intervals=["1m"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    dydx_task = asyncio.create_task(dydx_connector.connect())

    # --- GMX Web3 connector (stub) ---
    gmx_connector = GMXWeb3Connector(
        symbols=["BTCUSDT","ETHUSDT"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    gmx_task = asyncio.create_task(gmx_connector.start())

    # --- Stub connectors за Apex, Kcex, Kwenta, Vertex ---
    stub_symbols = ["BTCUSDT","ETHUSDT"]
    stub_exchanges = ["Apex","Kcex","Kwenta","Vertex"]
    stub_connector = MultiDEXWSConnector(
        symbols=stub_symbols,
        exchanges=[ExchangeName(exch.lower()) for exch in stub_exchanges],
        intervals=["1m"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    stub_task = asyncio.create_task(stub_connector.connect())

    print("[SYSTEM] All 8 DEX connectors started")
    try:
        yield
    finally:
        print("[SYSTEM] Shutting down...")
        await binance_connector.stop()
        await hyperliquid_connector.stop()
        await dydx_connector.stop()
        await gmx_connector.stop()
        await stub_connector.stop()

        await router.stop()
        hub_task.cancel()
        engine_task.cancel()
        recorder_task.cancel()
        await recorder.stop()
        print("[SYSTEM] Graceful shutdown completed")

app.router.lifespan_context = lifespan

# ========== WebSocket API ==========
@app.websocket("/ws/market/{client_id}")
async def market_ws(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)

# ========== Health Endpoint ==========
@app.get("/health")
def health():
    return {
        "status": "ok",
        "router": router.get_stats(),
        "clients": len(market_ws_hub.clients)
    }
