# backend/market_data/normalizer.py

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import List, Tuple, Literal, Dict, Any


# ============================================================
# ENUMS
# ============================================================

class MarketEventType(str, Enum):
    TRADE = "trade"
    ORDERBOOK = "orderbook"
    OHLCV = "ohlcv"


# ============================================================
# NORMALIZED MODELS
# ============================================================

@dataclass(frozen=True)
class NormalizedTrade:
    exchange: str
    symbol: str
    price: Decimal
    quantity: Decimal
    side: Literal["buy", "sell"]
    timestamp: int  # milliseconds
    event_type: MarketEventType = MarketEventType.TRADE


@dataclass(frozen=True)
class NormalizedOrderBook:
    exchange: str
    symbol: str
    bids: List[Tuple[Decimal, Decimal]]  # [(price, qty)]
    asks: List[Tuple[Decimal, Decimal]]
    timestamp: int
    event_type: MarketEventType = MarketEventType.ORDERBOOK


@dataclass(frozen=True)
class NormalizedOHLCV:
    exchange: str
    symbol: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    start_time: int
    close_time: int
    event_type: MarketEventType = MarketEventType.OHLCV


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================

def normalize_symbol_binance(raw_symbol: str) -> str:
    """
    Converts:
        BTCUSDT -> BTC/USDT
        ETHUSDC -> ETH/USDC
    """
    raw_symbol = raw_symbol.upper()

    # common quote assets (extendable)
    quotes = ["USDT", "USDC", "BUSD", "BTC", "ETH"]

    for quote in quotes:
        if raw_symbol.endswith(quote):
            base = raw_symbol[:-len(quote)]
            return f"{base}/{quote}"

    # fallback (no split)
    return raw_symbol


# ============================================================
# BINANCE ADAPTERS
# ============================================================

def normalize_binance_trade(data: Dict[str, Any]) -> NormalizedTrade:
    """
    Binance trade stream example:
    {
        "e": "trade",
        "E": 123456789,
        "s": "BTCUSDT",
        "t": 12345,
        "p": "50000.00",
        "q": "0.001",
        "T": 123456785,
        "m": true
    }
    """

    symbol = normalize_symbol_binance(data["s"])

    side = "sell" if data["m"] else "buy"

    return NormalizedTrade(
        exchange="binance",
        symbol=symbol,
        price=Decimal(data["p"]),
        quantity=Decimal(data["q"]),
        side=side,
        timestamp=int(data["T"]),
    )


def normalize_binance_orderbook(
    symbol: str,
    bids: List[List[str]],
    asks: List[List[str]],
    timestamp: int,
) -> NormalizedOrderBook:
    """
    bids / asks example:
    [
        ["50000.00", "0.5"],
        ["49999.00", "1.2"]
    ]
    """

    norm_symbol = normalize_symbol_binance(symbol)

    normalized_bids = [
        (Decimal(price), Decimal(qty)) for price, qty in bids
    ]

    normalized_asks = [
        (Decimal(price), Decimal(qty)) for price, qty in asks
    ]

    return NormalizedOrderBook(
        exchange="binance",
        symbol=norm_symbol,
        bids=normalized_bids,
        asks=normalized_asks,
        timestamp=int(timestamp),
    )


def normalize_binance_ohlcv(data: Dict[str, Any]) -> NormalizedOHLCV:
    """
    Binance kline example:
    {
        "e": "kline",
        "E": 123456789,
        "s": "BTCUSDT",
        "k": {
            "t": 123400000,
            "T": 123460000,
            "o": "50000.00",
            "h": "50500.00",
            "l": "49500.00",
            "c": "50200.00",
            "v": "100.5",
            "x": false
        }
    }
    """

    k = data["k"]
    symbol = normalize_symbol_binance(data["s"])

    return NormalizedOHLCV(
        exchange="binance",
        symbol=symbol,
        open=Decimal(k["o"]),
        high=Decimal(k["h"]),
        low=Decimal(k["l"]),
        close=Decimal(k["c"]),
        volume=Decimal(k["v"]),
        start_time=int(k["t"]),
        close_time=int(k["T"]),
    )
