from enum import Enum
from typing import TypedDict, Dict, Any


class MarketType(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"


class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradingPair(str):
    pass


# --- Тип за ордер / trade ---
class TradeData(TypedDict):
    pair: str
    expected_price: float
    expected_size: float
    current_price: float
    pool_address: str
    to: str
    data: bytes
    value: int


# --- Тип за резултат от MEV / sandwich проверка ---
class MEVRisk(TypedDict):
    block_trade: bool
    risk_score: float
    details: Dict[str, Any]


# --- Тип за резултат от mempool проверка ---
class MempoolRisk(TypedDict):
    frontrun_detected: bool
    emergency_boost: bool
    pending_txs_count: int


# --- Тип за резултат от liquidity / OI / funding проверка ---
class LiquidityRisk(TypedDict):
    overall_risk: bool
    liquidity: float
    open_interest: float
    funding_rate: float
    details: Dict[str, Any]


# --- Тип за резултат от gas optimizer ---
class GasFees(TypedDict):
    maxFeePerGas: int
    maxPriorityFeePerGas: int
