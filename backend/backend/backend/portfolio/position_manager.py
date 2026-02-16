from typing import Dict, Any


class PositionManager:

    def __init__(self):
        self.positions: Dict[str, Dict] = {}

        self.break_even_trigger = 0.02      # +2%
        self.trailing_trigger = 0.03        # +3%
        self.trailing_distance = 0.01       # 1%
        self.max_drawdown_close = 0.05      # -5%

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
            "size": size,
            "side": side,
            "leverage": leverage,
            "stop_loss": None,
            "take_profit": None,
            "highest_price": entry_price,
            "lowest_price": entry_price,
            "status": "open",
        }

    def set_initial_protection(
        self,
        symbol: str,
        stop_loss: float,
        take_profit: float,
    ):
        if symbol not in self.positions:
            return

        self.positions[symbol]["stop_loss"] = stop_loss
        self.positions[symbol]["take_profit"] = take_profit

    def update_market_price(
        self,
        symbol: str,
        current_price: float,
    ) -> Dict[str, Any]:

        if symbol not in self.positions:
            return {"action": None}

        position = self.positions[symbol]
        entry = position["entry_price"]
        side = position["side"]

        pnl_percent = self.calculate_pnl_percent(
            entry,
            current_price,
            side,
        )

        # Track extremes
        if current_price > position["highest_price"]:
            position["highest_price"] = current_price

        if current_price < position["lowest_price"]:
            position["lowest_price"] = current_price

        # 1️⃣ Emergency drawdown close
        if pnl_percent <= -self.max_drawdown_close:
            position["status"] = "closed"
            return {"action": "close", "reason": "max_drawdown"}

        # 2️⃣ Break-even move
        if pnl_percent >= self.break_even_trigger:
            position["stop_loss"] = entry

        # 3️⃣ Trailing stop
        if pnl_percent >= self.trailing_trigger:
            if side == "long":
                trailing_stop = position["highest_price"] * (1 - self.trailing_distance)
                position["stop_loss"] = max(position["stop_loss"], trailing_stop)
            else:
                trailing_stop = position["lowest_price"] * (1 + self.trailing_distance)
                position["stop_loss"] = min(position["stop_loss"], trailing_stop)

        # 4️⃣ Stop Loss hit
        if position["stop_loss"]:

            if side == "long" and current_price <= position["stop_loss"]:
                position["status"] = "closed"
                return {"action": "close", "reason": "stop_loss"}

            if side == "short" and current_price >= position["stop_loss"]:
                position["status"] = "closed"
                return {"action": "close", "reason": "stop_loss"}

        # 5️⃣ Take Profit hit
        if position["take_profit"]:

            if side == "long" and current_price >= position["take_profit"]:
                position["status"] = "closed"
                return {"action": "close", "reason": "take_profit"}

            if side == "short" and current_price <= position["take_profit"]:
                position["status"] = "closed"
                return {"action": "close", "reason": "take_profit"}

        return {"action": None}

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
