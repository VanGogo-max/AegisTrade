# core/risk/risk_rules_engine.py

class RiskRulesEngine:
    def __init__(self, max_leverage=10.0, min_liq_buffer=0.005,
                 max_position_per_symbol=None, max_total_exposure=None):
        """
        max_leverage: максимален allowed leverage на позиция
        min_liq_buffer: минимална дистанция до ликвидация
        max_position_per_symbol: dict, напр. {"BTCUSDT": 0.5, "ETHUSDT": 10}
        max_total_exposure: максимален allowed total exposure в USD
        """
        self.max_leverage = max_leverage
        self.min_liq_buffer = min_liq_buffer
        self.max_position_per_symbol = max_position_per_symbol or {}
        self.max_total_exposure = max_total_exposure or 1e9  # много голяма стойност по default

    def evaluate(self, shadow_account, shadow_positions, order):
        """
        Връща: "ALLOW", "BLOCK" или "EMERGENCY"
        """
        decision = "ALLOW"
        symbol = order["symbol"]
        size = order["size"]
        price = order["price"]
        direction = order["direction"]
        leverage = order.get("leverage", 1.0)

        # -----------------------
        # 1. Margin check
        # -----------------------
        order_margin = (size * price) / max(leverage, 1e-8)
        if shadow_account["used_margin"] + order_margin > shadow_account["available_margin"] + shadow_account["used_margin"]:
            return "BLOCK"

        # -----------------------
        # 2. Leverage check
        # -----------------------
        pos = shadow_positions.get(symbol, {"size": 0.0, "entry_price": 0.0})
        notional = abs(pos["size"] * pos["entry_price"])
        margin = max(shadow_account["used_margin"], 1e-8)
        current_leverage = notional / margin
        if current_leverage > self.max_leverage:
            return "BLOCK"

        # -----------------------
        # 3. Liquidation buffer
        # -----------------------
        if pos["size"] > 0:
            liq_price = pos["entry_price"] * (1 - margin / max(abs(pos["size"] * pos["entry_price"]), 1e-8))
        elif pos["size"] < 0:
            liq_price = pos["entry_price"] * (1 + margin / max(abs(pos["size"] * pos["entry_price"]), 1e-8))
        else:
            liq_price = order["price"]

        if abs(order["price"] - liq_price) / order["price"] < self.min_liq_buffer:
            return "BLOCK"

        # -----------------------
        # 4. Max position per symbol
        # -----------------------
        max_pos = self.max_position_per_symbol.get(symbol, None)
        if max_pos is not None and abs(pos["size"] + size*direction) > max_pos:
            return "BLOCK"

        # -----------------------
        # 5. Total exposure check
        # -----------------------
        total_exposure = sum(abs(p["size"]*p["entry_price"]) for p in shadow_positions.values())
        total_exposure += size * price  # нов ордер
        if total_exposure > self.max_total_exposure:
            return "BLOCK"

        return decision
