# backend/main.py

import os
from fastapi import FastAPI

from backend.market_data.market_router import MarketRouter
from backend.execution.execution_engine import ExecutionEngine
from backend.execution.binance_execution import BinanceExecutionAdapter
from backend.strategies.strategy_manager import StrategyManager
from backend.exchange_connectors.binance_ws import BinanceWebSocketClient
from backend.config.symbols import SYMBOLS


# ==========================================================
# APP
# ==========================================================

app = FastAPI(title="AI Futures Trading Engine")


# Core components
market_router = MarketRouter()
execution_engine = ExecutionEngine()
strategy_manager = StrategyManager()

ws_client = None


# ==========================================================
# EXECUTION SETUP
# ==========================================================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

if BINANCE_API_KEY and BINANCE_API_SECRET:
    adapter = BinanceExecutionAdapter(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    )
    execution_engine.register_adapter("binance", adapter)


# ==========================================================
# STARTUP / SHUTDOWN
# ==========================================================

@app.on_event("startup")
async def startup_event():
    global ws_client

    ws_client = BinanceWebSocketClient(
        symbols=SYMBOLS,
        router=market_router,
    )

    await ws_client.start()


@app.on_event("shutdown")
async def shutdown_event():
    if ws_client:
        await ws_client.stop()

    await strategy_manager.stop_all()


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
async def health():
    return {
        "status": "running",
        "symbols_loaded": len(SYMBOLS),
    }
