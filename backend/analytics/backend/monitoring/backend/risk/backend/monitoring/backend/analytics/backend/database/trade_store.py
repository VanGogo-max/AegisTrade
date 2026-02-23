"""
backend/database/trade_store.py

Persistent storage layer for executed trades.

Goals
-----
- Async safe
- High write throughput
- Queryable for analytics
- Pluggable backend (SQLite / Postgres later)

Current implementation: SQLite (aiosqlite)
"""

from __future__ import annotations

import aiosqlite
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime


class TradeStore:
    def __init__(self, db_path: str = "data/trades.db"):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    async def connect(self):
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("PRAGMA journal_mode=WAL;")
        await self._db.execute("PRAGMA synchronous=NORMAL;")
        await self._create_tables()

    async def close(self):
        if self._db:
            await self._db.close()

    async def _create_tables(self):
        assert self._db

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                size REAL,
                fee REAL,
                pnl REAL,
                strategy TEXT,
                exchange TEXT,
                timestamp INTEGER
            )
            """
        )

        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_symbol_time ON trades(symbol, timestamp)"
        )

        await self._db.commit()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def record_trade(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        fee: float = 0.0,
        pnl: float = 0.0,
        strategy: Optional[str] = None,
        exchange: Optional[str] = None,
        timestamp: Optional[int] = None,
    ):
        assert self._db

        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp() * 1000)

        async with self._lock:
            await self._db.execute(
                """
                INSERT INTO trades (
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
                ),
            )
            await self._db.commit()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_trades(
        self,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        assert self._db

        query = "SELECT * FROM trades WHERE 1=1"
        params: List[Any] = []

        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)

        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()

        columns = [col[0] for col in cursor.description]

        return [dict(zip(columns, row)) for row in rows]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    async def get_pnl(self, strategy: Optional[str] = None) -> float:
        assert self._db

        query = "SELECT SUM(pnl) FROM trades"
        params = []

        if strategy:
            query += " WHERE strategy = ?"
            params.append(strategy)

        cursor = await self._db.execute(query, params)
        result = await cursor.fetchone()

        return float(result[0] or 0)

    async def get_volume(self, symbol: Optional[str] = None) -> float:
        assert self._db

        query = "SELECT SUM(size * price) FROM trades"
        params = []

        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)

        cursor = await self._db.execute(query, params)
        result = await cursor.fetchone()

        return float(result[0] or 0)

    async def get_trade_count(self) -> int:
        assert self._db

        cursor = await self._db.execute("SELECT COUNT(*) FROM trades")
        result = await cursor.fetchone()

        return int(result[0])

