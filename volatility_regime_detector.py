# volatility_regime_detector.py

import numpy as np
from typing import List, Dict


class VolatilityRegimeDetector:
    """
    Класифицира пазара в режими:
    - LOW volatility  -> 70/25/5
    - HIGH volatility -> 50/30/20
    - TREND           -> 33/33/34

    Използва:
    - ATR (Average True Range)
    - Наклон на цената (trend strength)
    """

    def __init__(
        self,
        atr_period: int = 14,
        low_vol_threshold: float = 0.8,
        high_vol_threshold: float = 1.5,
        trend_slope_threshold: float = 0.0005
    ):
        self.atr_period = atr_period
        self.low_vol_threshold = low_vol_threshold
        self.high_vol_threshold = high_vol_threshold
        self.trend_slope_threshold = trend_slope_threshold

    def _calculate_atr(self, candles: List[Dict]) -> float:
        highs = np.array([c["high"] for c in candles])
        lows = np.array([c["low"] for c in candles])
        closes = np.array([c["close"] for c in candles])

        tr = np.maximum(
            highs[1:] - lows[1:],
            np.maximum(
                abs(highs[1:] - closes[:-1]),
                abs(lows[1:] - closes[:-1])
            )
        )

        atr = np.mean(tr[-self.atr_period:])
        return atr

    def _calculate_trend_slope(self, candles: List[Dict]) -> float:
        closes = np.array([c["close"] for c in candles])
        x = np.arange(len(closes))
        slope, _ = np.polyfit(x, closes, 1)
        return slope / closes.mean()

    def detect_regime(self, candles: List[Dict]) -> Dict:
        if len(candles) < self.atr_period + 2:
            raise ValueError("Not enough candles to detect volatility regime")

        atr = self._calculate_atr(candles)
        slope = self._calculate_trend_slope(candles)

        if abs(slope) > self.trend_slope_threshold:
            regime = "TREND"
            profile = {"tp1": 0.33, "tp2": 0.33, "tp3": 0.34}

        elif atr < self.low_vol_threshold:
            regime = "LOW"
            profile = {"tp1": 0.70, "tp2": 0.25, "tp3": 0.05}

        elif atr >= self.high_vol_threshold:
            regime = "HIGH"
            profile = {"tp1": 0.50, "tp2": 0.30, "tp3": 0.20}

        else:
            regime = "MEDIUM"
            profile = {"tp1": 0.50, "tp2": 0.30, "tp3": 0.20}

        return {
            "regime": regime,
            "atr": atr,
            "trend_slope": slope,
            "tp_profile": profile
      }
      
