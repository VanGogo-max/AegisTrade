from typing import Dict


class StrategyEngine:
    """
    Основна стратегия (MVP версия)
    Работи в dry-run режим и с реални данни
    """

    def __init__(self):
        self.last_price = None

    # ---------------- MAIN ----------------

    def generate_signal(self, price: float) -> str:
        """
        Генерира сигнал:
        - buy
        - sell
        - hold
        """

        if self.last_price is None:
            self.last_price = price
            return "hold"

        change_percent = ((price - self.last_price) / self.last_price) * 100

        self.last_price = price

        # 📉 спад → купуваме
        if change_percent <= -1:
            return "buy"

        # 📈 ръст → продаваме
        if change_percent >= 1:
            return "sell"

        return "hold"

    # ---------------- EXECUTION DECISION ----------------

    def decide(
        self,
        price: float,
        position: Dict,
        risk_decision: Dict
    ) -> Dict:
        """
        Комбинира:
        - стратегия
        - риск
        """

        signal = self.generate_signal(price)

        # 🔴 ако риск engine казва затвори
        if risk_decision.get("action") == "close":
            return {
                "action": "close",
                "reason": risk_decision.get("reason")
            }

        # 🟡 ако трябва да намалим позиция
        if risk_decision.get("action") == "reduce":
            return {
                "action": "reduce",
                "size": 0.5
            }

        # 🟢 стратегия
        if signal == "buy" and position.get("size_usd", 0) == 0:
            return {
                "action": "open_long"
            }

        if signal == "sell" and position.get("size_usd", 0) > 0:
            return {
                "action": "close"
            }

        return {
            "action": "hold"
        }
