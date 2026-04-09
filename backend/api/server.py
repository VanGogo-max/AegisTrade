import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="AegisTrade API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state
bot_state = {
    "running": False,
    "dry_run": True,
    "price": 0.0,
    "signal": "HOLD",
    "regime": "-",
    "action": "hold",
    "pnl": "-",
    "position": 0.0,
    "exchange": "hyperliquid",
}


class ModeUpdate(BaseModel):
    dry_run: bool


class ExchangeUpdate(BaseModel):
    exchange: str


@app.get("/api/status")
async def get_status():
    return bot_state


@app.post("/api/mode")
async def set_mode(update: ModeUpdate):
    bot_state["dry_run"] = update.dry_run
    mode = "DRY RUN" if update.dry_run else "LIVE"
    logger.info(f"Mode changed to {mode}")
    return {"dry_run": update.dry_run, "mode": mode}


@app.post("/api/exchange")
async def set_exchange(update: ExchangeUpdate):
    valid = ["hyperliquid", "gmx", "dydx", "vertex", "apex", "kwenta"]
    if update.exchange not in valid:
        return {"error": f"Unknown exchange: {update.exchange}"}
    bot_state["exchange"] = update.exchange
    logger.info(f"Exchange changed to {update.exchange}")
    return {"exchange": update.exchange}


@app.get("/api/exchanges")
async def get_exchanges():
    return {
        "exchanges": [
            "hyperliquid",
            "gmx",
            "dydx",
            "vertex",
            "apex",
            "kwenta",
        ]
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
