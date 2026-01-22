import asyncio
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

from backend.exchange_connectors.binance_ws import BinanceWSConnector
from backend.market_data.unified_router import UnifiedMarketDataRouter
from backend.ws_gateway.market_ws_hub import market_ws_hub, websocket_endpoint


app = FastAPI(title="Multi-DEX Trading Platform Backend")

router = UnifiedMarketDataRouter()
binance_connector: BinanceWSConnector | None = None


# ========== Lifecycle Management ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    global binance_connector

    # 1. Стартираме Unified Router
    router_task = asyncio.create_task(router.start())

    # 2. Свързваме Router -> WebSocket Hub
    async def ui_publisher(event: dict):
        await market_ws_hub.publish(event)

    router.subscribe("trade", ui_publisher)
    router.subscribe("orderbook", ui_publisher)
    router.subscribe("ohlcv", ui_publisher)

    # 3. Стартираме Binance WebSocket Connector
    binance_connector = BinanceWSConnector(
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        intervals=["1m", "5m"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )

    binance_task = asyncio.create_task(binance_connector.connect())

    # 4. Стартираме WS Hub dispatcher
    hub_task = asyncio.create_task(market_ws_hub.start())

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
        binance_task.cancel()

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
