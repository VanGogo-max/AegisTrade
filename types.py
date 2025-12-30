"""
types.py

Core domain types for the trading platform.
This file contains ONLY data definitions (no business logic).
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class MarketType(Enum):
    SPOT = "spot"
    FUTURES = "futures"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"


@dataclass(frozen=True)
class TradingPair:
    base: str
    quote: str

    def symbol(self) -> str:
        return f"{self.base}/{self.quote}"


@dataclass
class Position:
    position_id: str
    market_type: MarketType
    trading_pair: TradingPair
    side: PositionSide
    size: float
    entry_price: float
    leverage: Optional[float]
    status: PositionStatus
