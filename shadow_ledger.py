# core/risk/shadow_ledger.py

class ShadowLedger:
    def __init__(self):
        self.positions = {}  # symbol -> position dict
        self.account = {
            "equity": 100000.0,        # стартов капитал
            "used_margin": 0.0,
            "available_margin": 100000.0,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0
        }

    def simulate_order(self, order):
        """
        Симулира ордер без commit.
        order = {
            "symbol": str,
            "size": float,
            "price": float,
            "direction": int (+1 long / -1 short),
            "leverage": float
        }
        """
        symbol = order["symbol"]
        size = order["size"]
        price = order["price"]
        direction = order["direction"]
        leverage = order.get("leverage", 1.0)

        # Изчисляване на margin за ордера
        order_margin = (size * price) / max(leverage, 1e-8)

        # Симулиране на ново account state
        new_account = self.account.copy()
        new_account["used_margin"] += order_margin
        new_account["available_margin"] -= order_margin

        # Симулиране на нови позиции
        new_positions = {k: v.copy() for k, v in self.positions.items()}
        pos = new_positions.get(symbol, {"size": 0.0, "entry_price": 0.0})

        # Усредняване на entry_price при нови позиции
        total_size = pos["size"] + size * direction
        if total_size != 0:
            pos["entry_price"] = (
                (pos["entry_price"] * pos["size"] + price * size * direction) / total_size
            )
        pos["size"] = total_size

        new_positions[symbol] = pos

        return new_account, new_positions

    def commit(self, account_state, position_state):
        """
        Commit на новото state
        """
        self.account = account_state
        self.positions = position_state

    def get_snapshot(self):
        """
        Lock-free snapshot за стратегии / monitoring
        """
        return {
            "account": self.account.copy(),
            "positions": {k: v.copy() for k, v in self.positions.items()}
        }


# -------------------------------
# Тест / пример за работа
# -------------------------------
if __name__ == "__main__":
    ledger = ShadowLedger()
    order1 = {"symbol": "BTCUSDT", "size": 0.1, "price": 25000, "direction": 1, "leverage": 5}
    acc, pos = ledger.simulate_order(order1)
    print("Simulated account:", acc)
    print("Simulated positions:", pos)

    ledger.commit(acc, pos)
    snapshot = ledger.get_snapshot()
    print("Snapshot after commit:", snapshot)
