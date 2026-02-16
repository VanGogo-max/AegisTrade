import os
from fastapi import FastAPI
from pydantic import BaseModel

from backend.trading_orchestrator import TradingOrchestrator

# DEX execution clients
from backend.execution.hyperliquid_execution import HyperliquidExecutionClient
from backend.execution.dydx_execution import DydxExecutionClient


app = FastAPI(title="DEX Trading Engine")


# ==============================
# 🔧 DEX CLIENT INITIALIZATION
# ==============================

def initialize_dex_clients():

    dex_clients = {}

    if os.getenv("HYPERLIQUID_ENABLED", "true") == "true":
        dex_clients["hyperliquid"] = HyperliquidExecutionClient()

    if os.getenv("DYDX_ENABLED", "true") == "true":
        dex_clients["dydx"] = DydxExecutionClient()

    # Future:
    # dex_clients["gmx"] = GMXExecutionClient()
    # dex_clients["vertex"] = VertexExecutionClient()

    return dex_clients


dex_clients = initialize_dex_clients()

orchestrator = TradingOrchestrator(dex_clients)


# ==============================
# 📦 API MODELS
# ==============================

class TradeRequest(BaseModel):
    symbol: str
    side: str  # "long" or "short"
    size: float
    leverage: int
    strategy_name: str
    account_balance: float


# ==============================
# 🚀 API ENDPOINT
# ==============================

@app.post("/trade")
async def execute_trade(request: TradeRequest):

    result = await orchestrator.execute_signal(
        symbol=request.symbol,
        side=request.side,
        size=request.size,
        leverage=request.leverage,
        strategy_name=request.strategy_name,
        account_balance=request.account_balance,
    )

    return result


# ==============================
# 🩺 HEALTH CHECK
# ==============================

@app.get("/health")
def health_check():
    return {"status": "running"}
