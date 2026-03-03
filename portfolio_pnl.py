cat << 'PY' > portfolio_pnl.py
class PortfolioPnL:
    """
    Минимален portfolio tracker.
    """

    def __init__(self):
        self.positions = {}
        self.balance = 10000

    def update_position(self, symbol, qty, price):
        self.positions[symbol] = {
            "qty": qty,
            "entry": price
        }

    def close_position(self, symbol, price):
        pos = self.positions.get(symbol)

        if not pos:
            return 0

        pnl = (price - pos["entry"]) * pos["qty"]
        self.balance += pnl

        del self.positions[symbol]
        return pnl

    def equity(self):
        return self.balance
PY
