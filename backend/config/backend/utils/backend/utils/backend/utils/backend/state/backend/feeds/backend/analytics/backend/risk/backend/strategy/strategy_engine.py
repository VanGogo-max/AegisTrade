"""
AegisTrade — Strategy Engine
HMM Regime Detection + Hybrid Strategy (Turtle + First Candle)
"""
from __future__ import annotations
import math
import uuid
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from backend.config.config import (
    TURTLE_LOOKBACK, ATR_PERIOD, ATR_STOP_MULTIPLIER,
    OPENING_RANGE_TP_MULTIPLIER, HMM_MIN_BAR_STABILITY, HMM_N_STATES,
)
from backend.feeds.price_feed import Candle
from backend.utils.logger import get_logger

log = get_logger(__name__)

REGIME_LABELS = ["crash", "bear", "neutral", "bull", "euphoria"]


@dataclass
class Signal:
    side: str
    strategy: str
    symbol: str
    price: float
    stop_loss: float
    take_profit: float
    regime: str
    confidence: float = 1.0
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


def _atr(candles: List[Candle], period: int) -> float:
    if len(candles) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(candles)):
        c = candles[i]
        prev_close = candles[i - 1].close
        tr = max(
            c.high - c.low,
            abs(c.high - prev_close),
            abs(c.low - prev_close)
        )
        trs.append(tr)
    return sum(trs[-period:]) / period


def _highest_high(candles: List[Candle], n: int) -> float:
    return max(c.high for c in candles[-n:])


def _lowest_low(candles: List[Candle], n: int) -> float:
    return min(c.low for c in candles[-n:])


def _log_returns(candles: List[Candle]) -> np.ndarray:
    closes = np.array([c.close for c in candles])
    if len(closes) < 2:
        return np.array([])
    return np.diff(np.log(closes))


class RegimeDetector:
    def __init__(self) -> None:
        self._model = None
        self._prev_state: Optional[int] = None
        self._state_count: int = 0
        self._try_init_hmm()

    def _try_init_hmm(self) -> None:
        try:
            from hmmlearn import hmm
            self._model = hmm.GaussianHMM(
                n_components=HMM_N_STATES,
                covariance_type="diag",
                n_iter=100,
                random_state=42,
            )
            log.info("HMM regime detector initialised")
        except ImportError:
            log.warning("hmmlearn not installed — using fallback")

    def fit(self, candles: List[Candle]) -> None:
        if self._model is None or len(candles) < 30:
            return
        rets = _log_returns(candles).reshape(-1, 1)
        try:
            self._model.fit(rets)
            log.info("HMM fitted on %d bars", len(rets))
        except Exception as e:
            log.warning("HMM fit failed: %s", e)

    def predict(self, candles: List[Candle]) -> str:
        if self._model is None or len(candles) < 5:
            return self._volatility_fallback(candles)
        rets = _log_returns(candles[-30:]).reshape(-1, 1)
        try:
            states = self._model.predict(rets)
            raw_state = int(states[-1])
            if raw_state == self._prev_state:
                self._state_count += 1
            else:
                self._state_count = 1
                self._prev_state = raw_state
            if self._state_count < HMM_MIN_BAR_STABILITY:
                return REGIME_LABELS[self._prev_state] if self._prev_state is not None else "neutral"
            idx = min(raw_state, len(REGIME_LABELS) - 1)
            return REGIME_LABELS[idx]
        except Exception as e:
            log.debug("HMM predict error: %s", e)
            return self._volatility_fallback(candles)

    @staticmethod
    def _volatility_fallback(candles: List[Candle]) -> str:
        if len(candles) < 5:
            return "neutral"
        rets = _log_returns(candles[-20:]) if len(candles) >= 20 else _log_returns(candles)
        if len(rets) == 0:
            return "neutral"
        mean_ret = float(np.mean(rets))
        vol = float(np.std(rets))
        if mean_ret < -0.005 and vol > 0.03:
            return "crash"
        elif mean_ret < -0.002:
            return "bear"
        elif mean_ret > 0.005 and vol > 0.03:
            return "euphoria"
        elif mean_ret > 0.002:
            return "bull"
        return "neutral"


class TurtleStrategy:
    def generate(self, candles: List[Candle], symbol: str) -> Signal:
        if len(candles) < TURTLE_LOOKBACK + ATR_PERIOD + 2:
            return Signal("none", "turtle", symbol, 0, 0, 0, "neutral")
        current = candles[-1]
        price = current.close
        atr = _atr(candles, ATR_PERIOD)
        hh = _highest_high(candles[:-1], TURTLE_LOOKBACK)
        ll = _lowest_low(candles[:-1], TURTLE_LOOKBACK)
        stop_distance = ATR_STOP_MULTIPLIER * atr
        if current.high > hh:
            stop = price - stop_distance
            tp = price + stop_distance * 2
            return Signal("long", "turtle", symbol, price, stop, tp, "bull")
        if current.low < ll:
            stop = price + stop_distance
            tp = price - stop_distance * 2
            return Signal("short", "turtle", symbol, price, stop, tp, "bear")
        return Signal("none", "turtle", symbol, price, 0, 0, "neutral")


class FirstCandleStrategy:
    def generate(self, candles: List[Candle], symbol: str) -> Signal:
        if len(candles) < 5:
            return Signal("none", "first_candle", symbol, 0, 0, 0, "neutral")
        range_high = max(candles[0].high, candles[1].high)
        range_low = min(candles[0].low, candles[1].low)
        range_size = range_high - range_low
        if range_size == 0:
            return Signal("none", "first_candle", symbol, 0, 0, 0, "neutral")
        current = candles[-1]
        price = current.close
        tp_distance = range_size * OPENING_RANGE_TP_MULTIPLIER
        if current.high > range_high and current.close > range_high:
            return Signal("long", "first_candle", symbol, price, range_low, price + tp_distance, "neutral")
        if current.low < range_low and current.close < range_low:
            return Signal("short", "first_candle", symbol, price, range_high, price - tp_distance, "neutral")
        return Signal("none", "first_candle", symbol, price, 0, 0, "neutral")


class StrategyEngine:
    def __init__(self) -> None:
        self.regime_detector = RegimeDetector()
        self.turtle = TurtleStrategy()
        self.first_candle = FirstCandleStrategy()

    def fit_regime(self, candles: List[Candle]) -> None:
        self.regime_detector.fit(candles)

    def generate_signal(self, candles: List[Candle], symbol: str) -> Signal:
        if not candles:
            return Signal("none", "none", symbol, 0, 0, 0, "neutral")
        regime = self.regime_detector.predict(candles)
        log.info("Regime: %s for %s", regime, symbol)
        if regime in ("bull", "euphoria"):
            sig = self.turtle.generate(candles, symbol)
            sig.regime = regime
            return sig
        if regime == "neutral":
            sig = self.first_candle.generate(candles, symbol)
            sig.regime = regime
            return sig
        if regime in ("bear", "crash"):
            sig = self.turtle.generate(candles, symbol)
            sig.regime = regime
            if sig.side == "long":
                sig.side = "none"
                sig.strategy = "none"
            return sig
        return Signal("none", "none", symbol, candles[-1].close, 0, 0, regime)
