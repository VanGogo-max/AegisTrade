from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime


class MarketType(Enum):
    SPOT = "spot"
    FUTURES = "futures"


class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class PositionState:
    position_id: str
    symbol: str
    market_type: MarketType
    side: PositionSide

    entry_price: float
    quantity: float

    status: PositionStatus

    opened_at: datetime
    closed_at: Optional[datetime] = None

    exit_price: Optional[float] = None
    realized_pnl: Optional[float] = None

    def __post_init__(self) -> None:
        if self.entry_price <= 0:
            raise ValueError("entry_price must be positive")

        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

        if self.exit_price is not None and self.exit_price <= 0:
            raise ValueError("exit_price must be positive")

        if self.status == PositionStatus.CLOSED and self.closed_at is None:
            raise ValueError("closed_at must be set for CLOSED positions")
