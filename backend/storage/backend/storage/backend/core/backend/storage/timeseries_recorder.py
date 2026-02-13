"""
Timeseries Recorder

Append-only storage layer for normalized market data.
Designed for:
- Trades
- OHLCV candles
- Future funding / liquidation data

Storage format:
- JSONL (default, lightweight & append-safe)
- Easily extendable to Parquet / database

This module does NOT contain exchange-specific logic.
It only records already-normalized domain models.
"""

import asyncio
import json
from pathlib import Path
from typing import Union

from domain_types import Trade, OHLCV


class TimeseriesRecorder:
    """
    Append-only recorder for market data.
    Thread-safe via asyncio.Lock.
    """

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def record_trade(self, trade: Trade) -> None:
        await self._append("trades", trade.symbol, trade.__dict__)

    async def record_ohlcv(self, candle: OHLCV) -> None:
        await self._append("ohlcv", candle.symbol, candle.__dict__)

    async def _append(
        self,
        category: str,
        symbol: str,
        payload: dict
    ) -> None:
        """
        Writes one JSON line per event.
        File structure:
            data/{category}/{symbol}.jsonl
        """
        directory = self.base_path / category
        directory.mkdir(parents=True, exist_ok=True)

        file_path = directory / f"{symbol}.jsonl"

        async with self._lock:
            with file_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
