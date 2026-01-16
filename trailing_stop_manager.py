# trailing_stop_manager.py

from typing import Dict, Optional
import pandas as pd
import numpy as np


class TrailingStopManager:
    """
    Динамичен Trailing Stop:
    - Адаптивен според ATR (волатилност)
    - Работи за long и short
    - Активира се след TP1
    - Следи всяка нова свещ и мести SL само в печеливша посока
    """

    def __init__(self, atr_period: int = 14, atr_multiplier: float = 1.5):
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.active_trailing = False
        self.current_sl: Optional[float] = None

    def calculate_atr(self, candles: pd.DataFrame) -> float:
        high = candles['high']
        low = candles['low']
        close = candles['close'].shift(1)

        tr = pd.concat([
            high - low,
            (high - close).abs(),
            (low - close).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(self.atr_period).mean().iloc[-1]
        return atr

    def activate(self, entry_price: float, direction: str):
        self.active_trailing = True
        if direction == "long":
            self.current_sl = entry_price
        else:
            self.current_sl = entry_price

    def update(self, candles: pd.DataFrame, direction: str) -> Optional[float]:
        """
        Връща нов SL ако има движение, иначе None
        """
        if not self.active_trailing or len(candles) < self.atr_period + 2:
            return None

        atr = self.calculate_atr(candles)
        last_price = candles.iloc[-1]['close']
        trail_distance = atr * self.atr_multiplier

        if direction == "long":
            new_sl = last_price - trail_distance
            if new_sl > self.current_sl:
                self.current_sl = new_sl
                return self.current_sl

        elif direction == "short":
            new_sl = last_price + trail_distance
            if new_sl < self.current_sl:
                self.current_sl = new_sl
                return self.current_sl

        return None

    def get_current_sl(self) -> Optional[float]:
        return self.current_sl

    def reset(self):
        self.active_trailing = False
        self.current_sl = None
