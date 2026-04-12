"""
AegisTrade — UX Effects
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from backend.utils.logger import get_logger

log = get_logger(__name__)

UX_EVENT_QUEUE: asyncio.Queue = asyncio.Queue(maxsize=256)


@dataclass
class UXEvent:
    event_type: str
    name: str
    payload: dict = field(default_factory=dict)


async def emit(event_type: str, name: str, **payload) -> None:
    ev = UXEvent(event_type=event_type, name=name, payload=payload)
    try:
        UX_EVENT_QUEUE.put_nowait(ev)
    except asyncio.QueueFull:
        log.warning("UX event queue full — dropping %s/%s", event_type, name)
    log.debug("UX event: %s/%s %s", event_type, name, payload)


async def sound_buy(symbol: str, price: float) -> None:
    await emit("sound", "buy", symbol=symbol, price=price)

async def sound_sell(symbol: str, price: float) -> None:
    await emit("sound", "sell", symbol=symbol, price=price)

async def sound_stop_loss(symbol: str, pnl: float) -> None:
    await emit("sound", "stop_loss", symbol=symbol, pnl=pnl)

async def sound_profit(symbol: str, pnl: float) -> None:
    await emit("sound", "profit", symbol=symbol, pnl=pnl)

async def anim_new_position(symbol: str) -> None:
    await emit("animation", "new_position", symbol=symbol)

async def anim_pnl_update(pnl: float) -> None:
    color = "green" if pnl >= 0 else "red"
    await emit("animation", "pnl_update", pnl=pnl, color=color)

async def anim_risk_warning(level: str) -> None:
    await emit("animation", "risk_warning", level=level)
