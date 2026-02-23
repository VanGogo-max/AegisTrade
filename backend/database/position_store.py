"""
High Performance Position Engine

In-memory position tracking with durable snapshots.
Designed for low-latency trading systems.
"""

from __future__ import annotations

import asyncio
import aiosqlite
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class Position:
    symbol: str
    size: float = 0.0
    entry_price: float = 0.0
    realized_pnl: float = 0.0


class PositionStore:

    def __init__(
        self,
        db_path: str = "data/positions.db",
        snapshot_interval: float = 5.0,
    ):

        self.db_path = db_path
        self.snapshot_interval = snapshot_interval

        self._db: Optional[aiosqlite.Connection] = None
        self._positions: Dict[str, Position] = {}

        self._snapshot_task: Optional[asyncio.Task] = None
        self._running = False

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    async def start(self):

        self._db = await aiosqlite.connect(self.db_path)

        await self._create_tables()
        await self._load_snapshot()

        self._running = True
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())

    async def close(self):

        self._running = False

        if self._snapshot_task:
            await self._snapshot_task

        if self._db:
            await self._db.close()

    # --------------------------------------------------
    # Schema
    # --------------------------------------------------

    async def _create_tables(self):

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS position_snapshots(
                symbol TEXT PRIMARY KEY,
                size REAL,
                entry_price REAL,
                realized_pnl REAL,
                updated_at INTEGER
            )
            """
        )

        await self._db.commit()

    # --------------------------------------------------
    # Load snapshot
    # --------------------------------------------------

    async def _load_snapshot(self):

        cursor = await self._db.execute(
            "SELECT symbol,size,entry_price,realized_pnl FROM position_snapshots"
        )

        rows = await cursor.fetchall()

        for r in rows:
            self._positions[r[0]] = Position(
                symbol=r[0],
                size=r[1],
                entry_price=r[2],
                realized_pnl=r[3],
            )

    # --------------------------------------------------
    # Process fill
    # --------------------------------------------------

    async def process_fill(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        fee: float = 0.0,
    ):

        pos = self._positions.get(symbol)

        if pos is None:
            pos = Position(symbol=symbol)
            self._positions[symbol] = pos

        trade_size = size if side == "buy" else -size

        old_size = pos.size
        new_size = old_size + trade_size

        # close logic
        if old_size != 0 and (old_size > 0) != (new_size > 0):

            close_size = min(abs(old_size), abs(trade_size))

            pnl = close_size * (price - pos.entry_price)

            if old_size < 0:
                pnl = -pnl

            pos.realized_pnl += pnl

        # update entry
        if new_size != 0:

            pos.entry_price = (
                (pos.entry_price * abs(old_size) + price * abs(trade_size))
                / abs(new_size)
            )

        pos.realized_pnl -= fee
        pos.size = new_size

    # --------------------------------------------------
    # Snapshot loop
    # --------------------------------------------------

    async def _snapshot_loop(self):

        while self._running:

            await asyncio.sleep(self.snapshot_interval)

            await self._persist_snapshot()

    async def _persist_snapshot(self):

        timestamp = int(datetime.utcnow().timestamp() * 1000)

        rows = [
            (
                p.symbol,
                p.size,
                p.entry_price,
                p.realized_pnl,
                timestamp,
            )
            for p in self._positions.values()
        ]

        await self._db.executemany(
            """
            INSERT INTO position_snapshots
            (symbol,size,entry_price,realized_pnl,updated_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET
            size=excluded.size,
            entry_price=excluded.entry_price,
            realized_pnl=excluded.realized_pnl,
            updated_at=excluded.updated_at
            """,
            rows,
        )

        await self._db.commit()

    # --------------------------------------------------
    # Queries
    # --------------------------------------------------

    def get_position(self, symbol: str) -> Optional[Position]:

        return self._positions.get(symbol)

    def get_all_positions(self) -> List[Position]:

        return list(self._positions.values())

    def total_exposure(self) -> float:

        exposure = 0.0

        for p in self._positions.values():
            exposure += abs(p.size * p.entry_price)

        return exposure

    def total_realized_pnl(self) -> float:

        return sum(p.realized_pnl for p in self._positions.values())
