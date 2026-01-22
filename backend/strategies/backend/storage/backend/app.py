import asyncio
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

# Core modules
from backend.exchange_connectors.binance_ws import BinanceWSConnector
from backend.market_data.unified_router import UnifiedMarketDataRouter
from backend.market_data.snapshot_cache import SnapshotCache
from backend.ws_gateway.market_ws_hub import MarketWSHub, websocket_endpoint
from backend.strategies.strategy_engine import StrategyEngine, StrategyBase, PrintTradesStrategy
from backend.storage.timeseries_recorder import TimeseriesRecorder

app = FastAPI(title="Multi-DEX Trading Platform Backend")

# ========== Core Components ==========
router = UnifiedMarketDataRouter()
snapshot_cache = SnapshotCache()
market_ws_hub = MarketWSHub(snapshot_cache)
strategy_engine = StrategyEngine()
recorder = TimeseriesRecorder(base_path="./data")
binance_connector: BinanceWSConnector | None = None

# ========== Lifecycle Management ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    global binance_connector

    # --- Start Unified Router ---
    router_task = asyncio.create_task(router.start())

    # --- Connect Router -> SnapshotCache ---
    router.subscribe("trade", snapshot_cache.ingest)
    router.subscribe("orderbook", snapshot_cache.ingest)
    router.subscribe("ohlcv", snapshot_cache.ingest)

    # --- Connect Router -> WS Hub ---
    async def ui_publisher(event: dict):
        await market_ws_hub.publish(event)

    router.subscribe("trade", ui_publisher)
    router.subscribe("orderbook", ui_publisher)
    router.subscribe("ohlcv", ui_publisher)

    # --- Connect Router -> StrategyEngine ---
    async def strategy_publisher(event: dict):
        await strategy_engine.publish(event)

    router.subscribe("trade", strategy_publisher)
    router.subscribe("orderbook", strategy_publisher)
    router.subscribe("ohlcv", strategy_publisher)

    # --- Connect Router -> TimeseriesRecorder ---
    async def recorder_publisher(event: dict):
        await recorder.publish(event)

    router.subscribe("trade", recorder_publisher)
    router.subscribe("orderbook", recorder_publisher)
    router.subscribe("ohlcv", recorder_publisher)

    # --- Start WS Hub Dispatcher ---
    hub_task = asyncio.create_task(market_ws_hub.start())

    # --- Start Strategy Engine Loop ---
    engine_task = asyncio.create_task(strategy_engine.start())

    # --- Start Timeseries Recorder Loop ---
    recorder_task = asyncio.create_task(recorder.start())

    # --- Start Binance Connector ---
    binance_connector = BinanceWSConnector(
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        intervals=["1m", "5m"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    binance_task = asyncio.create_task(binance_connector.connect())

    print("[SYSTEM] All core services started")
    try:
        yield
    finally:
        print("[SYSTEM] Shutting down...")

        if binance_connector:
            await binance_connector.stop()

        await router.stop()
        router_task.cancel()
        hub_task.cancel()
        engine_task.cancel()
        recorder_task.cancel()
        binance_task.cancel()

        await recorder.stop()
        print("[SYSTEM] Graceful shutdown completed")


app.router.lifespan_context = lifespan

# ========== WebSocket API ==========
@app.websocket("/ws/market/{client_id}")
async def market_ws(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)

# ========== Health & Monitoring ==========
@app.get("/health")
def health():
    return {
        "status": "ok",
        "router": router.get_stats(),
        "clients": len(market_ws_hub.clients)
    }

# ========== Example Strategy Registration ==========
# Добавяме тестова стратегия за логване на трейдове
strategy_engine.register_strategy(PrintTradesStrategy("PrintTrades", symbols=["BTCUSDT","ETHUSDT"]))
