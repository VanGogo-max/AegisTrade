# position_manager.py

from typing import Dict, Optional
from partial_tp_engine import PartialTPEngine
from volatility_regime_detector import VolatilityRegimeDetector
from trailing_stop_manager import TrailingStopManager


class PositionManager:
    """
    Централен оркестратор на една активна позиция.
    Управлява:
    - Вход
    - Partial TP
    - SL / BE
    - Trailing
    - Волатилност профил
    """

    def __init__(self):
        self.active_position = None
        self.tp_engine: Optional[PartialTPEngine] = None
        self.vol_detector = VolatilityRegimeDetector()
        self.trailing_manager = TrailingStopManager()

    def open_position(self, signal: Dict, candles_df) -> Dict:
        """
        signal = {
            "direction": "long"/"short",
            "entry": float,
            "sl": float
        }
        """
        volatility_mode = self.vol_detector.detect(candles_df)
        self.tp_engine = PartialTPEngine(volatility_mode)

        self.tp_engine.set_trade(
            entry_price=signal["entry"],
            stop_loss=signal["sl"],
            direction=signal["direction"]
        )

        self.active_position = {
            "direction": signal["direction"],
            "entry": signal["entry"],
            "sl": signal["sl"],
            "volatility_mode": volatility_mode
        }

        return {
            "action": "OPEN",
            "entry": signal["entry"],
            "sl": signal["sl"],
            "tp_distribution": self.tp_engine.tp_structure,
            "volatility_mode": volatility_mode
        }

    def on_price_update(self, price: float, candles_df) -> Optional[Dict]:
        """
        Извиква се при всяка нова цена / свещ.
        Връща команда за ордър мениджъра.
        """
        if not self.active_position:
            return None

        event = self.tp_engine.on_price_update(price, candles_df)

        if not event:
            return None

        if event["event"] == "TP1_HIT":
            return {
                "action": "PARTIAL_CLOSE",
                "percent": event["close_pct"],
                "new_sl": event["new_sl"]
            }

        if event["event"] == "TP2_HIT":
            return {
                "action": "PARTIAL_CLOSE",
                "percent": event["close_pct"]
            }

        if event["event"] == "TRAILING_UPDATE":
            return {
                "action": "MOVE_SL",
                "new_sl": event["new_sl"]
            }

        return None

    def close_position(self, reason: str) -> Dict:
        self.active_position = None
        self.tp_engine = None
        return {
            "action": "CLOSE_ALL",
            "reason": reason
        }

    def get_status(self) -> Dict:
        if not self.active_position:
            return {"status": "NO_POSITION"}

        return {
            "status": "OPEN",
            "direction": self.active_position["direction"],
            "entry": self.active_position["entry"],
            "sl": self.tp_engine.get_current_sl(),
            "remaining_size": self.tp_engine.get_remaining_position_pct(),
            "volatility_mode": self.active_position["volatility_mode"]
        }
