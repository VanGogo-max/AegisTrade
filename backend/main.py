from fastapi import FastAPI
from typing import Dict, Any
import asyncio

from backend.orchestrator.dex_trading_orchestrator import DexTradingOrchestrator


app = FastAPI(title="AegisTrade DEX Engine")


# Избираме първата DEX
orchestrator = DexTradingOrchestrator(exchange_name="hyperliquid")


@app.get("/")
async def root():
    return {"status": "DEX engine running"}


@app.post("/trade")
async def trade(request: Dict[str, Any]):
    """
    Example body:
    {
        "symbols": ["BTC-USD"],
        "account_state": {
            "equity": 10000,
            "open_positions": [],
            "drawdown": 0.02
        }
    }
    """

    symbols = request.get("symbols", [])
    account_state = request.get("account_state", {})

    result = await orchestrator.run_cycle(
        symbols=symbols,
        account_state=account_state
    )

    return result
