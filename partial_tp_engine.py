# partial_tp_engine.py

from typing import Dict, List
from trailing_stop_manager import TrailingStopManager


class PartialTPEngine:
    """
    Управлява частично затваряне:
    TP1 -> BE
    TP2 -> фиксирана печалба
    TP3 -> Trailing Stop (ATR)
    """

    def __init__(self, volatility_mode: str = "medium"):
        self.volatility_mode = volatility_mode
        self.trailing_manager = TrailingStopManager()
        self.tp_structure = self._load_structure(volatility_mode)
        self.tp_hits = {"tp1": False, "tp2": False, "tp3": False}
        self.entry_price = None
        self.direction = None
        self.sl = None

    def _load_structure(self, mode: str):
        if mode == "low":
            return {"tp1": 0.70, "tp2": 0.25, "tp3": 0.05}
        elif mode == "high":
            return {"tp1": 0.50, "tp2": 0.30, "tp3": 0.20}
        elif mode == "trend":
            return {"tp1": 0.33, "tp2": 0.33, "tp3": 0.34}
        else:
            return {"tp1": 0.50, "tp2": 0.30, "tp3": 0.20}

    def set_trade(self, entry_price: float, stop_loss: float, direction: str):
        self.entry_price = entry_price
        self.sl = stop_loss
        self.direction = direction
        self.tp_hits = {"tp1": False, "tp2": False, "tp3": False}
        self.trailing_manager.reset()

    def get_tp_prices(self, risk_reward: float = 1.0):
        if self.direction == "long":
            return {
                "tp1": self.entry_price * (1 + 0.003),
                "tp2": self.entry_price * (1 + 0.006),
                "tp3": self.entry_price * (1 + 0.012)
            }
        else:
            return {
                "tp1": self.entry_price * (1 - 0.003),
                "tp2": self.entry_price * (1 - 0.006),
                "tp3": self.entry_price * (1 - 0.012)
            }

    def on_price_update(self, price: float, candles_df):
        tp_prices = self.get_tp_prices()

        # TP1
        if not self.tp_hits["tp1"]:
            if (self.direction == "long" and price >= tp_prices["tp1"]) or \
               (self.direction == "short" and price <= tp_prices["tp1"]):
                self.tp_hits["tp1"] = True
                self.sl = self.entry_price  # BE
                self.trailing_manager.activate(self.entry_price, self.direction)
                return {"event": "TP1_HIT", "new_sl": self.sl, "close_pct": self.tp_structure["tp1"]}

        # TP2
        if self.tp_hits["tp1"] and not self.tp_hits["tp2"]:
            if (self.direction == "long" and price >= tp_prices["tp2"]) or \
               (self.direction == "short" and price <= tp_prices["tp2"]):
                self.tp_hits["tp2"] = True
                return {"event": "TP2_HIT", "close_pct": self.tp_structure["tp2"]}

        # TP3 (Trailing)
        if self.tp_hits["tp1"]:
            new_sl = self.trailing_manager.update(candles_df, self.direction)
            if new_sl:
                self.sl = new_sl
                return {"event": "TRAILING_UPDATE", "new_sl": new_sl}

        return None

    def get_current_sl(self):
        return self.sl

    def get_remaining_position_pct(self):
        closed = 0
        if self.tp_hits["tp1"]:
            closed += self.tp_structure["tp1"]
        if self.tp_hits["tp2"]:
            closed += self.tp_structure["tp2"]
        return max(0, 1 - closed)
