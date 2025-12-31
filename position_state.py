# position_state.py
"""
Foundation types for position and order state management.
This file defines ONLY data structures and enums.
NO business logic is allowed here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MarketType(Enum):
    SPOT = "spot"
    FUTURES = "futures"


class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


@dataclass(frozen=True)
class PositionState:
    """
    Immutable snapshot of a trading position.
    """

    symbol: str
    market_type: MarketType
    side: PositionSide

    size: float
    entry_price: float

    leverage: Optional[float] = None
    liquidation_price: Optional[float] = None

    status: PositionStatus = PositionStatus.OPEN
