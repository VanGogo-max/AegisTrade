class BaseStrategy:
    def __init__(self, grsm):
        self.grsm = grsm  # инжектиран GRSM instance

    def generate_order(self):
        """
        TODO:
        - логика за генериране на ордер
        - return order dict с fields: symbol, size, price, direction, leverage
        """
        pass

    def submit_order(self, order):
        """
        TODO:
        - изпраща order към GRSM
        - получава статус (ACCEPTED / REJECTED / EMERGENCY)
        """
        pass
