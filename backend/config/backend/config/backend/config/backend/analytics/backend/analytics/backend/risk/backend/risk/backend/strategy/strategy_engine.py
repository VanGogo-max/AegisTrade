"""
AegisTrade - Strategy Engine
"""
from __future__ import annotations
from dataclasses import dataclass
from backend.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class Signal:
    side: str
    symbol: str
    price: float
    qty: float = 0.01
    regime: str = "neutral"
    strategy: str = "turtle_rsi"
    dex: str = "hyperliquid"


class StrategyEngine:
    def __init__(self) -> None:
        self._regime = "neutral"

    def fit_regime(self, candles: list) -> None:
        if len(candles) < 20:
            return
        try:
            closes = [float(c.get("c", c[-1] if isinstance(c, list) else 0)) for c in candles[-20:]]
            avg = sum(closes) / len(closes)
            last = closes[-1]
            self._regime = "bull" if last > avg * 1.01 else "bear" if last < avg * 0.99 else "neutral"
        except Exception:
            self._regime = "neutral"

    def generate_signal(self, candles: list, symbol: str) -> Signal:
        if len(candles) < 25:
            return Signal(side="none", symbol=symbol, price=0.0)
        try:
            closes = [float(c.get("c", c[-1] if isinstance(c, list) else 0)) for c in candles]
            price = closes[-1]
            sma20 = sum(closes[-20:]) / 20
            sma5 = sum(closes[-5:]) / 5
            gains = [max(closes[i] - closes[i-1], 0) for i in range(-14, 0)]
            losses = [max(closes[i-1] - closes[i], 0) for i in range(-14, 0)]
            avg_gain = sum(gains) / 14 or 0.001
            avg_loss = sum(losses) / 14 or 0.001
            rsi = 100 - (100 / (1 + avg_gain / avg_loss))
            if sma5 > sma20 and rsi < 65 and self._regime != "bear":
                return Signal(side="buy", symbol=symbol, price=price, regime=self._regime)
            elif sma5 < sma20 and rsi > 35 and self._regime != "bull":
                return Signal(side="sell", symbol=symbol, price=price, regime=self._regime)
        except Exception as e:
            log.warning("Strategy error: %s", e)
        return Signal(side="none", symbol=symbol, price=0.0, regime=self._regime)
