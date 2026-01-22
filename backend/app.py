import asyncio
from typing import Dict, Any, Callable, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

# ===== Core Market Data Layer =====
from backend.market_data.unified_router import UnifiedMarketDataRouter
from backend.market_data.snapshot_cache import SnapshotCache

# ===== WebSocket Gateway =====
from backend.ws_gateway.market_ws_hub import MarketWSHub, websocket_endpoint

# ===== Strategy Engine =====
from backend.strategies.strategy_engine import StrategyEngine, StrategyBase

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

# ============================================================
# Unified Event Schema (за всички борси)
# ============================================================

"""
Normalized event format:

event = {
    "exchange": "binance" | "hyperliquid" | "gmx" | "dydx" | "apex" | "kcex" | "kwenta" | "vertex",
    "symbol": "BTCUSDT",
    "type": "trade" | "orderbook" | "ohlcv",
    "ts": 1700000000.123,

    # trade
    "price": float,
    "qty": float,
    "side": "buy" | "sell",

    # orderbook
    "bids": [[price, size], ...],
    "asks": [[price, size], ...],

    # ohlcv
    "interval": "1m",
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volume": float,
}
"""

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
            type_=OrderType(signal.get("type", "market"))
        )
        await self.om.submit_order(order)


strategy_order_router: StrategyOrderRouter | None = None


# ============================================================
# Wiring: Router → Cache / WS / Strategies / Storage
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
# Lifespan Bootstrap (тук ще закачим борсите в Part 2)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global order_manager, strategy_order_router

    # Core wiring
    wire_router()

    # Start subsystems
    ws_task = asyncio.create_task(ws_hub.start())
    strat_task = asyncio.create_task(strategy_engine.start())
    rec_task = asyncio.create_task(recorder.start())

    # Order manager
    order_manager = OrderManager(
        risk_check=simple_risk_check,
        send_order_callable=mock_send_order  # после ще го вържем към реални конектори
    )
    asyncio.create_task(order_manager.start())
    strategy_order_router = StrategyOrderRouter(order_manager)

    print("[SYSTEM] Core services started")

    try:
        yield
    finally:
        print("[SYSTEM] Shutting down core services...")
        await router.stop()
        ws_task.cancel()
        strat_task.cancel()
        rec_task.cancel()
        await recorder.stop()


app.router.lifespan_context = lifespan


# ============================================================
# WebSocket API за Frontend
# ============================================================

@app.websocket("/ws/market/{client_id}")
async def market_ws(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "router_stats": router.get_stats(),
        "ws_clients": len(ws_hub.clients),
    }
  # ============================================================
# Exchange Connectors
# ============================================================

from backend.exchange_connectors.binance_ws import BinanceWSConnector
from backend.exchange_connectors.hyperliquid_ws import HyperliquidWSConnector
from backend.exchange_connectors.dydx_ws import DydxWSConnector        # ще го добавим след това
from backend.exchange_connectors.gmx_web3_connector import GMXWeb3Connector
from backend.exchange_connectors.stub_ws import StubDEXConnector


async def start_connectors():
    tasks = []

    # ---------- Binance ----------
    binance = BinanceWSConnector(
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        intervals=["1m", "5m"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    tasks.append(asyncio.create_task(binance.connect()))

    # ---------- Hyperliquid ----------
    hyperliquid = HyperliquidWSConnector(
        symbols=["BTC", "ETH", "SOL"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    tasks.append(asyncio.create_task(hyperliquid.connect()))

    # ---------- dYdX ----------
    dydx = DydxWSConnector(
        symbols=["BTC-USD", "ETH-USD"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    tasks.append(asyncio.create_task(dydx.connect()))

    # ---------- GMX (Web3) ----------
    gmx = GMXWeb3Connector(
        symbols=["BTC", "ETH"],
        on_message=lambda e: asyncio.create_task(router.publish(e))
    )
    tasks.append(asyncio.create_task(gmx.start()))

    # ---------- Stub DEXes ----------
    apex = StubDEXConnector("apex", ["BTCUSDT", "ETHUSDT"], router)
    kcex = StubDEXConnector("kcex", ["BTCUSDT", "ETHUSDT"], router)
    kwenta = StubDEXConnector("kwenta", ["BTCUSDT", "ETHUSDT"], router)
    vertex = StubDEXConnector("vertex", ["BTCUSDT", "ETHUSDT"], router)

    tasks.append(asyncio.create_task(apex.start()))
    tasks.append(asyncio.create_task(kcex.start()))
    tasks.append(asyncio.create_task(kwenta.start()))
    tasks.append(asyncio.create_task(vertex.start()))

    print("[SYSTEM] All 8 DEX connectors started")

    return tasks
import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List


class BaseExchangeConnector(ABC):
    def __init__(
        self,
        name: str,
        symbols: List[str],
        on_message: Callable[[Dict[str, Any]], None]
    ):
        self.name = name
        self.symbols = symbols
        self.on_message = on_message
        self._running = False
        self._reconnect_delay = 5

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    async def _safe_emit(self, event: Dict[str, Any]):
        event["exchange"] = self.name
        await self.on_message(event)

    async def run_forever(self):
        self._running = True
        while self._running:
            try:
                await self.connect()
            except Exception as e:
                print(f"[{self.name}] Connection error: {e}. Reconnecting in {self._reconnect_delay}s")
                await asyncio.sleep(self._reconnect_delay)

    def stop(self):
        self._running = False
  
