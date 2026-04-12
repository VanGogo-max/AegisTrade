"""
AegisTrade — State Manager
"""
from __future__ import annotations
import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional

from backend.config.config import (
    INITIAL_CAPITAL, STATE_FILE, TRADE_HISTORY_FILE, REFERRAL_FILE
)
from backend.utils.logger import get_logger

log = get_logger(__name__)
_lock = asyncio.Lock()


@dataclass
class Position:
    id: str
    symbol: str
    side: str
    qty: float
    entry_price: float
    stop_loss: float
    take_profit: float
    strategy: str
    dex: str
    opened_at: float = field(default_factory=time.time)
    pnl: float = 0.0


@dataclass
class TradeRecord:
    id: str
    symbol: str
    side: str
    qty: float
    entry_price: float
    exit_price: float
    pnl: float
    strategy: str
    dex: str
    opened_at: float
    closed_at: float = field(default_factory=time.time)
    reason: str = ""


@dataclass
class BotState:
    balance: float = INITIAL_CAPITAL
    equity: float = INITIAL_CAPITAL
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    total_pnl: float = 0.0
    positions: Dict[str, dict] = field(default_factory=dict)
    system_locked: bool = False
    trading_halted: bool = False
    current_regime: str = "neutral"
    day_start_balance: float = INITIAL_CAPITAL
    week_start_balance: float = INITIAL_CAPITAL
    last_reset: float = field(default_factory=time.time)


class StateManager:
    def __init__(self) -> None:
        self._state = BotState()
        self._trades: List[dict] = []
        self._referrals: dict = {}
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for f in [STATE_FILE, TRADE_HISTORY_FILE, REFERRAL_FILE]:
            Path(f).parent.mkdir(parents=True, exist_ok=True)

    async def load(self) -> None:
        async with _lock:
            self._state = await asyncio.to_thread(self._load_state)
            self._trades = await asyncio.to_thread(self._load_json, TRADE_HISTORY_FILE, [])
            self._referrals = await asyncio.to_thread(self._load_json, REFERRAL_FILE, {})
        log.info("State loaded. Balance=%.2f", self._state.balance)

    async def save(self) -> None:
        async with _lock:
            await asyncio.to_thread(self._write_json, STATE_FILE, asdict(self._state))
            await asyncio.to_thread(self._write_json, TRADE_HISTORY_FILE, self._trades)
            await asyncio.to_thread(self._write_json, REFERRAL_FILE, self._referrals)

    def _load_state(self) -> BotState:
        data = self._load_json(STATE_FILE, None)
        if data:
            try:
                return BotState(**{k: v for k, v in data.items()
                                   if k in BotState.__dataclass_fields__})
            except Exception as e:
                log.warning("State parse error: %s — using fresh state", e)
        return BotState()

    @staticmethod
    def _load_json(path: str, default):
        try:
            with open(path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    @staticmethod
    def _write_json(path: str, data) -> None:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @property
    def balance(self) -> float:
        return self._state.balance

    @property
    def equity(self) -> float:
        return self._state.equity

    @property
    def daily_pnl(self) -> float:
        return self._state.daily_pnl

    @property
    def weekly_pnl(self) -> float:
        return self._state.weekly_pnl

    @property
    def total_pnl(self) -> float:
        return self._state.total_pnl

    @property
    def positions(self) -> Dict[str, dict]:
        return self._state.positions

    @property
    def system_locked(self) -> bool:
        return self._state.system_locked

    @property
    def trading_halted(self) -> bool:
        return self._state.trading_halted

    @property
    def current_regime(self) -> str:
        return self._state.current_regime

    @property
    def trades(self) -> List[dict]:
        return self._trades

    @property
    def referrals(self) -> dict:
        return self._referrals

    def get_snapshot(self) -> dict:
        return {
            **asdict(self._state),
            "open_positions_count": len(self._state.positions),
        }

    async def open_position(self, pos: Position) -> None:
        async with _lock:
            self._state.positions[pos.id] = asdict(pos)
        await self.save()

    async def close_position(
        self, position_id: str, exit_price: float, reason: str = ""
    ) -> Optional[TradeRecord]:
        async with _lock:
            pos_data = self._state.positions.pop(position_id, None)
        if not pos_data:
            log.warning("close_position: unknown id %s", position_id)
            return None
        pos = Position(**pos_data)
        if pos.side == "long":
            pnl = (exit_price - pos.entry_price) * pos.qty
        else:
            pnl = (pos.entry_price - exit_price) * pos.qty
        record = TradeRecord(
            id=str(uuid.uuid4()),
            symbol=pos.symbol,
            side=pos.side,
            qty=pos.qty,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            pnl=pnl,
            strategy=pos.strategy,
            dex=pos.dex,
            opened_at=pos.opened_at,
            reason=reason,
        )
        async with _lock:
            self._state.balance += pnl
            self._state.equity = self._state.balance
            self._state.daily_pnl += pnl
            self._state.weekly_pnl += pnl
            self._state.total_pnl += pnl
            self._trades.append(asdict(record))
        await self.save()
        return record

    async def update_regime(self, regime: str) -> None:
        async with _lock:
            self._state.current_regime = regime

    async def set_halted(self, halted: bool) -> None:
        async with _lock:
            self._state.trading_halted = halted
        await self.save()

    async def set_locked(self, locked: bool) -> None:
        async with _lock:
            self._state.system_locked = locked
        await self.save()

    async def daily_reset(self) -> None:
        async with _lock:
            self._state.day_start_balance = self._state.balance
            self._state.daily_pnl = 0.0
        await self.save()

    async def weekly_reset(self) -> None:
        async with _lock:
            self._state.week_start_balance = self._state.balance
            self._state.weekly_pnl = 0.0
        await self.save()

    async def add_referral(self, code: str, data: dict) -> None:
        async with _lock:
            self._referrals[code] = data
        await self.save()

    def get_referral(self, code: str) -> Optional[dict]:
        return self._referrals.get(code)
