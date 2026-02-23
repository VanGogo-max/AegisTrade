"""
Institutional Position Store

Responsibilities
----------------
• Track open positions
• Maintain position history
• Calculate realized PnL
• Provide exposure metrics
• Serve analytics queries
"""

from __future__ import annotations

import asyncio
import aiosqlite
from typing import Optional, Dict, Any, List
from datetime import datetime


class PositionStore:

    def __init__(self, db_path: str = "data/positions.db"):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    # ----------------------------------------------------
    # Connection
    # ----------------------------------------------------

    async def connect(self):
        self._db = await aiosqlite.connect(self.db_path)

        await self._db.execute("PRAGMA journal_mode=WAL;")
        await self._db.execute("PRAGMA synchronous=NORMAL;")

        await self._create_tables()

    async def close(self):
        if self._db:
            await self._db.close()

    # ----------------------------------------------------
    # Schema
    # ----------------------------------------------------

    async def _create_tables(self):
        assert self._db

        # Current positions
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                realized_pnl REAL,
                updated_at INTEGER
            )
            """
        )

        # History
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS position_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                size REAL,
                entry_price REAL,
                realized_pnl REAL,
                timestamp INTEGER
            )
            """
        )

        await self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_position_history_symbol ON position_history(symbol)"
        )

        await self._db.commit()

    # ----------------------------------------------------
    # Update from fills
    # ----------------------------------------------------

    async def process_fill(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        fee: float = 0.0,
    ):
        """
        Update position after a trade execution.
        """

        assert self._db

        async with self._lock:

            position = await self._get_position(symbol)

            if position is None:

                new_size = size if side == "buy" else -size
                entry_price = price
                realized = -fee

            else:

                current_size = position["size"]
                entry_price = position["entry_price"]
                realized = position["realized_pnl"] or 0

                trade_size = size if side == "buy" else -size
                new_size = current_size + trade_size

                # position reduction / close
                if current_size != 0 and (current_size > 0) != (new_size > 0):

                    close_size = min(abs(current_size), abs(trade_size))

                    pnl = close_size * (price - entry_price)

                    if current_size < 0:
                        pnl = -pnl

                    realized += pnl

                # weighted entry
                if new_size != 0:
                    entry_price = (
                        (entry_price * abs(current_size) + price * abs(trade_size))
                        / abs(new_size)
                    )

                realized -= fee

            timestamp = int(datetime.utcnow().timestamp() * 1000)

            await self._save_position(
                symbol,
                new_size,
                entry_price,
                realized,
                timestamp,
            )

            await self._record_history(
                symbol,
                new_size,
                entry_price,
                realized,
                timestamp,
            )

    # ----------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------

    async def _get_position(self, symbol: str):

        cursor = await self._db.execute(
            "SELECT symbol,size,entry_price,realized_pnl FROM positions WHERE symbol=?",
            (symbol,),
        )

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "symbol": row[0],
            "size": row[1],
            "entry_price": row[2],
            "realized_pnl": row[3],
        }

    async def _save_position(
        self,
        symbol: str,
        size: float,
        entry_price: float,
        realized: float,
        timestamp: int,
    ):

        await self._db.execute(
            """
            INSERT INTO positions(symbol,size,entry_price,realized_pnl,updated_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET
            size=excluded.size,
            entry_price=excluded.entry_price,
            realized_pnl=excluded.realized_pnl,
            updated_at=excluded.updated_at
            """,
            (symbol, size, entry_price, realized, timestamp),
        )

        await self._db.commit()

    async def _record_history(
        self,
        symbol: str,
        size: float,
        entry_price: float,
        realized: float,
        timestamp: int,
    ):

        await self._db.execute(
            """
            INSERT INTO position_history
            (symbol,size,entry_price,realized_pnl,timestamp)
            VALUES (?,?,?,?,?)
            """,
            (symbol, size, entry_price, realized, timestamp),
        )

        await self._db.commit()

    # ----------------------------------------------------
    # Queries
    # ----------------------------------------------------

    async def get_position(self, symbol: str):

        return await self._get_position(symbol)

    async def get_all_positions(self) -> List[Dict[str, Any]]:

        cursor = await self._db.execute(
            "SELECT symbol,size,entry_price,realized_pnl FROM positions"
        )

        rows = await cursor.fetchall()

        return [
            {
                "symbol": r[0],
                "size": r[1],
                "entry_price": r[2],
                "realized_pnl": r[3],
            }
            for r in rows
        ]

    async def get_total_exposure(self) -> float:

        cursor = await self._db.execute(
            "SELECT SUM(ABS(size * entry_price)) FROM positions"
        )

        r = await cursor.fetchone()

        return float(r[0] or 0)

    async def get_realized_pnl(self) -> float:

        cursor = await self._db.execute(
            "SELECT SUM(realized_pnl) FROM positions"
        )

        r = await cursor.fetchone()

        return float(r[0] or 0)
