import asyncio
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

# ===== Core Market Data Layer =====
from backend.market_data.unified_router import UnifiedMarketDataRouter
from backend.market_data.snapshot_cache import SnapshotCache

# ===== WebSocket Gateway =====
from backend.ws_gateway.market_ws_hub import MarketWSHub, websocket_endpoint

# ===== Strategy Engine =====
from backend.strategies.strategy_engine import StrategyEngine

# ===== Storage =====
from backend.storage.timeseries_recorder import TimeseriesRecorder

# ===== Execution Layer =====
from backend.execution.order_manager import (
    OrderManager,
    Order,
    OrderSide,
    OrderType,
    simple_risk_check,
    mock_send_order,
)

# ===== Exchange Connectors =====
from backend.exchange_connectors.binance_ws import BinanceWSConnector
from backend.exchange_connectors.hyperliquid_ws import HyperliquidWSConnector
from backend.exchange_connectors.dydx_ws import DydxWSConnector
from backend.exchange_connectors.gmx_web3_connector import GMXWeb3Connector
from backend.exchange_connectors.stub_ws import StubDEXConnector


# ============================================================
# Core Instances
# ============================================================

app = FastAPI(title="Multi-DEX Trading Platform")

router = UnifiedMarketDataRouter()
snapshot_cache = SnapshotCache()
ws_hub = MarketWSHub(snapshot_cache)
strategy_engine = StrategyEngine()
recorder = TimeseriesRecorder(base_path="./data")

order_manager: OrderManager | None = None


# ============================================================
# Strategy → Order Router
# ============================================================

class StrategyOrderRouter:
    def __init__(self, om: OrderManager):
        self.om = om

    async def send(self, signal: Dict[str, Any]):
        order = Order(
            symbol=signal["symbol"],
            side=OrderSide(signal["side"]),
            qty=signal["qty"],
            price=signal.get("price"),
            type_=OrderType(signal.get("type", "market")),
        )
        await self.om.submit_order(order)


strategy_order_router: StrategyOrderRouter | None = None


# ============================================================
# Wiring
# ============================================================

async def _fanout_to_cache(event: Dict):
    await snapshot_cache.ingest(event)


async def _fanout_to_ws(event: Dict):
    await ws_hub.publish(event)


async def _fanout_to_strategies(event: Dict):
    await strategy_engine.publish(event)


async def _fanout_to_storage(event: Dict):
    await recorder.publish(event)


def wire_router():
    for t in ("trade", "orderbook", "ohlcv"):
        router.subscribe(t, _fanout_to_cache)
        router.subscribe(t, _fanout_to_ws)
        router.subscribe(t, _fanout_to_strategies)
        router.subscribe(t, _fanout_to_storage)


# ============================================================
# Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global order_manager, strategy_order_router

    wire_router()

    ws_task = asyncio.create_task(ws_hub.start())
    strat_task = asyncio.create_task(strategy_engine.start())
    rec_task = asyncio.create_task(recorder.start())

    order_manager = OrderManager(
        risk_check=simple_risk_check,
        send_order_callable=mock_send_order,
    )
    asyncio.create_task(order_manager.start())
    strategy_order_router = StrategyOrderRouter(order_manager)

    print("[SYSTEM] Core services started")

    try:
        yield
    finally:
        print("[SYSTEM] Shutting down...")
        await router.stop()
        ws_task.cancel()
        strat_task.cancel()
        rec_task.cancel()
        await recorder.stop()


app.router.lifespan_context = lifespan


# ============================================================
# WebSocket API
# ============================================================

@app.websocket("/ws/market/{client_id}")
async def market_ws(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "router_stats": router.get_stats(),
        "ws_clients": len(ws_hub.clients),
    }


# ============================================================
# Start Exchange Connectors
# ============================================================

async def start_connectors():
    tasks = []

    binance = BinanceWSConnector(
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        intervals=["1m", "5m"],
        on_message=lambda e: asyncio.create_task(router.publish(e)),
    )
    tasks.append(asyncio.create_task(binance.connect()))

    hyperliquid = HyperliquidWSConnector(
        symbols=["BTC", "ETH", "SOL"],
        on_message=lambda e: asyncio.create_task(router.publish(e)),
    )
    tasks.append(asyncio.create_task(hyperliquid.connect()))

    dydx = DydxWSConnector(
        symbols=["BTC-USD", "ETH-USD"],
        on_message=lambda e: asyncio.create_task(router.publish(e)),
    )
    tasks.append(asyncio.create_task(dydx.connect()))

    gmx = GMXWeb3Connector(
        symbols=["BTC", "ETH"],
        on_message=lambda e: asyncio.create_task(router.publish(e)),
    )
    tasks.append(asyncio.create_task(gmx.start()))

    for name in ("apex", "kcex", "kwenta", "vertex"):
        stub = StubDEXConnector(name, ["BTCUSDT", "ETHUSDT"], router)
        tasks.append(asyncio.create_task(stub.start()))

    print("[SYSTEM] All connectors started")
    return tasks
