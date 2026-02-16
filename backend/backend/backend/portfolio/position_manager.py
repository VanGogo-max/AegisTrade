from typing import Dict, Any


class PositionManager:

    def __init__(self):

        self.positions: Dict[str, Dict] = {}

        # --- Risk Parameters ---
        self.break_even_trigger = 0.02          # +2%
        self.partial_tp_trigger = 0.03          # +3%
        self.partial_tp_ratio = 0.5             # close 50%
        self.max_drawdown_close = 0.05          # -5%

        # Volatility multiplier (ATR based)
        self.volatility_multiplier = 1.5

    # ==============================
    # POSITION REGISTRATION
    # ==============================

    def register_position(
        self,
        symbol: str,
        entry_price: float,
        size: float,
        side: str,
        leverage: int,
    ):

        self.positions[symbol] = {
            "entry_price": entry_price,
            "original_size": size,
            "remaining_size": size,
            "side": side,
            "leverage": leverage,
            "stop_loss": None,
            "take_profit": None,
            "highest_price": entry_price,
            "lowest_price": entry_price,
            "partial_tp_done": False,
            "status": "open",
        }

    # ==============================
    # MARKET UPDATE
    # ==============================

    def update_market_price(
        self,
        symbol: str,
        current_price: float,
        atr_value: float,   # volatility input
    ) -> Dict[str, Any]:

        if symbol not in self.positions:
            return {"action": None}

        position = self.positions[symbol]
        entry = position["entry_price"]
        side = position["side"]

        pnl_percent = self.calculate_pnl_percent(entry, current_price, side)

        # Track extremes
        if current_price > position["highest_price"]:
            position["highest_price"] = current_price

        if current_price < position["lowest_price"]:
            position["lowest_price"] = current_price

        # ==============================
        # 1️⃣ Emergency Drawdown Close
        # ==============================

        if pnl_percent <= -self.max_drawdown_close:
            position["status"] = "closed"
            return {"action": "close_full", "reason": "max_drawdown"}

        # ==============================
        # 2️⃣ Break Even Move
        # ==============================

        if pnl_percent >= self.break_even_trigger:
            position["stop_loss"] = entry

        # ==============================
        # 3️⃣ Partial Take Profit
        # ==============================

        if (
            pnl_percent >= self.partial_tp_trigger
            and not position["partial_tp_done"]
        ):
            partial_size = position["original_size"] * self.partial_tp_ratio
            position["remaining_size"] -= partial_size
            position["partial_tp_done"] = True

            return {
                "action": "close_partial",
                "size": partial_size,
                "reason": "partial_take_profit",
            }

        # ==============================
        # 4️⃣ Volatility-Adaptive Trailing Stop
        # ==============================

        dynamic_distance = atr_value * self.volatility_multiplier

        if side == "long":

            trailing_stop = position["highest_price"] - dynamic_distance

            if position["stop_loss"] is None:
                position["stop_loss"] = trailing_stop
            else:
                position["stop_loss"] = max(
                    position["stop_loss"],
                    trailing_stop,
                )

            if current_price <= position["stop_loss"]:
                position["status"] = "closed"
                return {"action": "close_full", "reason": "trailing_stop"}

        else:

            trailing_stop = position["lowest_price"] + dynamic_distance

            if position["stop_loss"] is None:
                position["stop_loss"] = trailing_stop
            else:
                position["stop_loss"] = min(
                    position["stop_loss"],
                    trailing_stop,
                )

            if current_price >= position["stop_loss"]:
                position["status"] = "closed"
                return {"action": "close_full", "reason": "trailing_stop"}

        return {"action": None}

    # ==============================
    # PNL CALCULATION
    # ==============================

    @staticmethod
    def calculate_pnl_percent(
        entry: float,
        current: float,
        side: str,
    ) -> float:

        if side == "long":
            return (current - entry) / entry
        else:
            return (entry - current) / entry
