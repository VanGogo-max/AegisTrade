# backend/main.py

import os
from fastapi import FastAPI

from backend.market_data.market_router import MarketRouter
from backend.execution.execution_engine import ExecutionEngine
from backend.execution.binance_execution import BinanceExecutionAdapter
from backend.strategies.strategy_manager import StrategyManager


# ==========================================================
# APP INITIALIZATION
# ==========================================================

app = FastAPI(title="Multi-DEX Trading Engine")


# Core infrastructure
market_router = MarketRouter()
execution_engine = ExecutionEngine()
strategy_manager = StrategyManager()


# ==========================================================
# BINANCE EXECUTION SETUP
# ==========================================================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

if BINANCE_API_KEY and BINANCE_API_SECRET:
    binance_adapter = BinanceExecutionAdapter(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    )

    execution_engine.register_adapter("binance", binance_adapter)


# ==========================================================
# STARTUP / SHUTDOWN
# ==========================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize background services here:
    - WebSocket connectors
    - Strategy loading
    - Market streams
    """
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """
    Graceful shutdown:
    - Stop strategies
    - Close connectors
    """
    await strategy_manager.stop_all()


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
async def health():
    return {"status": "ok"}
