class ShadowLedger:
    def __init__(self):
        self.positions = {}  # symbol -> position dict
        self.account = {
            "equity": 0.0,
            "used_margin": 0.0,
            "available_margin": 0.0,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0
        }

    def simulate_order(self, order):
        """
        TODO:
        - симулира нов ордер върху shadow state
        - изчислява margin, leverage, liquidation price
        - връща ново account и positions без commit
        """
        pass

    def commit(self, account_state, position_state):
        """
        TODO:
        - update на реалното state
        - update на equity, used_margin, positions
        """
        pass

    def get_snapshot(self):
        """
        TODO:
        - lock-free read snapshot
        - return copy на account и positions
        """
        pass
