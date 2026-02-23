"""
backend/database/trade_store.py
Enterprise-grade trade storage.

Features
--------
- Async safe
- Batch writes
- Deduplication
- High performance SQLite config
- Analytics ready
- Postgres migration friendly
"""

from __future__ import annotations

import asyncio
import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime


class TradeStore:

    def __init__(
        self,
        db_path: str = "data/trades.db",
        batch_size: int = 100,
        flush_interval: float = 1.0,
    ):
        self.db_path = db_path
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._db: Optional[aiosqlite.Connection] = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._writer_task: Optional[asyncio.Task] = None
        self._running = False

    # -----------------------------------------------------
    # Connection
    # -----------------------------------------------------

    async def connect(self):
        self._db = await aiosqlite.connect(self.db_path)

        await self._db.execute("PRAGMA journal_mode=WAL;")
        await self._db.execute("PRAGMA synchronous=NORMAL;")
        await self._db.execute("PRAGMA temp_store=MEMORY;")

        await self._create_tables()

        self._running = True
        self._writer_task = asyncio.create_task(self._writer_loop())

    async def close(self):
        self._running = False

        if self._writer_task:
            await self._writer_task

        if self._db:
            await self._db.close()

    # -----------------------------------------------------
    # Schema
    # -----------------------------------------------------

    async def _create_tables(self):
        assert self._db

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                size REAL NOT NULL,
                fee REAL,
                pnl REAL,
                strategy TEXT,
                exchange TEXT,
                timestamp INTEGER
            )
            """
        )

        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trades(symbol, timestamp)"
        )

        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy)"
        )

        await self._db.commit()

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    async def record_trade(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        fee: float = 0,
        pnl: float = 0,
        strategy: Optional[str] = None,
        exchange: Optional[str] = None,
        timestamp: Optional[int] = None,
    ):
        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp() * 1000)

        await self._queue.put(
            (
                trade_id,
                symbol,
                side,
                price,
                size,
                fee,
                pnl,
                strategy,
                exchange,
                timestamp,
            )
        )

    # -----------------------------------------------------
    # Writer loop (batch insert)
    # -----------------------------------------------------

    async def _writer_loop(self):
        buffer = []

        while self._running or not self._queue.empty():

            try:
                item = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.flush_interval,
                )
                buffer.append(item)

                if len(buffer) >= self.batch_size:
                    await self._flush(buffer)
                    buffer.clear()

            except asyncio.TimeoutError:
                if buffer:
                    await self._flush(buffer)
                    buffer.clear()

    async def _flush(self, trades):
        assert self._db

        await self._db.executemany(
            """
            INSERT OR IGNORE INTO trades (
                trade_id,
                symbol,
                side,
                price,
                size,
                fee,
                pnl,
                strategy,
                exchange,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trades,
        )

        await self._db.commit()

    # -----------------------------------------------------
    # Queries
    # -----------------------------------------------------

    async def get_trades(
        self,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        assert self._db

        query = "SELECT * FROM trades WHERE 1=1"
        params: List[Any] = []

        if symbol:
            query += " AND symbol=?"
            params.append(symbol)

        if strategy:
            query += " AND strategy=?"
            params.append(strategy)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()

        columns = [c[0] for c in cursor.description]

        return [dict(zip(columns, r)) for r in rows]

    # -----------------------------------------------------
    # Analytics helpers
    # -----------------------------------------------------

    async def get_total_pnl(self) -> float:
        assert self._db

        cursor = await self._db.execute(
            "SELECT SUM(pnl) FROM trades"
        )

        result = await cursor.fetchone()

        return float(result[0] or 0)

    async def get_total_volume(self) -> float:
        assert self._db

        cursor = await self._db.execute(
            "SELECT SUM(price * size) FROM trades"
        )

        result = await cursor.fetchone()

        return float(result[0] or 0)

    async def get_trade_count(self) -> int:
        assert self._db

        cursor = await self._db.execute(
            "SELECT COUNT(*) FROM trades"
        )

        result = await cursor.fetchone()

        return int(result[0])
