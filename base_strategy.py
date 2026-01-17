# core/strategies/base_strategy.py

class BaseStrategy:
    """
    Базов клас за всички стратегии.
    Всяка стратегия трябва да имплементира метода generate_orders()
    """

    def __init__(self, name, grsm):
        self.name = name
        self.grsm = grsm

    def generate_orders(self):
        """
        Трябва да се override-не от конкретна стратегия.
        Връща list от ордери:
        [
            {"symbol": str, "size": float, "price": float, "direction": int, "leverage": float},
            ...
        ]
        """
        raise NotImplementedError("generate_orders must be implemented by the strategy")

    def run(self):
        """
        Основен метод за стартиране на стратегията.
        Подаваме ордери в GRSM batch обработка.
        """
        orders = self.generate_orders()
        if orders:
            results = self.grsm.process_orders_batch(orders)
            return results
        return []
