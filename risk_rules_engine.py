# core/risk/risk_rules_engine.py

class RiskRulesEngine:
    def __init__(self, max_leverage=10.0, min_liq_buffer=0.005):
        """
        max_leverage: максимален allowed leverage на позиция
        min_liq_buffer: минимална дистанция до ликвидация (например 0.5%)
        """
        self.max_leverage = max_leverage
        self.min_liq_buffer = min_liq_buffer

    def evaluate(self, shadow_account, shadow_positions, order):
        """
        Проверява дали ордерът може да се приеме.
        Връща:
            "ALLOW"   – разрешен
            "BLOCK"   – отхвърлен
            "EMERGENCY" – критично нарушение
        """
        decision = "ALLOW"

        # -----------------------
        # 1. Проверка margin
        # -----------------------
        size = order["size"]
        price = order["price"]
        leverage = order.get("leverage", 1.0)
        order_margin = (size * price) / max(leverage, 1e-8)

        if shadow_account["used_margin"] + order_margin > shadow_account["available_margin"] + shadow_account["used_margin"]:
            return "BLOCK"

        # -----------------------
        # 2. Проверка leverage
        # -----------------------
        symbol = order["symbol"]
        pos = shadow_positions.get(symbol, {"size": 0.0, "entry_price": 0.0})
        notional = abs(pos["size"] * pos["entry_price"])
        margin = max(shadow_account["used_margin"], 1e-8)
        current_leverage = notional / margin

        if current_leverage > self.max_leverage:
            return "BLOCK"

        # -----------------------
        # 3. Ликвидационна дистанция
        # -----------------------
        # за long позиции
        if pos["size"] > 0:
            liq_price = pos["entry_price"] * (1 - margin / max(abs(pos["size"] * pos["entry_price"]), 1e-8))
        # за short позиции
        elif pos["size"] < 0:
            liq_price = pos["entry_price"] * (1 + margin / max(abs(pos["size"] * pos["entry_price"]), 1e-8))
        else:
            liq_price = order["price"]

        if abs(order["price"] - liq_price) / order["price"] < self.min_liq_buffer:
            return "BLOCK"

        # Ако всичко е ОК
        return decision


# -------------------------------
# Тест / пример за работа
# -------------------------------
if __name__ == "__main__":
    from core.risk.shadow_ledger import ShadowLedger

    ledger = ShadowLedger()
    risk = RiskRulesEngine(max_leverage=5.0)

    # Симулация на приемлив ордер
    order1 = {"symbol": "BTCUSDT", "size": 0.1, "price": 25000, "direction": 1, "leverage": 2}
    acc, pos = ledger.simulate_order(order1)
    decision = risk.evaluate(acc, pos, order1)
    print("Decision order1:", decision)  # EXPECTED: ALLOW

    # Симулация на прекомерен leverage
    order2 = {"symbol": "BTCUSDT", "size": 1.0, "price": 25000, "direction": 1, "leverage": 50}
    acc2, pos2 = ledger.simulate_order(order2)
    decision2 = risk.evaluate(acc2, pos2, order2)
    print("Decision order2:", decision2)  # EXPECTED: BLOCK
