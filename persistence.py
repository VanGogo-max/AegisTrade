"""
persistence.py

SQLite persistence layer for trading results.
"""

import sqlite3
from typing import List, Tuple

from position_manager import Position
from domain_types import PositionSide


class Persistence:
    """
    Handles durable storage of closed trading positions.
    """

    def __init__(self, db_path: str = "trading.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS closed_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    size REAL NOT NULL,
                    pnl REAL NOT NULL
                )
                """
            )
            conn.commit()

    def save_closed_position(self, position: Position, pnl: float) -> None:
        """
        Persists a closed position and its realized PnL.
        """
        if position.exit_price is None:
            raise ValueError("Cannot persist position without exit_price.")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO closed_positions
                (symbol, side, entry_price, exit_price, size, pnl)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    position.symbol,
                    position.side.value,
                    position.entry_price,
                    position.exit_price,
                    position.size,
                    pnl,
                ),
            )
            conn.commit()

    def load_all_closed_positions(self) -> List[Tuple]:
        """
        Returns all stored closed positions as raw rows.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM closed_positions")
            return cursor.fetchall()
