"""
Order Store

Tracks orders, fills, and statuses for institutional/proprietary trading.
Supports HFT-friendly in-memory operations with snapshot persistence.
"""

from __future__ import annotations

import asyncio
import aiosqlite
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    price: float
    size: float
    filled: float = 0.0
    status: str = "open"  # open, partially_filled, filled, cancelled
    created_at: float = datetime.utcnow().timestamp()
    updated_at: float = datetime.utcnow().timestamp()


class OrderStore:

    def __init__(self, db_path: str = "data/orders.db", snapshot_interval: float = 5.0):

        self.db_path = db_path
        self.snapshot_interval = snapshot_interval

        self._db: Optional[aiosqlite.Connection] = None
        self._orders: Dict[str, Order] = {}

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
            CREATE TABLE IF NOT EXISTS orders(
                order_id TEXT PRIMARY KEY,
                symbol TEXT,
                side TEXT,
                price REAL,
                size REAL,
                filled REAL,
                status TEXT,
                created_at INTEGER,
                updated_at INTEGER
            )
            """
        )
        await self._db.commit()

    # --------------------------------------------------
    # Snapshot load/save
    # --------------------------------------------------

    async def _load_snapshot(self):
        cursor = await self._db.execute(
            "SELECT order_id,symbol,side,price,size,filled,status,created_at,updated_at FROM orders"
        )
        rows = await cursor.fetchall()
        for r in rows:
            self._orders[r[0]] = Order(
                order_id=r[0],
                symbol=r[1],
                side=r[2],
                price=r[3],
                size=r[4],
                filled=r[5],
                status=r[6],
                created_at=r[7],
                updated_at=r[8],
            )

    async def _snapshot_loop(self):
        while self._running:
            await asyncio.sleep(self.snapshot_interval)
            await self._persist_snapshot()

    async def _persist_snapshot(self):
        timestamp = datetime.utcnow().timestamp()
        rows = [
            (
                o.order_id,
                o.symbol,
                o.side,
                o.price,
                o.size,
                o.filled,
                o.status,
                o.created_at,
                timestamp,
            )
            for o in self._orders.values()
        ]
        await self._db.executemany(
            """
            INSERT INTO orders(order_id,symbol,side,price,size,filled,status,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            ON CONFLICT(order_id) DO UPDATE SET
                filled=excluded.filled,
                status=excluded.status,
                updated_at=excluded.updated_at
            """,
            rows,
        )
        await self._db.commit()

    # --------------------------------------------------
    # Order operations
    # --------------------------------------------------

    def add_order(self, order: Order):
        self._orders[order.order_id] = order

    def update_order_fill(self, order_id: str, filled: float):
        order = self._orders.get(order_id)
        if not order:
            return
        order.filled += filled
        if order.filled >= order.size:
            order.status = "filled"
        elif order.filled > 0:
            order.status = "partially_filled"
        order.updated_at = datetime.utcnow().timestamp()

    def cancel_order(self, order_id: str):
        order = self._orders.get(order_id)
        if order and order.status not in ["filled", "cancelled"]:
            order.status = "cancelled"
            order.updated_at = datetime.utcnow().timestamp()

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_all_orders(self) -> List[Order]:
        return list(self._orders.values())
