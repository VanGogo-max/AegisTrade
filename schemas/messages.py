# schemas/messages.py

from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime


# -------- ORDERBOOK --------

class OrderbookLevel(BaseModel):
    price: float
    size: float


class OrderbookSnapshot(BaseModel):
    symbol: str
    bids: List[OrderbookLevel]
    asks: List[OrderbookLevel]
    timestamp: datetime


# -------- TRADES --------

class Trade(BaseModel):
    trade_id: str
    symbol: str
    side: Literal["buy", "sell"]
    price: float
    size: float
    timestamp: datetime


class TradesMessage(BaseModel):
    trades: List[Trade]


# -------- POSITIONS --------

class Position(BaseModel):
    symbol: str
    side: Literal["long", "short"]
    size: float
    entry_price: float
    mark_price: float
    pnl: float
    leverage: float


class PositionsMessage(BaseModel):
    positions: List[Position]


# -------- ORDERS --------

class Order(BaseModel):
    order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    price: float
    size: float
    status: Literal["open", "filled", "canceled"]


class OrdersMessage(BaseModel):
    orders: List[Order]


# -------- BALANCES --------

class Balance(BaseModel):
    asset: str
    available: float
    locked: float


class BalancesMessage(BaseModel):
    balances: List[Balance]


# -------- OHLCV (CHART) --------

class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVMessage(BaseModel):
    symbol: str
    timeframe: str  # e.g. "1m", "5m"
    candles: List[Candle]


# -------- ROOT WS MESSAGE --------

class WSMessage(BaseModel):
    type: Literal[
        "orderbook",
        "trades",
        "positions",
        "orders",
        "balances",
        "ohlcv"
    ]
    data: dict
